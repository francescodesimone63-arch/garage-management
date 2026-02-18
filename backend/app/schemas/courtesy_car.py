"""
Courtesy car schemas for API requests and responses
ALLINEATO AL MODELLO DATABASE
"""
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from app.models.courtesy_car import CourtesyCarStatus, AssignmentStatus


class CourtesyCarBase(BaseModel):
    """
    Base courtesy car schema - ALLINEATO AL MODELLO.
    
    NOTA IMPORTANTE: La disponibilità è gestita SOLO dal campo Vehicle.disponibile.
    Il campo 'stato' è usato per tracciare il ciclo di vita del contratto (manutenzione, etc.)
    e NON determina la disponibilità per l'assegnazione a schede lavoro.
    """
    vehicle_id: int = Field(..., gt=0)
    contratto_tipo: str = Field(..., pattern="^(leasing|affitto|proprieta)$")
    fornitore_contratto: Optional[str] = Field(None, max_length=200)
    data_inizio_contratto: Optional[date] = None
    data_scadenza_contratto: Optional[date] = None
    canone_mensile: Optional[Decimal] = Field(None, ge=0)
    km_inclusi_anno: Optional[int] = Field(None, ge=0)
    stato: CourtesyCarStatus = CourtesyCarStatus.DISPONIBILE
    note: Optional[str] = None
    contratto_firmato: Optional[str] = Field(None, max_length=500)  # Path al file PDF
    
    @validator('data_scadenza_contratto')
    def validate_scadenza(cls, v, values):
        if v and 'data_inizio_contratto' in values and values['data_inizio_contratto']:
            if v <= values['data_inizio_contratto']:
                raise ValueError('Data scadenza deve essere dopo data inizio')
        return v


class CourtesyCarCreate(CourtesyCarBase):
    """Schema for creating a courtesy car"""
    pass


class CourtesyCarUpdate(BaseModel):
    """Schema for updating a courtesy car"""
    vehicle_id: Optional[int] = Field(None, gt=0)
    contratto_tipo: Optional[str] = Field(None, pattern="^(leasing|affitto|proprieta)$")
    fornitore_contratto: Optional[str] = Field(None, max_length=200)
    data_inizio_contratto: Optional[date] = None
    data_scadenza_contratto: Optional[date] = None
    canone_mensile: Optional[Decimal] = Field(None, ge=0)
    km_inclusi_anno: Optional[int] = Field(None, ge=0)
    stato: Optional[CourtesyCarStatus] = None
    note: Optional[str] = None
    contratto_firmato: Optional[str] = Field(None, max_length=500)  # Path al file PDF


class CourtesyCarInDBBase(CourtesyCarBase):
    """Base schema for courtesy car in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class CourtesyCar(CourtesyCarInDBBase):
    """Schema for courtesy car response"""
    
    class Config:
        from_attributes = True


class CarAssignmentBase(BaseModel):
    """Base car assignment schema"""
    courtesy_car_id: int = Field(..., gt=0)
    work_order_id: Optional[int] = Field(None, gt=0)
    customer_id: int = Field(..., gt=0)
    data_inizio: datetime
    data_fine_prevista: datetime
    km_inizio: Optional[int] = Field(None, ge=0)
    stato: AssignmentStatus = AssignmentStatus.PRENOTATA
    note: Optional[str] = None
    
    @validator('data_fine_prevista')
    def validate_fine_prevista(cls, v, values):
        if 'data_inizio' in values and v <= values['data_inizio']:
            raise ValueError('Data fine prevista deve essere dopo data inizio')
        return v


class CarAssignmentCreate(CarAssignmentBase):
    """Schema for creating a car assignment"""
    pass


class CarAssignmentUpdate(BaseModel):
    """Schema for updating a car assignment"""
    data_fine_effettiva: Optional[datetime] = None
    km_fine: Optional[int] = Field(None, ge=0)
    stato: Optional[AssignmentStatus] = None
    note: Optional[str] = None


class CarAssignmentResponse(CarAssignmentBase):
    """Schema for car assignment response"""
    id: int
    data_fine_effettiva: Optional[datetime] = None
    km_fine: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CourtesyCarWithAssignments(CourtesyCar):
    """Schema for courtesy car with active assignment"""
    active_assignment: Optional[CarAssignmentResponse] = None
    total_assignments: int = 0
    assignments: List[CarAssignmentResponse] = []


# Aliases for endpoint compatibility
CourtesyCarResponse = CourtesyCar
CourtesyCarWithLoans = CourtesyCarWithAssignments  # Alias for backward compatibility with endpoints


class CourtesyCarLoanRequest(BaseModel):
    """Schema for requesting a courtesy car assignment"""
    customer_id: int = Field(..., gt=0)
    work_order_id: Optional[int] = Field(None, gt=0)
    loan_start_date: Optional[datetime] = None
    expected_return_date: Optional[datetime] = None
    km_at_loan: int = Field(..., ge=0)
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class CourtesyCarReturnRequest(BaseModel):
    """Schema for returning a courtesy car"""
    return_date: Optional[datetime] = None
    km_at_return: int = Field(..., ge=0)
    condition_notes: Optional[str] = None
    needs_maintenance: bool = False
    
    class Config:
        from_attributes = True
