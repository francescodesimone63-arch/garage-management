"""
Vehicle schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

# Import at runtime to allow Pydantic to resolve forward references
# Circular imports are OK here because we use forward references with strings
if TYPE_CHECKING:
    pass


class VehicleBase(BaseModel):
    """Base vehicle schema"""
    customer_id: int
    marca: str = Field(..., min_length=1, max_length=50)
    modello: str = Field(..., min_length=1, max_length=50)
    anno: int = Field(..., ge=1900, le=2100)
    targa: str = Field(..., min_length=1, max_length=20)
    telaio: Optional[str] = Field(None, min_length=1, max_length=50)
    colore: Optional[str] = Field(None, max_length=30)
    km_attuali: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    
    # Dati tecnici (da verifica targa)
    cilindrata: Optional[str] = Field(None, max_length=20)
    kw: Optional[int] = Field(None, ge=0)
    cv: Optional[int] = Field(None, ge=0)
    porte: Optional[int] = Field(None, ge=2, le=7)
    carburante: Optional[str] = Field(None, max_length=30)
    prima_immatricolazione: Optional[str] = Field(None, max_length=10)
    
    @validator('targa')
    def validate_targa(cls, v):
        # Italian license plate format validation (simplified)
        return v.upper().replace(' ', '')
    
    @validator('telaio')
    def validate_telaio(cls, v):
        # VIN validation but allow any length
        if v and len(v) > 0:
            return v.upper()
        return v


class VehicleCreate(VehicleBase):
    """Schema for creating a vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    customer_id: Optional[int] = None
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modello: Optional[str] = Field(None, min_length=1, max_length=50)
    anno: Optional[int] = Field(None, ge=1900, le=2100)
    targa: Optional[str] = Field(None, min_length=1, max_length=20)
    telaio: Optional[str] = Field(None, min_length=1, max_length=50)
    colore: Optional[str] = Field(None, max_length=30)
    km_attuali: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    
    # Dati tecnici (da verifica targa)
    cilindrata: Optional[str] = Field(None, max_length=20)
    kw: Optional[int] = Field(None, ge=0)
    cv: Optional[int] = Field(None, ge=0)
    porte: Optional[int] = Field(None, ge=2, le=7)
    carburante: Optional[str] = Field(None, max_length=30)
    prima_immatricolazione: Optional[str] = Field(None, max_length=10)


class VehicleInDBBase(VehicleBase):
    """Base schema for vehicle in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Vehicle(VehicleInDBBase):
    """Schema for vehicle response"""
    work_orders_count: Optional[int] = 0
    last_service_date: Optional[datetime] = None
    next_service_km: Optional[int] = None
    
    class Config:
        from_attributes = True


# Alias for compatibility
VehicleResponse = Vehicle


class VehicleWithCustomer(Vehicle):
    """Schema for vehicle with customer info"""
    customer: Optional['Customer'] = None


class VehicleWithHistory(Vehicle):
    """Schema for vehicle with service history"""
    work_orders: List['WorkOrder'] = []
    total_spent: Optional[float] = 0.0


class VehicleMaintenanceStatus(BaseModel):
    """Schema for vehicle maintenance status"""
    vehicle_id: int
    targa: str
    prossima_revisione: Optional[date] = None
    prossimo_tagliando_km: Optional[int] = None
    prossimo_tagliando_data: Optional[date] = None
    giorni_alla_revisione: Optional[int] = None
    km_al_tagliando: Optional[int] = None
    stato: str  # 'ok', 'warning', 'critical'
    
    class Config:
        from_attributes = True
