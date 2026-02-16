"""
API endpoints per la gestione degli scadenziari manutenzione (Maintenance Schedules).
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.maintenance_schedule import MaintenanceSchedule, MaintenanceType, MaintenanceStatus
from app.models.vehicle import Vehicle
from app.schemas.maintenance_schedule import (
    MaintenanceScheduleCreate, MaintenanceScheduleUpdate, MaintenanceScheduleResponse,
    MaintenanceScheduleWithVehicle, MaintenanceAlert
)

router = APIRouter()


@router.get("/", response_model=List[MaintenanceScheduleResponse])
def get_maintenance_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    vehicle_id: Optional[int] = None,
    maintenance_type: Optional[MaintenanceType] = None,
    status_filter: Optional[MaintenanceStatus] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera scadenziari manutenzione con filtri.
    """
    query = db.query(MaintenanceSchedule)
    
    # Filtro veicolo
    if vehicle_id:
        query = query.filter(MaintenanceSchedule.vehicle_id == vehicle_id)
    
    # Filtro tipo manutenzione
    if maintenance_type:
        query = query.filter(MaintenanceSchedule.tipo == maintenance_type)
    
    # Filtro status
    if status_filter:
        query = query.filter(MaintenanceSchedule.stato == status_filter)
    
    # Solo scaduti
    if overdue_only:
        today = datetime.utcnow().date()
        query = query.filter(
            and_(
                MaintenanceSchedule.stato == MaintenanceStatus.ATTIVO,
                or_(
                    MaintenanceSchedule.data_scadenza < today,
                    MaintenanceSchedule.km_scadenza.isnot(None)  # TODO: verificare con km attuali veicolo
                )
            )
        )
    
    query = query.order_by(MaintenanceSchedule.data_scadenza.asc())
    schedules = query.offset(skip).limit(limit).all()
    
    return schedules


@router.post("/", response_model=MaintenanceScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_schedule(
    schedule_data: MaintenanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Crea nuovo scadenzario manutenzione.
    Richiede ruolo: ADMIN, GENERAL_MANAGER, WORKSHOP
    """
    # Verifica esistenza veicolo
    vehicle = db.query(Vehicle).filter(Vehicle.id == schedule_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veicolo ID {schedule_data.vehicle_id} non trovato"
        )
    
    # Crea scadenzario
    schedule = MaintenanceSchedule(**schedule_data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # TODO: Creare notifica automatica
    
    return schedule


@router.get("/alerts", response_model=List[MaintenanceAlert])
def get_maintenance_alerts(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera alert manutenzioni in scadenza.
    
    days_ahead: giorni di anticipo per alert (default 30)
    """
    today = datetime.utcnow().date()
    alert_date = today + timedelta(days=days_ahead)
    
    # Recupera manutenzioni attive in scadenza
    query = db.query(MaintenanceSchedule).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVO,
            MaintenanceSchedule.data_scadenza <= alert_date
        )
    ).order_by(MaintenanceSchedule.data_scadenza.asc())
    
    schedules = query.all()
    
    # Costruisci alert con info veicolo
    alerts = []
    for schedule in schedules:
        vehicle = schedule.vehicle
        days_until_due = (schedule.data_scadenza - today).days if schedule.data_scadenza else None
        
        alert_level = "info"
        if days_until_due < 0:
            alert_level = "critical"  # Scaduto
        elif days_until_due <= 7:
            alert_level = "warning"  # Scade tra 7 giorni
        
        alerts.append(
            MaintenanceAlert(
                **schedule.__dict__,
                vehicle_info={
                    "id": vehicle.id,
                    "marca": vehicle.marca,
                    "modello": vehicle.modello,
                    "targa": vehicle.targa
                } if vehicle else None,
                days_until_due=days_until_due,
                is_overdue=days_until_due < 0,
                alert_level=alert_level
            )
        )
    
    return alerts


@router.get("/vehicle/{vehicle_id}", response_model=List[MaintenanceScheduleWithVehicle])
def get_vehicle_schedules(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera tutti gli scadenziari di un veicolo.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veicolo ID {vehicle_id} non trovato"
        )
    
    schedules = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id
    ).order_by(MaintenanceSchedule.data_scadenza.asc()).all()
    
    # Costruisci risposta con info veicolo
    result = []
    for schedule in schedules:
        result.append(
            MaintenanceScheduleWithVehicle(
                **schedule.__dict__,
                vehicle_info={
                    "id": vehicle.id,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "license_plate": vehicle.license_plate
                }
            )
        )
    
    return result


@router.get("/{schedule_id}", response_model=MaintenanceScheduleWithVehicle)
def get_maintenance_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli scadenzario manutenzione.
    """
    schedule = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scadenzario ID {schedule_id} non trovato"
        )
    
    vehicle = schedule.vehicle
    
    return MaintenanceScheduleWithVehicle(
        **schedule.__dict__,
        vehicle_info={
            "id": vehicle.id,
            "marca": vehicle.marca,
            "modello": vehicle.modello,
            "targa": vehicle.targa
        } if vehicle else None
    )


@router.put("/{schedule_id}", response_model=MaintenanceScheduleResponse)
def update_maintenance_schedule(
    schedule_id: int,
    schedule_data: MaintenanceScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Aggiorna scadenzario manutenzione.
    Richiede ruolo: ADMIN, GENERAL_MANAGER, WORKSHOP
    """
    schedule = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scadenzario ID {schedule_id} non trovato"
        )
    
    # Aggiorna campi
    update_data = schedule_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Elimina scadenzario manutenzione.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    schedule = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scadenzario ID {schedule_id} non trovato"
        )
    
    db.delete(schedule)
    db.commit()
    
    return None


@router.patch("/{schedule_id}/complete", response_model=MaintenanceScheduleResponse)
def complete_maintenance(
    schedule_id: int,
    completion_date: Optional[datetime] = None,
    completion_km: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Segna manutenzione come completata.
    """
    schedule = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scadenzario ID {schedule_id} non trovato"
        )
    
    if schedule.stato == MaintenanceStatus.COMPLETATO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manutenzione già completata"
        )
    
    # Aggiorna status e dati completamento
    schedule.stato = MaintenanceStatus.COMPLETATO
    schedule.completion_date = completion_date or datetime.utcnow()
    schedule.completion_km = completion_km
    
    if notes:
        schedule.notes = f"{schedule.notes}\n{notes}" if schedule.notes else notes
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.patch("/{schedule_id}/skip", response_model=MaintenanceScheduleResponse)
def skip_maintenance(
    schedule_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Salta/annulla manutenzione.
    """
    schedule = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scadenzario ID {schedule_id} non trovato"
        )
    
    schedule.stato = MaintenanceStatus.ANNULLATO
    schedule.notes = f"{schedule.notes}\nSALTATO: {reason}" if schedule.notes else f"SALTATO: {reason}"
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.get("/stats/summary", response_model=dict)
def get_maintenance_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche scadenzari manutenzione.
    """
    total_schedules = db.query(func.count(MaintenanceSchedule.id)).scalar() or 0
    
    # Conta per status
    status_stats = db.query(
        MaintenanceSchedule.status,
        func.count(MaintenanceSchedule.id)
    ).group_by(MaintenanceSchedule.status).all()
    
    # Conta scaduti
    today = datetime.utcnow().date()
    overdue = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVO,
            MaintenanceSchedule.data_scadenza < today
        )
    ).scalar() or 0
    
    # Prossimi 30 giorni
    upcoming = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVO,
            MaintenanceSchedule.data_scadenza >= today,
            MaintenanceSchedule.data_scadenza <= today + timedelta(days=30)
        )
    ).scalar() or 0
    
    return {
        "total_schedules": total_schedules,
        "overdue": overdue,
        "upcoming_30_days": upcoming,
        "by_status": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in status_stats
        }
    }
