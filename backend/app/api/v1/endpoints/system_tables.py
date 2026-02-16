"""
System tables endpoints for master data management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.deps import get_db, get_current_user, get_current_active_superuser
from app.models import DamageType, CustomerType, WorkOrderStatusType, PriorityType, InterventionStatusType, User
from app.schemas.system_tables import (
    DamageTypeCreate,
    DamageTypeUpdate,
    DamageTypeResponse,
    CustomerTypeCreate,
    CustomerTypeUpdate,
    CustomerTypeResponse,
    WorkOrderStatusTypeCreate,
    WorkOrderStatusTypeUpdate,
    WorkOrderStatusTypeResponse,
    PriorityTypeCreate,
    PriorityTypeUpdate,
    PriorityTypeResponse,
    InterventionStatusTypeCreate,
    InterventionStatusTypeUpdate,
    InterventionStatusTypeResponse,
)

router = APIRouter(tags=["system-tables"])


# ============================================================================
# DAMAGE TYPES ENDPOINTS
# ============================================================================

@router.get("/damage-types", response_model=List[DamageTypeResponse])
def get_damage_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all damage types (accessibile a tutti gli utenti autenticati)"""
    return db.query(DamageType).all()


@router.post("/damage-types", response_model=DamageTypeResponse, status_code=status.HTTP_201_CREATED)
def create_damage_type(
    damage_type_in: DamageTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create damage type (admin only)"""
    # Check if already exists
    existing = db.query(DamageType).filter(
        DamageType.nome.ilike(damage_type_in.nome)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo tipo di danno esiste già"
        )
    
    damage_type = DamageType(**damage_type_in.model_dump())
    db.add(damage_type)
    db.commit()
    db.refresh(damage_type)
    return damage_type


@router.put("/damage-types/{damage_type_id}", response_model=DamageTypeResponse)
def update_damage_type(
    damage_type_id: int,
    damage_type_in: DamageTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update damage type (admin only)"""
    damage_type = db.query(DamageType).filter(DamageType.id == damage_type_id).first()
    
    if not damage_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di danno non trovato"
        )
    
    # Check nome uniqueness if changed
    if damage_type_in.nome and damage_type_in.nome != damage_type.nome:
        existing = db.query(DamageType).filter(
            DamageType.nome.ilike(damage_type_in.nome),
            DamageType.id != damage_type_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo nome è già in uso"
            )
    
    update_data = damage_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(damage_type, field, value)
    
    db.add(damage_type)
    db.commit()
    db.refresh(damage_type)
    return damage_type


@router.delete("/damage-types/{damage_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_damage_type(
    damage_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete damage type (admin only)"""
    damage_type = db.query(DamageType).filter(DamageType.id == damage_type_id).first()
    
    if not damage_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di danno non trovato"
        )
    
    db.delete(damage_type)
    db.commit()


# ============================================================================
# CUSTOMER TYPES ENDPOINTS
# ============================================================================

@router.get("/customer-types", response_model=List[CustomerTypeResponse])
def get_customer_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all customer types (accessibile a tutti gli utenti autenticati)"""
    return db.query(CustomerType).all()


@router.post("/customer-types", response_model=CustomerTypeResponse, status_code=status.HTTP_201_CREATED)
def create_customer_type(
    customer_type_in: CustomerTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create customer type (admin only)"""
    # Check if already exists
    existing = db.query(CustomerType).filter(
        CustomerType.nome.ilike(customer_type_in.nome)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo tipo di cliente esiste già"
        )
    
    customer_type = CustomerType(**customer_type_in.model_dump())
    db.add(customer_type)
    db.commit()
    db.refresh(customer_type)
    return customer_type


@router.put("/customer-types/{customer_type_id}", response_model=CustomerTypeResponse)
def update_customer_type(
    customer_type_id: int,
    customer_type_in: CustomerTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update customer type (admin only)"""
    customer_type = db.query(CustomerType).filter(CustomerType.id == customer_type_id).first()
    
    if not customer_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di cliente non trovato"
        )
    
    # Check nome uniqueness if changed
    if customer_type_in.nome and customer_type_in.nome != customer_type.nome:
        existing = db.query(CustomerType).filter(
            CustomerType.nome.ilike(customer_type_in.nome),
            CustomerType.id != customer_type_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo nome è già in uso"
            )
    
    update_data = customer_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer_type, field, value)
    
    db.add(customer_type)
    db.commit()
    db.refresh(customer_type)
    return customer_type


@router.delete("/customer-types/{customer_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_type(
    customer_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete customer type (admin only)"""
    customer_type = db.query(CustomerType).filter(CustomerType.id == customer_type_id).first()
    
    if not customer_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo di cliente non trovato"
        )
    
    db.delete(customer_type)
    db.commit()


# ============================================================================
# WORK ORDER STATUS TYPES ENDPOINTS
# ============================================================================

@router.get("/work-order-status-types", response_model=List[WorkOrderStatusTypeResponse])
def get_work_order_status_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all work order status types (accessibile a tutti gli utenti autenticati)"""
    return db.query(WorkOrderStatusType).all()


@router.post("/work-order-status-types", response_model=WorkOrderStatusTypeResponse, status_code=status.HTTP_201_CREATED)
def create_work_order_status_type(
    status_type_in: WorkOrderStatusTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create work order status type (admin only)"""
    # Check if already exists
    existing = db.query(WorkOrderStatusType).filter(
        WorkOrderStatusType.nome.ilike(status_type_in.nome)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo stato della scheda esiste già"
        )
    
    status_type = WorkOrderStatusType(**status_type_in.model_dump())
    db.add(status_type)
    db.commit()
    db.refresh(status_type)
    return status_type


@router.put("/work-order-status-types/{status_type_id}", response_model=WorkOrderStatusTypeResponse)
def update_work_order_status_type(
    status_type_id: int,
    status_type_in: WorkOrderStatusTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update work order status type (admin only)"""
    status_type = db.query(WorkOrderStatusType).filter(WorkOrderStatusType.id == status_type_id).first()
    
    if not status_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stato della scheda non trovato"
        )
    
    # Check nome uniqueness if changed
    if status_type_in.nome and status_type_in.nome != status_type.nome:
        existing = db.query(WorkOrderStatusType).filter(
            WorkOrderStatusType.nome.ilike(status_type_in.nome),
            WorkOrderStatusType.id != status_type_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo nome è già in uso"
            )
    
    update_data = status_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(status_type, field, value)
    
    db.add(status_type)
    db.commit()
    db.refresh(status_type)
    return status_type


@router.delete("/work-order-status-types/{status_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_work_order_status_type(
    status_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete work order status type (admin only)"""
    status_type = db.query(WorkOrderStatusType).filter(WorkOrderStatusType.id == status_type_id).first()
    
    if not status_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stato della scheda non trovato"
        )
    
    db.delete(status_type)
    db.commit()


# ============================================================================
# PRIORITY TYPES ENDPOINTS
# ============================================================================

@router.get("/priority-types", response_model=List[PriorityTypeResponse])
def get_priority_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all priority types (accessibile a tutti gli utenti autenticati)"""
    return db.query(PriorityType).all()


@router.post("/priority-types", response_model=PriorityTypeResponse, status_code=status.HTTP_201_CREATED)
def create_priority_type(
    priority_type_in: PriorityTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create priority type (admin only)"""
    # Check if already exists
    existing = db.query(PriorityType).filter(
        PriorityType.nome.ilike(priority_type_in.nome)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questa priorità esiste già"
        )
    
    priority_type = PriorityType(**priority_type_in.model_dump())
    db.add(priority_type)
    db.commit()
    db.refresh(priority_type)
    return priority_type


@router.put("/priority-types/{priority_type_id}", response_model=PriorityTypeResponse)
def update_priority_type(
    priority_type_id: int,
    priority_type_in: PriorityTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update priority type (admin only)"""
    priority_type = db.query(PriorityType).filter(PriorityType.id == priority_type_id).first()
    
    if not priority_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Priorità non trovata"
        )
    
    # Check nome uniqueness if changed
    if priority_type_in.nome and priority_type_in.nome != priority_type.nome:
        existing = db.query(PriorityType).filter(
            PriorityType.nome.ilike(priority_type_in.nome),
            PriorityType.id != priority_type_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo nome è già in uso"
            )
    
    update_data = priority_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(priority_type, field, value)
    
    db.add(priority_type)
    db.commit()
    db.refresh(priority_type)
    return priority_type


@router.delete("/priority-types/{priority_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_priority_type(
    priority_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete priority type (admin only)"""
    priority_type = db.query(PriorityType).filter(PriorityType.id == priority_type_id).first()
    
    if not priority_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Priorità non trovata"
        )
    
    db.delete(priority_type)
    db.commit()


# ============================================================================
# INTERVENTION STATUS TYPES ENDPOINTS
# ============================================================================

@router.get("/intervention-status-types", response_model=List[InterventionStatusTypeResponse])
def get_intervention_status_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all intervention status types (accessibile a tutti gli utenti autenticati).
    
    Stati predefiniti:
    - preso_in_carico: L'intervento è in lavorazione
    - attesa_componente: È stato richiesto l'acquisto di un componente
    - sospeso: Intervento sospeso (richiede nota descrittiva)
    - concluso: L'intervento è stato completato
    """
    return db.query(InterventionStatusType).filter(
        InterventionStatusType.attivo == True
    ).order_by(InterventionStatusType.ordine).all()


@router.get("/intervention-status-types/all", response_model=List[InterventionStatusTypeResponse])
def get_all_intervention_status_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """Get all intervention status types including inactive (admin only)"""
    return db.query(InterventionStatusType).order_by(InterventionStatusType.ordine).all()


@router.post("/intervention-status-types", response_model=InterventionStatusTypeResponse, status_code=status.HTTP_201_CREATED)
def create_intervention_status_type(
    status_type_in: InterventionStatusTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Create intervention status type (admin only)"""
    # Check if codice already exists
    existing = db.query(InterventionStatusType).filter(
        InterventionStatusType.codice.ilike(status_type_in.codice)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo codice stato intervento esiste già"
        )
    
    status_type = InterventionStatusType(**status_type_in.model_dump())
    db.add(status_type)
    db.commit()
    db.refresh(status_type)
    return status_type


@router.put("/intervention-status-types/{status_type_id}", response_model=InterventionStatusTypeResponse)
def update_intervention_status_type(
    status_type_id: int,
    status_type_in: InterventionStatusTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Update intervention status type (admin only)"""
    status_type = db.query(InterventionStatusType).filter(InterventionStatusType.id == status_type_id).first()
    
    if not status_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stato intervento non trovato"
        )
    
    # Check codice uniqueness if changed
    if status_type_in.codice and status_type_in.codice != status_type.codice:
        existing = db.query(InterventionStatusType).filter(
            InterventionStatusType.codice.ilike(status_type_in.codice),
            InterventionStatusType.id != status_type_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo codice è già in uso"
            )
    
    update_data = status_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(status_type, field, value)
    
    db.add(status_type)
    db.commit()
    db.refresh(status_type)
    return status_type


@router.delete("/intervention-status-types/{status_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intervention_status_type(
    status_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete intervention status type (admin only)"""
    status_type = db.query(InterventionStatusType).filter(InterventionStatusType.id == status_type_id).first()
    
    if not status_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stato intervento non trovato"
        )
    
    db.delete(status_type)
    db.commit()
