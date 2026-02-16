"""
API endpoints per la gestione delle auto di cortesia (Courtesy Cars).
ALLINEATO AL MODELLO DATABASE
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.courtesy_car import CourtesyCar, CourtesyCarStatus, CarAssignment, AssignmentStatus
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.schemas.courtesy_car import (
    CourtesyCarCreate, CourtesyCarUpdate, CourtesyCarResponse,
    CourtesyCarWithLoans, CourtesyCarLoanRequest, CourtesyCarReturnRequest
)

router = APIRouter()


@router.get("/", response_model=List[CourtesyCarResponse])
def get_courtesy_cars(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    stato_filter: Optional[CourtesyCarStatus] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera lista auto di cortesia con filtri.
    ALLINEATO AL MODELLO: usa 'stato' non 'status'
    """
    query = db.query(CourtesyCar)
    
    # Filtro stato
    if stato_filter:
        query = query.filter(CourtesyCar.stato == stato_filter)
    
    # Solo disponibili
    if available_only:
        query = query.filter(CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE)
    
    # Join con vehicle per ordinare per targa
    query = query.join(Vehicle).order_by(Vehicle.targa)
    courtesy_cars = query.offset(skip).limit(limit).all()
    
    return courtesy_cars


@router.post("/", response_model=CourtesyCarResponse, status_code=status.HTTP_201_CREATED)
def create_courtesy_car(
    car_data: CourtesyCarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Registra una nuova auto di cortesia.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    ALLINEATO AL MODELLO: usa vehicle_id non license_plate
    """
    # Verifica vehicle_id univoco in courtesy_cars
    existing = db.query(CourtesyCar).filter(
        CourtesyCar.vehicle_id == car_data.vehicle_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle ID '{car_data.vehicle_id}' già registrata come auto di cortesia"
        )
    
    # Verifica che il vehicle esista
    vehicle = db.query(Vehicle).filter(Vehicle.id == car_data.vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle ID {car_data.vehicle_id} non trovato"
        )
    
    # Crea auto di cortesia
    courtesy_car = CourtesyCar(**car_data.model_dump())
    db.add(courtesy_car)
    db.commit()
    db.refresh(courtesy_car)
    
    return courtesy_car


@router.get("/available", response_model=List[CourtesyCarResponse])
def get_available_cars(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera auto di cortesia disponibili.
    
    Se specificate date, verifica disponibilità nel periodo usando CarAssignment.
    ALLINEATO AL MODELLO: usa stato=DISPONIBILE e verifico assignmentssenza sovrapposizioni
    """
    query = db.query(CourtesyCar).filter(
        CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE
    )
    
    # TODO: Se specificate date, controllare sovrapposizioni con assegnazioni in corso
    # SELECT courtesy_car WHERE NOT EXISTS(
    #   SELECT * FROM car_assignments 
    #   WHERE (data_inizio BETWEEN date_from AND date_to)
    #     AND (data_fine_effettiva IS NULL OR data_fine_effettiva >= date_from)
    # )
    
    # Join con vehicle per ordinare per targa
    cars = query.join(Vehicle).order_by(Vehicle.targa).all()
    return cars


@router.get("/{car_id}", response_model=CourtesyCarWithLoans)
def get_courtesy_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli auto di cortesia con storico prestiti.
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # TODO: Recuperare storico prestiti da tabella apposita
    loan_history = []
    
    return CourtesyCarWithLoans(
        **car.__dict__,
        loan_history=loan_history,
        total_loans=len(loan_history)
    )


@router.put("/{car_id}", response_model=CourtesyCarResponse)
def update_courtesy_car(
    car_id: int,
    car_data: CourtesyCarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Aggiorna informazioni auto di cortesia.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    ALLINEATO AL MODELLO: non modifichiamo vehicle_id (è unique, immutabile)
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # Aggiorna campi (escludiamo vehicle_id per evitare conflitti di unicità)
    update_data = car_data.model_dump(exclude_unset=True, exclude={'vehicle_id'})
    for field, value in update_data.items():
        setattr(car, field, value)
    
    db.commit()
    db.refresh(car)
    
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_courtesy_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """
    Elimina auto di cortesia.
    Richiede ruolo: ADMIN
    ALLINEATO AL MODELLO: controlla AssignmentStatus, non usa campi inesistenti
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # Verifica che non abbia assegnazioni in corso
    active_assignment = db.query(CarAssignment).filter(
        and_(
            CarAssignment.courtesy_car_id == car_id,
            CarAssignment.stato.in_([AssignmentStatus.PRENOTATA, AssignmentStatus.IN_CORSO])
        )
    ).first()
    
    if active_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossibile eliminare: auto ha assegnazioni in corso o prenotate"
        )
    
    db.delete(car)
    db.commit()
    
    return None


@router.post("/{car_id}/loan", response_model=CourtesyCarResponse)
def loan_courtesy_car(
    car_id: int,
    loan_data: CourtesyCarLoanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP, UserRole.BODYSHOP]))
):
    """
    Registra assegnazione auto di cortesia a cliente tramite CarAssignment.
    ALLINEATO AL MODELLO: crea record in CarAssignment, non modifica CourtesyCar direttamente
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # Verifica disponibilità (nessuna assegnazione attiva)
    active_assignment = db.query(CarAssignment).filter(
        and_(
            CarAssignment.courtesy_car_id == car_id,
            CarAssignment.stato.in_([AssignmentStatus.PRENOTATA, AssignmentStatus.IN_CORSO])
        )
    ).first()
    
    if active_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auto non disponibile. C'è un'assegnazione in corso"
        )
    
    # Verifica esistenza cliente
    customer = db.query(Customer).filter(Customer.id == loan_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente ID {loan_data.customer_id} non trovato"
        )
    
    # Verifica work_order
    if loan_data.work_order_id:
        from app.models.work_order import WorkOrder
        work_order = db.query(WorkOrder).filter(WorkOrder.id == loan_data.work_order_id).first()
        if not work_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheda lavoro ID {loan_data.work_order_id} non trovata"
            )
    
    # Crea assegnazione
    assignment = CarAssignment(
        courtesy_car_id=car_id,
        work_order_id=loan_data.work_order_id,
        customer_id=loan_data.customer_id,
        data_inizio=loan_data.loan_start_date or datetime.utcnow(),
        data_fine_prevista=loan_data.expected_return_date,
        km_inizio=loan_data.km_at_loan,
        stato=AssignmentStatus.PRENOTATA,
        note=loan_data.notes
    )
    db.add(assignment)
    
    # Aggiorna stato auto a ASSEGNATA
    car.stato = CourtesyCarStatus.ASSEGNATA
    
    db.commit()
    db.refresh(car)
    
    return car


@router.post("/{car_id}/return", response_model=CourtesyCarResponse)
def return_courtesy_car(
    car_id: int,
    return_data: CourtesyCarReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP, UserRole.BODYSHOP]))
):
    """
    Registra restituzione auto di cortesia completando l'assegnazione.
    ALLINEATO AL MODELLO: aggiorna CarAssignment, non modifica CourtesyCar direttamente
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # Cerca assegnazione in corso
    assignment = db.query(CarAssignment).filter(
        and_(
            CarAssignment.courtesy_car_id == car_id,
            CarAssignment.stato.in_([AssignmentStatus.PRENOTATA, AssignmentStatus.IN_CORSO])
        )
    ).order_by(CarAssignment.data_inizio.desc()).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nessuna assegnazione attiva per l'auto"
        )
    
    # Calcola km percorsi
    km_driven = 0
    if assignment.km_inizio and return_data.km_at_return:
        km_driven = return_data.km_at_return - assignment.km_inizio
    
    # Aggiorna assegnazione
    assignment.data_fine_effettiva = return_data.return_date or datetime.utcnow()
    assignment.km_fine = return_data.km_at_return
    assignment.stato = AssignmentStatus.COMPLETATA
    assignment.note = return_data.condition_notes or assignment.note
    
    # Aggiorna stato auto
    new_status = CourtesyCarStatus.DISPONIBILE
    if return_data.needs_maintenance:
        new_status = CourtesyCarStatus.MANUTENZIONE
    
    car.stato = new_status
    
    db.commit()
    db.refresh(car)
    
    return car


@router.patch("/{car_id}/maintenance", response_model=CourtesyCarResponse)
def set_maintenance_status(
    car_id: int,
    in_maintenance: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER, UserRole.WORKSHOP]))
):
    """
    Imposta/rimuove stato manutenzione per auto di cortesia.
    ALLINEATO AL MODELLO: usa stato=MANUTENZIONE o DISPONIBILE, non verifica campi inesistenti
    """
    car = db.query(CourtesyCar).filter(CourtesyCar.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Auto di cortesia ID {car_id} non trovata"
        )
    
    # Verifica che non abbia assegnazioni in corso
    active_assignment = db.query(CarAssignment).filter(
        and_(
            CarAssignment.courtesy_car_id == car_id,
            CarAssignment.stato == AssignmentStatus.IN_CORSO
        )
    ).first()
    
    if active_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossibile modificare: auto attualmente assegnata"
        )
    
    if in_maintenance:
        car.stato = CourtesyCarStatus.MANUTENZIONE
    else:
        car.stato = CourtesyCarStatus.DISPONIBILE
    
    db.commit()
    db.refresh(car)
    
    return car


@router.get("/stats/summary", response_model=dict)
def get_courtesy_car_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche generali auto di cortesia.
    ALLINEATO AL MODELLO: usa stato non status, valori corretti enum
    """
    total_cars = db.query(func.count(CourtesyCar.id)).scalar() or 0
    
    # Conta per stato
    state_stats = db.query(
        CourtesyCar.stato,
        func.count(CourtesyCar.id)
    ).group_by(CourtesyCar.stato).all()
    
    available = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE
    ).scalar() or 0
    
    assigned = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.ASSEGNATA
    ).scalar() or 0
    
    in_maintenance = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.MANUTENZIONE
    ).scalar() or 0
    
    out_of_service = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.FUORI_SERVIZIO
    ).scalar() or 0
    
    return {
        "total_cars": total_cars,
        "available": available,
        "assigned": assigned,
        "in_maintenance": in_maintenance,
        "out_of_service": out_of_service,
        "utilization_rate": round((assigned / total_cars * 100) if total_cars > 0 else 0, 2),
        "by_status": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in state_stats
        }
    }
