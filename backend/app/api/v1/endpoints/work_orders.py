"""
Endpoint per gestione ordini di lavoro (schede lavoro)
"""
from typing import Any, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload, noload
from sqlalchemy import func, extract, or_

from app.core.deps import get_db, get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.vehicle import Vehicle
from app.models.customer import Customer
from app.schemas.work_order import (
    WorkOrderCreate, 
    WorkOrderUpdate, 
    WorkOrderResponse, 
    WorkOrderWithDetails,
    WorkOrderStats
)
from app.utils.work_order_utils import generate_numero_scheda
from app.services.work_order_state_manager import WorkOrderStateManager

router = APIRouter()


@router.get("/", dependencies=[Depends(require_permission("work_orders.view"))])
def read_work_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Cerca per numero scheda, cliente o veicolo"),
    stato: Optional[str] = Query(None, description="Filtra per stato (bozza, approvata, in lavorazione, completata, annullata)"),
    vehicle_id: Optional[int] = Query(None, description="Filtra per veicolo"),
    date_from: Optional[date] = Query(None, description="Data inizio"),
    date_to: Optional[date] = Query(None, description="Data fine"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni lista ordini di lavoro con filtri - FORMATO PAGINATO
    """
    query = db.query(WorkOrder).options(
        selectinload(WorkOrder.customer),
        selectinload(WorkOrder.vehicle),
        noload(WorkOrder.interventions)  # Non caricare interventions nella lista - causa problemi di serializzazione
    )
    
    # Filtro ricerca
    if search:
        search_filter = f"%{search}%"
        query = query.join(Customer).join(Vehicle).filter(
            or_(
                WorkOrder.numero_scheda.ilike(search_filter),
                Customer.nome.ilike(search_filter),
                Customer.cognome.ilike(search_filter),
                Customer.ragione_sociale.ilike(search_filter),
                Vehicle.targa.ilike(search_filter)
            )
        )
    
    # Filtro stato - CONVERTIRE DA STRINGA A ENUM
    if stato:
        try:
            stato_enum = WorkOrderStatus(stato.lower())
            query = query.filter(WorkOrder.stato == stato_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stato '{stato}' non valido. Valori ammessi: bozza, approvata, in lavorazione, completata, annullata"
            )
    
    # Filtro veicolo
    if vehicle_id:
        query = query.filter(WorkOrder.vehicle_id == vehicle_id)
    
    # Filtro date
    if date_from:
        query = query.filter(WorkOrder.data_appuntamento >= date_from)
    
    if date_to:
        query = query.filter(WorkOrder.data_appuntamento <= date_to)
    
    # Conta totale
    total = query.count()
    
    # Ordina per data creazione decrescente
    work_orders = query.order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit).all()
    
    # Costruisci risposta con dati customer e vehicle
    items = []
    for wo in work_orders:
        # interventions sono escluse dalla query, quindi non causeranno problemi di serializzazione
        # Usa model_construct() senza validazione per evitare errori su dati incoerenti nel DB
        wo_data = WorkOrderResponse.model_construct(**wo.__dict__).model_dump()
        
        # Aggiungi dati customer
        if wo.customer:
            wo_data['customer_nome'] = wo.customer.full_name
            wo_data['customer_email'] = wo.customer.email
            wo_data['customer_telefono'] = wo.customer.cellulare or wo.customer.telefono
        
        # Aggiungi dati vehicle
        if wo.vehicle:
            wo_data['vehicle_targa'] = wo.vehicle.targa
            wo_data['vehicle_marca'] = wo.vehicle.marca
            wo_data['vehicle_modello'] = wo.vehicle.modello
            wo_data['vehicle_anno'] = wo.vehicle.anno
            wo_data['vehicle_colore'] = wo.vehicle.colore
        
        items.append(wo_data)
    
    # Ritorna formato paginato
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "size": limit
    }


@router.get("/next-numero-scheda", response_model=dict)
def get_next_numero_scheda(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni il prossimo numero_scheda che verrà assegnato per la data odierna
    Formato: YYZZ-XXXX (es: 0226-0001)
    """
    from datetime import datetime
    today = datetime.now()
    numero_scheda = generate_numero_scheda(db, today)
    return {"numero_scheda": numero_scheda}


@router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("work_orders.create"))])
def create_work_order(
    *,
    db: Session = Depends(get_db),
    work_order_in: WorkOrderCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Crea nuovo ordine di lavoro - NUMERO SCHEDA GENERATO AUTOMATICAMENTE
    """
    print(f"🔍 DEBUG: work_order_in ricevuto = {work_order_in.model_dump()}")
    print(f"🔍 DEBUG: numero_scheda dal frontend = {work_order_in.numero_scheda}")
    
    # Verifica che il veicolo esista
    vehicle = db.query(Vehicle).filter(Vehicle.id == work_order_in.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    # Verifica che il cliente esista
    customer = db.query(Customer).filter(Customer.id == work_order_in.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    # LOG dettagliato della richiesta ricevuta
    import logging
    logging.warning(f"[WORKORDER][CREATE] Payload ricevuto: {work_order_in.model_dump()}")
    # Crea ordine di lavoro con campi CORRETTI
    work_order_data = work_order_in.model_dump()
    work_order_data['creato_da'] = current_user.id  # CORRETTO: creato_da non created_by
    
    # Se data_compilazione non è fornita, usa ora corrente per generare numero_scheda
    # ma lascia il campo None così che il database usi il server_default
    compilation_date = work_order_in.data_compilazione or datetime.now()
    
    # SEMPRE genera il numero_scheda dal backend - NON usare mai quello dal frontend
    # per evitare duplicati e garantire univocità
    work_order_data['numero_scheda'] = generate_numero_scheda(db, compilation_date)
    
    # Se stato non specificato, imposta BOZZA
    if 'stato' not in work_order_data or work_order_data['stato'] is None:
        work_order_data['stato'] = WorkOrderStatus.BOZZA
    
    work_order = WorkOrder(**work_order_data)
    
    db.add(work_order)
    db.commit()
    db.refresh(work_order, ['id', 'numero_scheda', 'creato_da', 'created_at', 'updated_at'])  # Refresh solo i campi necessari
    
    return WorkOrderResponse.model_validate(work_order)


@router.get("/stats", response_model=WorkOrderStats)
def read_work_orders_stats(
    db: Session = Depends(get_db),
    month: Optional[int] = Query(None, description="Mese (1-12)"),
    year: Optional[int] = Query(None, description="Anno"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni statistiche ordini di lavoro
    """
    # Se non specificato, usa mese e anno correnti
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    # Query base
    query = db.query(WorkOrder).filter(
        extract('month', WorkOrder.created_at) == month,
        extract('year', WorkOrder.created_at) == year
    )
    
    # Conta totali per stato
    total = query.count()
    bozza = query.filter(WorkOrder.stato == WorkOrderStatus.BOZZA).count()
    approvata = query.filter(WorkOrder.stato == WorkOrderStatus.APPROVATA).count()
    in_lavorazione = query.filter(WorkOrder.stato == WorkOrderStatus.IN_LAVORAZIONE).count()
    completata = query.filter(WorkOrder.stato == WorkOrderStatus.COMPLETATA).count()
    annullata = query.filter(WorkOrder.stato == WorkOrderStatus.ANNULLATA).count()
    
    # Calcola totale fatturato
    total_revenue = db.query(func.sum(WorkOrder.costo_finale)).filter(
        WorkOrder.stato.in_([WorkOrderStatus.COMPLETATA]),
        extract('month', WorkOrder.created_at) == month,
        extract('year', WorkOrder.created_at) == year
    ).scalar() or 0.0
    
    # Calcola valore medio ordine
    avg_order_value = float(total_revenue / completata) if completata > 0 else 0.0
    
    return {
        "total_orders": total,
        "open_orders": bozza + approvata,
        "in_progress_orders": in_lavorazione,
        "completed_orders": completata,
        "average_completion_time": None,
        "total_revenue": float(total_revenue),
        "average_order_value": avg_order_value
    }


@router.get("/{work_order_id}", response_model=WorkOrderResponse, dependencies=[Depends(require_permission("work_orders.view"))])
def read_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni ordine di lavoro specifico con dettagli completi INCLUSI interventions
    """
    work_order = db.query(WorkOrder)\
        .options(selectinload(WorkOrder.interventions))\
        .filter(WorkOrder.id == work_order_id)\
        .first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordine di lavoro non trovato"
        )
    
    return work_order


@router.put("/{work_order_id}", response_model=WorkOrderResponse, dependencies=[Depends(require_permission("work_orders.edit"))])
def update_work_order(
    *,
    db: Session = Depends(get_db),
    work_order_id: int,
    work_order_in: WorkOrderUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Aggiorna ordine di lavoro - ALLINEATO AL MODEL
    """
    work_order = db.query(WorkOrder).options(
        noload(WorkOrder.interventions)  # Non caricare interventions - causa problemi di serializzazione
    ).filter(WorkOrder.id == work_order_id).first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordine di lavoro non trovato"
        )
    
    # LOG dettagliato della richiesta ricevuta
    import logging
    logging.warning(f"[WORKORDER][UPDATE] Payload ricevuto: {work_order_in.model_dump(exclude_unset=True)}")
    
    # Aggiorna campi con model_dump
    update_data = work_order_in.model_dump(exclude_unset=True)
    
    # Gestisci la logica di pulizia per sinistro
    if 'sinistro' in update_data and not update_data['sinistro']:
        # Se sinistro viene deselezionato, pulisci i campi correlati
        work_order.ramo_sinistro_id = None
        work_order.legale = None
        work_order.autorita = None
        work_order.numero_sinistro = None
        work_order.compagnia_sinistro = None
        work_order.compagnia_debitrice_sinistro = None
        work_order.scoperto = None
        work_order.perc_franchigia = None
    
    # Applica i campi aggiornati
    for field, value in update_data.items():
        setattr(work_order, field, value)
    
    db.add(work_order)
    db.commit()
    db.refresh(work_order)
    
    return WorkOrderResponse.model_validate(work_order)


@router.patch("/{work_order_id}/status")
async def update_work_order_status(
    *,
    db: Session = Depends(get_db),
    work_order_id: int,
    new_status: WorkOrderStatus = Query(..., description="Nuovo stato"),
    reason: Optional[str] = Query(None, description="Motivo della transizione"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Aggiorna lo stato dell'ordine di lavoro con registrazione della transizione nella cronologia.
    Utilizza il WorkOrderStateManager per validare, eseguire e registrare l'audit trail.
    """
    from app.services.work_order_state_manager import WorkOrderStateManager
    
    state_manager = WorkOrderStateManager(db)
    
    try:
        result = await state_manager.transition(
            work_order_id=work_order_id,
            new_state=new_status,
            user=current_user,
            reason=reason,
            ip_address=None,
            user_agent=None
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento dello stato: {str(e)}"
        )


@router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("work_orders.delete"))])
def delete_work_order(
    *,
    db: Session = Depends(get_db),
    work_order_id: int,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Elimina ordine di lavoro:
    - Admin/GM possono eliminare sempre (se in bozza)
    - Creatore può eliminare la propria scheda se in bozza
    """
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordine di lavoro non trovato"
        )
    
    # Controlla i permessi: admin/GM oppure creatore
    is_admin_or_gm = current_user.ruolo in ['admin', 'responsabile_generale']
    is_creator = work_order.creato_da == current_user.id
    
    if not (is_admin_or_gm or is_creator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi per eliminare questa scheda. Solo il creatore o un amministratore possono eliminarla."
        )
    
    # Solo ordini in bozza possono essere eliminati
    if work_order.stato != WorkOrderStatus.BOZZA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo ordini in stato 'bozza' possono essere eliminati"
        )
    
    db.delete(work_order)
    db.commit()


# ================== STATE TRANSITION ENDPOINTS ==================

@router.get("/{work_order_id}/available-transitions")
def get_available_transitions(
    work_order_id: int,
    interventions_count: Optional[int] = None,
    has_descrizione: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni le transizioni di stato disponibili per la scheda corrente
    basate sul ruolo dell'utente corrente.
    
    Parametri opzionali per validazione con dati dalla form:
    - interventions_count: numero di interventi nella form
    - has_descrizione: se la descrizione è compilata nella form
    """
    from app.services.work_order_state_manager import WorkOrderStateManager
    
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheda non trovata"
        )
    
    # Costruisci form_overrides se forniti
    form_overrides = None
    if interventions_count is not None or has_descrizione is not None:
        form_overrides = {}
        if interventions_count is not None:
            form_overrides['interventions_count'] = interventions_count
        if has_descrizione is not None:
            form_overrides['has_descrizione'] = has_descrizione
    
    state_manager = WorkOrderStateManager(db)
    transitions = state_manager.get_available_transitions(work_order, current_user, form_overrides)
    
    return {
        "work_order_id": work_order_id,
        "current_state": work_order.stato.value,
        "available_transitions": transitions
    }


from pydantic import BaseModel

class TransitionRequest(BaseModel):
    """Schema per la richiesta di transizione di stato"""
    reason: Optional[str] = None
    interventions_count: Optional[int] = None
    has_descrizione: Optional[bool] = None

@router.post("/{work_order_id}/transition/{new_state}")
async def transition_work_order(
    work_order_id: int,
    new_state: str,
    request_body: Optional[TransitionRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Esegui una transizione di stato sulla scheda di lavoro
    
    - **work_order_id**: ID della scheda
    - **new_state**: Nuovo stato desiderato (bozza, approvata, in lavorazione, completata, annullata)
    - **reason**: Motivo della transizione (obbligatorio per alcune transizioni)
    - **interventions_count**: Numero di interventi nella form (per validazione)
    - **has_descrizione**: Se la descrizione è compilata nella form (per validazione)
    """
    from app.services.work_order_state_manager import WorkOrderStateManager
    
    # Converti lo stato da stringa a enum
    try:
        new_state_enum = WorkOrderStatus(new_state.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stato '{new_state}' non valido"
        )
    
    state_manager = WorkOrderStateManager(db)
    
    # Ottieni IP address dalla request
    # Nota: In produzione, usare request.client.host
    ip_address = None
    user_agent = None
    
    # Costruisci form_overrides se forniti
    form_overrides = None
    reason = None
    if request_body:
        reason = request_body.reason
        if request_body.interventions_count is not None or request_body.has_descrizione is not None:
            form_overrides = {}
            if request_body.interventions_count is not None:
                form_overrides['interventions_count'] = request_body.interventions_count
            if request_body.has_descrizione is not None:
                form_overrides['has_descrizione'] = request_body.has_descrizione
    
    try:
        result = await state_manager.transition(
            work_order_id=work_order_id,
            new_state=new_state_enum,
            user=current_user,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            form_overrides=form_overrides
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la transizione: {str(e)}"
        )


@router.get("/{work_order_id}/audit-trail")
def get_audit_trail(
    work_order_id: int,
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni la cronologia di tutte le transizioni di stato per la scheda
    """
    from app.services.work_order_state_manager import WorkOrderStateManager
    
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheda non trovata"
        )
    
    state_manager = WorkOrderStateManager(db)
    audit_trail = state_manager.get_audit_trail(work_order_id, limit=limit)
    
    return {
        "work_order_id": work_order_id,
        "audit_trail": audit_trail
    }
