"""
API endpoints per la gestione dei ricambi (Parts).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.part import Part
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.schemas.part import (
    PartCreate, PartUpdate, PartResponse,
    PartWithStats, PartInventoryItem
)

router = APIRouter()


@router.get("/", response_model=List[PartResponse])
def get_parts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    category: Optional[str] = None,
    supplier: Optional[str] = None,
    low_stock: bool = False,
    out_of_stock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera lista ricambi con filtri avanzati.
    """
    query = db.query(Part)
    
    # Filtro ricerca testuale
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Part.codice.ilike(search_filter),
                Part.nome.ilike(search_filter),
                Part.descrizione.ilike(search_filter),
                Part.marca.ilike(search_filter)
            )
        )
    
    # Filtro categoria
    if category:
        query = query.filter(Part.categoria == category)
    
    # Filtro fornitore
    if supplier:
        query = query.filter(Part.fornitore.ilike(f"%{supplier}%"))
    
    # Filtro scorte basse
    if low_stock:
        query = query.filter(Part.quantita <= Part.quantita_minima)
    
    # Filtro fuori stock
    if out_of_stock:
        query = query.filter(Part.quantita == 0)
    
    # Ordinamento per codice
    query = query.order_by(Part.codice)
    
    parts = query.offset(skip).limit(limit).all()
    return parts


@router.post("/", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def create_part(
    part_data: PartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Crea un nuovo ricambio.
    Richiede ruolo: ADMIN o GENERAL_MANAGER
    """
    # Verifica codice ricambio univoco
    existing = db.query(Part).filter(Part.codice == part_data.codice).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Codice ricambio '{part_data.codice}' già esistente"
        )
    
    # Crea ricambio
    part = Part(**part_data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    
    return part


@router.get("/inventory", response_model=List[PartInventoryItem])
def get_inventory_status(
    alert_level: Optional[str] = Query(None, regex="^(ok|low|out)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera stato inventario ricambi con livelli di alert.
    
    alert_level:
    - ok: scorte normali
    - low: scorte sotto livello riordino
    - out: esauriti
    """
    query = db.query(Part)
    
    if alert_level == "out":
        query = query.filter(Part.quantita == 0)
    elif alert_level == "low":
        query = query.filter(
            and_(
                Part.quantita > 0,
                Part.quantita <= Part.quantita_minima
            )
        )
    elif alert_level == "ok":
        query = query.filter(Part.quantita > Part.quantita_minima)
    
    parts = query.order_by(Part.quantita.asc()).all()
    
    # Costruisci risposta con alert status
    inventory_items = []
    for part in parts:
        alert_status = "ok"
        if part.quantita == 0:
            alert_status = "out"
        elif part.quantita <= part.quantita_minima:
            alert_status = "low"
        
        inventory_items.append(
            PartInventoryItem(
                **part.__dict__,
                alert_status=alert_status,
                needs_reorder=part.quantita <= part.quantita_minima
            )
        )
    
    return inventory_items


@router.get("/{part_id}", response_model=PartWithStats)
def get_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli ricambio con statistiche utilizzo.
    """
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ricambio ID {part_id} non trovato"
        )
    
    # Calcola statistiche utilizzo
    # Conta utilizzi in schede lavoro completate
    total_used = db.query(func.sum(Part.quantita)).scalar() or 0
    
    # Schede lavoro che usano questo ricambio (tramite relazione molti-a-molti)
    work_orders_count = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.parts.any(id=part_id)
    ).scalar() or 0
    
    # Valore inventario attuale
    inventory_value = part.quantita * part.prezzo_acquisto
    
    return PartWithStats(
        **part.__dict__,
        total_used=total_used,
        work_orders_count=work_orders_count,
        inventory_value=inventory_value,
        turnover_rate=0.0  # TODO: implementare calcolo turnover
    )


@router.put("/{part_id}", response_model=PartResponse)
def update_part(
    part_id: int,
    part_data: PartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Aggiorna informazioni ricambio.
    Richiede ruolo: ADMIN o GENERAL_MANAGER
    """
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ricambio ID {part_id} non trovato"
        )
    
    # Verifica univocità codice se modificato
    if part_data.codice and part_data.codice != part.codice:
        existing = db.query(Part).filter(
            and_(
                Part.codice == part_data.codice,
                Part.id != part_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Codice ricambio '{part_data.codice}' già esistente"
            )
    
    # Aggiorna campi
    update_data = part_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    db.commit()
    db.refresh(part)
    
    return part


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(
    part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """
    Elimina ricambio.
    Richiede ruolo: ADMIN
    """
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ricambio ID {part_id} non trovato"
        )
    
    # Verifica se il ricambio è usato in schede lavoro
    work_orders = db.query(WorkOrder).filter(
        WorkOrder.parts.any(id=part_id)
    ).count()
    
    if work_orders > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossibile eliminare: ricambio utilizzato in {work_orders} schede lavoro"
        )
    
    db.delete(part)
    db.commit()
    
    return None


@router.patch("/{part_id}/stock", response_model=PartResponse)
def adjust_stock(
    part_id: int,
    quantity_change: int,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Aggiusta quantità in stock (carico/scarico manuale).
    
    quantity_change: valore positivo (carico) o negativo (scarico)
    """
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ricambio ID {part_id} non trovato"
        )
    
    # Calcola nuova quantità
    new_quantity = part.quantita + quantity_change
    
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantità insufficiente. Disponibile: {part.quantita}, Richiesto: {abs(quantity_change)}"
        )
    
    # Aggiorna stock
    part.quantita = new_quantity
    
    # TODO: Registrare movimento magazzino in tabella apposita
    # movement = StockMovement(
    #     part_id=part_id,
    #     quantity=quantity_change,
    #     type="manual_adjustment",
    #     note=note,
    #     user_id=current_user.id
    # )
    # db.add(movement)
    
    db.commit()
    db.refresh(part)
    
    return part


@router.get("/categories/list", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera lista categorie ricambi univoche.
    """
    categories = db.query(Part.categoria).distinct().filter(
        Part.categoria.isnot(None)
    ).all()
    
    return [cat[0] for cat in categories if cat[0]]


@router.get("/suppliers/list", response_model=List[str])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera lista fornitori univoci.
    """
    suppliers = db.query(Part.fornitore).distinct().filter(
        Part.fornitore.isnot(None)
    ).all()
    
    return [sup[0] for sup in suppliers if sup[0]]
