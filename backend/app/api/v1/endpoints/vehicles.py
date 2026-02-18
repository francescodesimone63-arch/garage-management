"""
Endpoint per gestione veicoli
"""
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.customer import Customer
from app.models.work_order import WorkOrder
from app.models.courtesy_car import CourtesyCar
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleWithHistory

router = APIRouter()


@router.get("/")
def read_vehicles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = Query(None, description="Filtra per cliente"),
    search: Optional[str] = Query(None, description="Cerca per targa o telaio"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni lista veicoli con filtri opzionali - formato paginato
    """
    query = db.query(Vehicle)

    # Filtra per cliente se specificato
    if customer_id:
        query = query.filter(Vehicle.customer_id == customer_id)

    # Applica ricerca se fornita
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Vehicle.targa.ilike(search_filter)) |
            (Vehicle.telaio.ilike(search_filter))
        )

    # Conta totale
    total = query.count()
    
    # Ottieni veicoli paginati
    vehicles = query.offset(skip).limit(limit).all()
    
    # Ritorna formato paginato con serializzazione
    return {
        "items": [VehicleResponse.model_validate(v) for v in vehicles],
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "size": limit
    }


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Crea nuovo veicolo
    """
    # Verifica che il cliente esista
    customer = db.query(Customer).filter(Customer.id == vehicle_in.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    # Verifica targa univoca
    existing = db.query(Vehicle).filter(Vehicle.targa == vehicle_in.targa).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un veicolo con questa targa esiste già"
        )
    
    # Verifica telaio univoco se fornito
    if vehicle_in.telaio:
        existing = db.query(Vehicle).filter(Vehicle.telaio == vehicle_in.telaio).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un veicolo con questo telaio esiste già"
            )
    
    # Crea veicolo
    vehicle = Vehicle(**vehicle_in.dict())
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    return VehicleResponse.model_validate(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def read_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni veicolo specifico per ID
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    return VehicleResponse.model_validate(vehicle)


@router.get("/{vehicle_id}/history", response_model=VehicleWithHistory)
def read_vehicle_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni veicolo con storico lavori
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    return vehicle


@router.get("/{vehicle_id}/maintenance-status")
def read_vehicle_maintenance_status(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni stato manutenzione veicolo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    # Calcola km dall'ultimo tagliando
    last_service = db.query(WorkOrder).filter(
        WorkOrder.vehicle_id == vehicle_id,
        WorkOrder.status.in_(["completed", "paid"]),
        WorkOrder.type_of_service == "maintenance"
    ).order_by(WorkOrder.completion_date.desc()).first()
    
    km_since_service = None
    if last_service and last_service.odometer_reading and vehicle.km_attuali:
        km_since_service = vehicle.km_attuali - last_service.odometer_reading
    
    # Conta giorni dall'ultimo intervento
    days_since_service = None
    if last_service and last_service.completion_date:
        days_since_service = (datetime.now() - last_service.completion_date).days
    
    return {
        "vehicle_id": vehicle_id,
        "current_mileage": vehicle.km_attuali,
        "last_service_date": last_service.completion_date if last_service else None,
        "last_service_mileage": last_service.odometer_reading if last_service else None,
        "km_since_service": km_since_service,
        "days_since_service": days_since_service,
        "needs_service": km_since_service > 15000 if km_since_service else False
    }


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Aggiorna veicolo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    # Verifica targa univoca se cambiata
    if vehicle_in.targa is not None and vehicle_in.targa != vehicle.targa:
        existing = db.query(Vehicle).filter(
            Vehicle.targa == vehicle_in.targa,
            Vehicle.id != vehicle_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questa targa è già in uso"
            )
    
    # Verifica telaio univoco se cambiato
    if vehicle_in.telaio is not None and vehicle_in.telaio != vehicle.telaio:
        existing = db.query(Vehicle).filter(
            Vehicle.telaio == vehicle_in.telaio,
            Vehicle.id != vehicle_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo telaio è già in uso"
            )
    
    # ========== VALIDAZIONE COURTESY CAR ==========
    # Controlla se sta cambiando courtesy_car flag o cliente
    update_data = vehicle_in.dict(exclude_unset=True)
    is_changing_courtesy_flag = "courtesy_car" in update_data and update_data["courtesy_car"] != vehicle.courtesy_car
    is_changing_customer = "customer_id" in update_data and update_data["customer_id"] != vehicle.customer_id
    
    if is_changing_courtesy_flag or is_changing_customer:
        # Controlla se esiste un record in courtesy_cars per questo veicolo
        courtesy_car_record = db.query(CourtesyCar).filter(CourtesyCar.vehicle_id == vehicle_id).first()
        
        if courtesy_car_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo veicolo è un'auto di cortesia. Per poter cambiare stato si devono cancellare i dati nella funzione preposta"
            )
    
    # ========== AGGIORNA CAMPI ==========
    old_customer_id = vehicle.customer_id
    new_customer_id = update_data.get("customer_id", old_customer_id)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    # Se il customer_id è cambiato, aggiorna tutte le work order associate a questo veicolo
    if "customer_id" in update_data and new_customer_id != old_customer_id:
        work_orders = db.query(WorkOrder).filter(WorkOrder.vehicle_id == vehicle_id).all()
        for wo in work_orders:
            wo.customer_id = new_customer_id
            db.add(wo)
        db.commit()

    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Elimina veicolo (solo se non ha ordini di lavoro)
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veicolo non trovato"
        )
    
    # Verifica che non abbia ordini di lavoro
    work_orders_count = db.query(WorkOrder).filter(WorkOrder.vehicle_id == vehicle_id).count()
    if work_orders_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non è possibile eliminare un veicolo con ordini di lavoro associati"
        )
    
    db.delete(vehicle)
    db.commit()
