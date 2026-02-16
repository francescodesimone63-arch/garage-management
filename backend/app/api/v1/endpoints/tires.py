"""
API endpoints per la gestione degli pneumatici (Tires).
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.tire import Tire, TirePosition, TireCondition
from app.models.vehicle import Vehicle
from app.schemas.tire import (
    TireCreate, TireUpdate, TireResponse,
    TireWithVehicle, TireRotationRequest
)

router = APIRouter()


@router.get("/", response_model=List[TireResponse])
def get_tires(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    vehicle_id: Optional[int] = None,
    position: Optional[TirePosition] = None,
    condition: Optional[TireCondition] = None,
    needs_replacement: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera lista pneumatici con filtri.
    """
    query = db.query(Tire)
    
    # Filtro veicolo
    if vehicle_id:
        query = query.filter(Tire.vehicle_id == vehicle_id)
    
    # Filtro posizione (campo 'posizione' nel modello)
    if position:
        query = query.filter(Tire.posizione == position)
    
    # Filtro condizione (campo 'condizione' nel modello)
    if condition:
        query = query.filter(Tire.condizione == condition)
    
    # Filtro necessità sostituzione
    if needs_replacement:
        query = query.filter(
            or_(
                Tire.condition.in_([TireCondition.POOR, TireCondition.WORN_OUT]),
                Tire.tread_depth < 3.0  # Limite legale 1.6mm, soglia sicurezza 3mm
            )
        )
    
    # Ordina per veicolo e posizione di deposito
    query = query.order_by(Tire.vehicle_id, Tire.posizione)
    tires = query.offset(skip).limit(limit).all()
    
    return tires


@router.post("/", response_model=TireResponse, status_code=status.HTTP_201_CREATED)
def create_tire(
    tire_data: TireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Registra un nuovo pneumatico.
    Richiede ruolo: ADMIN, GENERAL_MANAGER, WORKSHOP
    """
    # Verifica esistenza veicolo
    vehicle = db.query(Vehicle).filter(Vehicle.id == tire_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veicolo ID {tire_data.vehicle_id} non trovato"
        )
    
    # Verifica che la posizione non sia già occupata (opzionale)
    existing = db.query(Tire).filter(
        and_(
            Tire.vehicle_id == tire_data.vehicle_id,
            Tire.position == tire_data.position
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Posizione {tire_data.position} già occupata per questo veicolo"
        )
    
    # Crea pneumatico
    tire = Tire(**tire_data.model_dump())
    db.add(tire)
    db.commit()
    db.refresh(tire)
    
    return tire


@router.get("/vehicle/{vehicle_id}", response_model=List[TireWithVehicle])
def get_vehicle_tires(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tutti gli pneumatici di un veicolo con dettagli.
    """
    # Verifica esistenza veicolo
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veicolo ID {vehicle_id} non trovato"
        )
    
    # Recupera pneumatici con join al veicolo
    tires = db.query(Tire).filter(Tire.vehicle_id == vehicle_id).order_by(Tire.position).all()
    
    # Costruisci risposta con info veicolo
    result = []
    for tire in tires:
        result.append(
            TireWithVehicle(
                **tire.__dict__,
                vehicle_info={
                    "id": vehicle.id,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "license_plate": vehicle.license_plate
                }
            )
        )
    
    return result


@router.get("/{tire_id}", response_model=TireWithVehicle)
def get_tire(
    tire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli pneumatico singolo.
    """
    tire = db.query(Tire).filter(Tire.id == tire_id).first()
    if not tire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pneumatico ID {tire_id} non trovato"
        )
    
    # Recupera info veicolo
    vehicle = tire.vehicle
    
    return TireWithVehicle(
        **tire.__dict__,
        vehicle_info={
            "id": vehicle.id,
            "make": vehicle.make,
            "model": vehicle.model,
            "license_plate": vehicle.license_plate
        } if vehicle else None
    )


@router.put("/{tire_id}", response_model=TireResponse)
def update_tire(
    tire_id: int,
    tire_data: TireUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Aggiorna informazioni pneumatico.
    Richiede ruolo: ADMIN, GENERAL_MANAGER, WORKSHOP
    """
    tire = db.query(Tire).filter(Tire.id == tire_id).first()
    if not tire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pneumatico ID {tire_id} non trovato"
        )
    
    # Verifica cambio posizione non in conflitto
    if tire_data.position and tire_data.position != tire.position:
        existing = db.query(Tire).filter(
            and_(
                Tire.vehicle_id == tire.vehicle_id,
                Tire.position == tire_data.position,
                Tire.id != tire_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Posizione {tire_data.position} già occupata"
            )
    
    # Aggiorna campi
    update_data = tire_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tire, field, value)
    
    db.commit()
    db.refresh(tire)
    
    return tire


@router.delete("/{tire_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tire(
    tire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Elimina pneumatico.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    tire = db.query(Tire).filter(Tire.id == tire_id).first()
    if not tire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pneumatico ID {tire_id} non trovato"
        )
    
    db.delete(tire)
    db.commit()
    
    return None


@router.post("/rotation", response_model=dict)
def rotate_tires(
    rotation_data: TireRotationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Esegue rotazione pneumatici secondo pattern specificato.
    
    Patterns comuni:
    - FORWARD_CROSS: Anteriori -> Posteriori opposti, Posteriori -> Anteriori stesso lato
    - REARWARD_CROSS: Posteriori -> Anteriori opposti, Anteriori -> Posteriori stesso lato
    - X_PATTERN: Incrocio completo (FL->RR, FR->RL, RL->FR, RR->FL)
    - STRAIGHT: Anteriori -> Posteriori stesso lato
    """
    vehicle_id = rotation_data.vehicle_id
    
    # Recupera tutti i pneumatici del veicolo
    tires = db.query(Tire).filter(Tire.vehicle_id == vehicle_id).all()
    
    if len(tires) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Veicolo deve avere 4 pneumatici registrati. Trovati: {len(tires)}"
        )
    
    # Crea mappa posizioni attuali
    tire_map = {tire.position: tire for tire in tires}
    
    # Pattern di rotazione
    rotation_patterns = {
        "FORWARD_CROSS": {
            TirePosition.FRONT_LEFT: TirePosition.REAR_RIGHT,
            TirePosition.FRONT_RIGHT: TirePosition.REAR_LEFT,
            TirePosition.REAR_LEFT: TirePosition.FRONT_LEFT,
            TirePosition.REAR_RIGHT: TirePosition.FRONT_RIGHT
        },
        "REARWARD_CROSS": {
            TirePosition.FRONT_LEFT: TirePosition.REAR_LEFT,
            TirePosition.FRONT_RIGHT: TirePosition.REAR_RIGHT,
            TirePosition.REAR_LEFT: TirePosition.FRONT_RIGHT,
            TirePosition.REAR_RIGHT: TirePosition.FRONT_LEFT
        },
        "X_PATTERN": {
            TirePosition.FRONT_LEFT: TirePosition.REAR_RIGHT,
            TirePosition.FRONT_RIGHT: TirePosition.REAR_LEFT,
            TirePosition.REAR_LEFT: TirePosition.FRONT_RIGHT,
            TirePosition.REAR_RIGHT: TirePosition.FRONT_LEFT
        },
        "STRAIGHT": {
            TirePosition.FRONT_LEFT: TirePosition.REAR_LEFT,
            TirePosition.FRONT_RIGHT: TirePosition.REAR_RIGHT,
            TirePosition.REAR_LEFT: TirePosition.FRONT_LEFT,
            TirePosition.REAR_RIGHT: TirePosition.FRONT_RIGHT
        }
    }
    
    pattern = rotation_patterns.get(rotation_data.pattern)
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pattern '{rotation_data.pattern}' non valido"
        )
    
    # Esegui rotazione
    # Prima salva le posizioni originali
    original_positions = {tire.id: tire.position for tire in tires}
    
    # Aggiorna posizioni secondo pattern
    for old_pos, new_pos in pattern.items():
        if old_pos in tire_map:
            tire_map[old_pos].position = new_pos
            tire_map[old_pos].last_rotation_date = datetime.utcnow()
            tire_map[old_pos].last_rotation_km = rotation_data.current_km
    
    db.commit()
    
    # Prepara risposta
    return {
        "success": True,
        "message": f"Rotazione pneumatici completata con pattern {rotation_data.pattern}",
        "vehicle_id": vehicle_id,
        "pattern": rotation_data.pattern,
        "current_km": rotation_data.current_km,
        "rotations": [
            {
                "tire_id": tire_id,
                "from": original_positions[tire_id].value,
                "to": tire_map[original_positions[tire_id]].position.value
            }
            for tire_id in original_positions.keys()
        ]
    }


@router.get("/alerts/replacement-needed", response_model=List[TireWithVehicle])
def get_replacement_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera pneumatici che necessitano sostituzione.
    
    Criteri:
    - Profondità battistrada < 3mm
    - Condizione POOR o WORN_OUT
    - Età > 6 anni
    """
    # Data limite (6 anni fa)
    six_years_ago = datetime.utcnow() - timedelta(days=365*6)
    
    query = db.query(Tire).filter(
        or_(
            Tire.tread_depth < 3.0,
            Tire.condition.in_([TireCondition.POOR, TireCondition.WORN_OUT]),
            Tire.manufacture_date < six_years_ago
        )
    )
    
    tires = query.all()
    
    # Costruisci risposta con info veicolo
    result = []
    for tire in tires:
        vehicle = tire.vehicle
        result.append(
            TireWithVehicle(
                **tire.__dict__,
                vehicle_info={
                    "id": vehicle.id,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "license_plate": vehicle.license_plate
                } if vehicle else None
            )
        )
    
    return result


@router.get("/stats/summary", response_model=dict)
def get_tire_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche generali pneumatici.
    """
    total_tires = db.query(func.count(Tire.id)).scalar() or 0
    
    # Conta per condizione
    condition_stats = db.query(
        Tire.condition,
        func.count(Tire.id)
    ).group_by(Tire.condition).all()
    
    # Pneumatici da sostituire
    needs_replacement = db.query(func.count(Tire.id)).filter(
        or_(
            Tire.tread_depth < 3.0,
            Tire.condition.in_([TireCondition.POOR, TireCondition.WORN_OUT])
        )
    ).scalar() or 0
    
    # Profondità media
    avg_tread_depth = db.query(func.avg(Tire.tread_depth)).scalar() or 0
    
    return {
        "total_tires": total_tires,
        "needs_replacement": needs_replacement,
        "average_tread_depth": round(float(avg_tread_depth), 2),
        "by_condition": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in condition_stats
        }
    }
