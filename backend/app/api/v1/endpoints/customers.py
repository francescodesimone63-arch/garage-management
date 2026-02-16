"""
Endpoint per gestione clienti
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithVehicles, CustomerStats

router = APIRouter()


@router.get("/")
def read_customers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Cerca per nome, cognome, email o telefono"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni lista clienti con ricerca opzionale - formato paginato
    """
    query = db.query(Customer)
    
    # Applica filtro ricerca se fornito
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Customer.nome.ilike(search_filter)) |
            (Customer.cognome.ilike(search_filter)) |
            (Customer.email.ilike(search_filter)) |
            (Customer.telefono.ilike(search_filter))
        )
    
    # Conta totale
    total = query.count()
    
    # Ottieni clienti paginati
    customers = query.offset(skip).limit(limit).all()
    
    # Ritorna formato paginato con serializzazione
    return {
        "items": [CustomerResponse.model_validate(c) for c in customers],
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "size": limit
    }


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: CustomerCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Crea nuovo cliente
    """
    # Verifica email univoca (se fornita)
    if customer_in.email:
        existing = db.query(Customer).filter(Customer.email == customer_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un cliente con questa email esiste già"
            )
    
    # Crea cliente - USA model_dump
    customer = Customer(**customer_in.model_dump())
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni cliente specifico per ID
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}/details", response_model=CustomerWithVehicles)
def read_customer_with_vehicles(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni cliente con i suoi veicoli
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    return customer


@router.get("/{customer_id}/stats", response_model=CustomerStats)
def read_customer_stats(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni statistiche cliente
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    # Conta veicoli
    vehicles_count = db.query(Vehicle).filter(Vehicle.customer_id == customer_id).count()
    
    # Conta ordini di lavoro
    work_orders_count = db.query(WorkOrder).join(Vehicle).filter(
        Vehicle.customer_id == customer_id
    ).count()
    
    # Calcola totale speso
    total_spent = db.query(WorkOrder).join(Vehicle).filter(
        Vehicle.customer_id == customer_id,
        WorkOrder.status.in_(["completed", "paid"])
    ).with_entities(
        db.func.sum(WorkOrder.total_cost)
    ).scalar() or 0.0
    
    return {
        "customer_id": customer_id,
        "vehicles_count": vehicles_count,
        "work_orders_count": work_orders_count,
        "total_spent": float(total_spent)
    }


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: CustomerUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Aggiorna cliente
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    # Verifica email univoca se cambiata
    if customer_in.email is not None and customer_in.email != customer.email:
        existing = db.query(Customer).filter(
            Customer.email == customer_in.email,
            Customer.id != customer_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questa email è già in uso"
            )
    
    # Aggiorna campi - USA model_dump
    update_data = customer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Elimina cliente (solo se non ha veicoli o ordini)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente non trovato"
        )
    
    # Verifica che non abbia veicoli
    vehicles_count = db.query(Vehicle).filter(Vehicle.customer_id == customer_id).count()
    if vehicles_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non è possibile eliminare un cliente con veicoli associati"
        )
    
    db.delete(customer)
    db.commit()
