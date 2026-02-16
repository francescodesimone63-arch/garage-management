"""
Tire schemas for API requests and responses
ALLINEATO AL MODELLO DATABASE
"""
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from app.models.tire import TireStatus, TireSeason, TirePosition, TireCondition

if TYPE_CHECKING:
    from app.schemas.vehicle import Vehicle
else:
    Vehicle = Any


class TireBase(BaseModel):
    """Base tire schema - ALLINEATO AL MODELLO"""
    vehicle_id: int = Field(..., gt=0)
    tipo_stagione: TireSeason = Field(...)
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modello: Optional[str] = Field(None, min_length=1, max_length=50)
    misura: Optional[str] = Field(None, min_length=1, max_length=30)
    data_deposito: Optional[datetime] = None
    data_ultimo_cambio: Optional[datetime] = None
    data_prossimo_cambio: Optional[datetime] = None
    stato: TireStatus = TireStatus.DEPOSITATI
    posizione_deposito: Optional[str] = Field(None, max_length=50)
    posizione: Optional[TirePosition] = None
    condizione: TireCondition = TireCondition.BUONO
    profondita_battistrada: Optional[int] = Field(None, ge=0, le=20)
    data_produzione: Optional[datetime] = None
    data_ultima_rotazione: Optional[datetime] = None
    km_ultima_rotazione: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    
    @validator('data_prossimo_cambio')
    def validate_prossimo_cambio(cls, v, values):
        if v and 'data_ultimo_cambio' in values and values['data_ultimo_cambio']:
            if v <= values['data_ultimo_cambio']:
                raise ValueError('Data prossimo cambio deve essere dopo ultimo cambio')
        return v
    
    @validator('km_ultima_rotazione')
    def validate_km_ultima_rotazione(cls, v, values):
        if v is not None and v < 0:
            raise ValueError('km_ultima_rotazione non può essere negativo')
        return v


class TireCreate(TireBase):
    """Schema for creating a tire - TUTTI I CAMPI COME BASE"""
    pass


class TireUpdate(BaseModel):
    """Schema for updating a tire - TUTTI CAMPI OPZIONALI"""
    tipo_stagione: Optional[TireSeason] = None
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    modello: Optional[str] = Field(None, min_length=1, max_length=50)
    misura: Optional[str] = Field(None, min_length=1, max_length=30)
    data_deposito: Optional[datetime] = None
    data_ultimo_cambio: Optional[datetime] = None
    data_prossimo_cambio: Optional[datetime] = None
    stato: Optional[TireStatus] = None
    posizione_deposito: Optional[str] = Field(None, max_length=50)
    posizione: Optional[TirePosition] = None
    condizione: Optional[TireCondition] = None
    profondita_battistrada: Optional[int] = Field(None, ge=0, le=20)
    data_produzione: Optional[datetime] = None
    data_ultima_rotazione: Optional[datetime] = None
    km_ultima_rotazione: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None


class TireInDBBase(TireBase):
    """Base schema for tire in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class Tire(TireInDBBase):
    """Schema for tire response"""
    giorni_al_cambio: Optional[int] = None
    eta_mesi_dalla_produzione: Optional[float] = None
    
    @validator('giorni_al_cambio', always=True)
    def calculate_giorni_cambio(cls, v, values):
        if 'data_prossimo_cambio' in values and values['data_prossimo_cambio']:
            today = datetime.utcnow()
            delta = values['data_prossimo_cambio'] - today
            return delta.days
        return None
    
    @validator('eta_mesi_dalla_produzione', always=True)
    def calculate_eta_produzione(cls, v, values):
        if 'manufacture_date' in values and values['manufacture_date']:
            today = datetime.utcnow()
            delta = today - values['manufacture_date']
            return delta.days / 30.44
        return None
    
    class Config:
        from_attributes = True


class TireWithVehicle(Tire):
    """Schema for tire with vehicle info"""
    vehicle: Optional['Vehicle'] = None


class TireSet(BaseModel):
    """Schema for a set of tires"""
    vehicle_id: int
    tipo_stagione: TireSeason
    tires: List[Tire]
    data_ultimo_cambio: Optional[datetime] = None
    km_al_cambio: Optional[int] = None
    
    class Config:
        from_attributes = True


class TireRotationRequest(BaseModel):
    """Schema for tire rotation request"""
    vehicle_id: int
    current_km: int = Field(..., ge=0, description="Current vehicle kilometers")
    pattern: Optional[str] = Field(None, description="Rotation pattern: FORWARD_CROSS, REARWARD_CROSS, X_PATTERN, STRAIGHT")
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# Aliases for endpoint compatibility
TireResponse = Tire
