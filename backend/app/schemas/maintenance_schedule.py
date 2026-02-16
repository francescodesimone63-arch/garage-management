"""
Maintenance schedule schemas for API requests and responses
ALLINEATO AL MODELLO DATABASE
"""
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from app.models.maintenance_schedule import MaintenanceType, MaintenanceStatus

if TYPE_CHECKING:
    from app.schemas.vehicle import Vehicle
else:
    Vehicle = Any


class MaintenanceScheduleBase(BaseModel):
    """Base maintenance schedule schema - ALLINEATO AL MODELLO"""
    vehicle_id: int = Field(..., gt=0)
    tipo: MaintenanceType = Field(...)
    descrizione: str = Field(..., min_length=1, max_length=500)
    km_scadenza: Optional[int] = Field(None, ge=0)
    data_scadenza: Optional[date] = None
    km_preavviso: int = Field(default=1000, ge=0)
    giorni_preavviso: int = Field(default=30, ge=0)
    stato: MaintenanceStatus = MaintenanceStatus.ATTIVA
    ricorrente: bool = Field(default=False)
    intervallo_km: Optional[int] = Field(None, ge=0)
    intervallo_giorni: Optional[int] = Field(None, ge=0)
    ultima_notifica: Optional[datetime] = None
    
    @validator('data_scadenza')
    def validate_data_scadenza(cls, v):
        if v and v < date.today():
            raise ValueError('Data scadenza non può essere nel passato')
        return v
    
    @validator('intervallo_giorni')
    def validate_intervalli(cls, v, values):
        # At least one interval must be specified for recurring maintenance
        if values.get('ricorrente') and not v and not values.get('intervallo_km'):
            raise ValueError('Per manutenzione ricorrente, almen uno intervallo (km o giorni) deve essere specificato')
        return v


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    """Schema for creating a maintenance schedule"""
    pass


class MaintenanceScheduleUpdate(BaseModel):
    """Schema for updating a maintenance schedule"""
    tipo: Optional[MaintenanceType] = None
    descrizione: Optional[str] = Field(None, min_length=1, max_length=500)
    km_scadenza: Optional[int] = Field(None, ge=0)
    data_scadenza: Optional[date] = None
    km_preavviso: Optional[int] = Field(None, ge=0)
    giorni_preavviso: Optional[int] = Field(None, ge=0)
    stato: Optional[MaintenanceStatus] = None
    ricorrente: Optional[bool] = None
    intervallo_km: Optional[int] = Field(None, ge=0)
    intervallo_giorni: Optional[int] = Field(None, ge=0)
    ultima_notifica: Optional[datetime] = None


class MaintenanceScheduleInDBBase(MaintenanceScheduleBase):
    """Base schema for maintenance schedule in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class MaintenanceSchedule(MaintenanceScheduleInDBBase):
    """Schema for maintenance schedule response"""
    km_rimanenti: Optional[int] = None
    giorni_rimanenti: Optional[int] = None
    stato_scadenza: str = "ok"  # 'ok', 'prossima', 'scaduta'
    
    @validator('km_rimanenti', always=True)
    def calculate_km_rimanenti(cls, v, values):
        if 'km_scadenza' in values and values['km_scadenza']:
            # This would need current vehicle km from context
            return None  # Will be calculated in the service layer
        return None
    
    @validator('giorni_rimanenti', always=True)
    def calculate_giorni_rimanenti(cls, v, values):
        if 'data_scadenza' in values and values['data_scadenza']:
            today = date.today()
            delta = values['data_scadenza'] - today
            return delta.days
        return None
    
    @validator('stato_scadenza', always=True)
    def determine_stato(cls, v, values):
        giorni = values.get('giorni_rimanenti')
        if giorni is not None:
            if giorni < 0:
                return 'scaduta'
            elif giorni <= values.get('giorni_preavviso', 30):
                return 'prossima'
            else:
                return 'ok'
        return 'ok'
    
    class Config:
        from_attributes = True


class MaintenanceScheduleWithVehicle(MaintenanceSchedule):
    """Schema for maintenance schedule with vehicle info"""
    vehicle: Optional['Vehicle'] = None


class MaintenanceAlert(BaseModel):
    """Schema for maintenance alert"""
    id: int
    vehicle_id: int
    maintenance_type: str
    due_date: Optional[date] = None
    due_km: Optional[int] = None
    days_until_due: int = 0
    is_overdue: bool = False
    alert_level: str = "info"  # 'info', 'warning', 'critical'
    
    class Config:
        from_attributes = True


# Aliases for endpoint compatibility
MaintenanceScheduleResponse = MaintenanceSchedule
