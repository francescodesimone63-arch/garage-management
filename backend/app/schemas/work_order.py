"""
Work order schemas for API requests and responses

BUSINESS RULE - APPROVAZIONE OBBLIGATORIA:
Tutte le schede lavoro richiedono approvazione del Garage Manager (GM).
Il workflow prevede:
1. Creazione scheda in stato BOZZA
2. Approvazione obbligatoria da parte del GM
3. Solo dopo l'approvazione la scheda passa a APPROVATA e può essere pianificata
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.work_order import WorkOrderStatus
from app.schemas.intervention import Intervention


class WorkOrderBase(BaseModel):
    """Base work order schema - ALLINEATO AL MODEL DATABASE"""
    vehicle_id: int
    customer_id: int
    numero_scheda: Optional[str] = Field(None, min_length=1, max_length=20, description="Generato automaticamente dal sistema")
    data_compilazione: Optional[datetime] = Field(None, description="Data compilazione scheda (opzionale - usa server default se non fornito)")
    data_appuntamento: Optional[datetime] = None
    data_fine_prevista: Optional[datetime] = None
    data_completamento: Optional[datetime] = None
    priorita: Optional[str] = Field('media', max_length=20)
    valutazione_danno: str
    sinistro: Optional[bool] = Field(False, description="Se è un sinistro assicurativo")
    ramo_sinistro_id: Optional[int] = None
    legale: Optional[str] = None
    autorita: Optional[str] = None
    numero_sinistro: Optional[str] = None
    compagnia_sinistro: Optional[str] = None
    compagnia_debitrice_sinistro: Optional[str] = None
    scoperto: Optional[float] = Field(None, ge=0)
    perc_franchigia: Optional[float] = Field(None, ge=0, le=100)
    stato: WorkOrderStatus = WorkOrderStatus.BOZZA
    creato_da: Optional[int] = None
    approvato_da: Optional[int] = None
    auto_cortesia_id: Optional[int] = None
    costo_stimato: Optional[float] = Field(None, ge=0)
    costo_finale: Optional[float] = Field(None, ge=0)
    
    @staticmethod
    def parse_datetime_flexible(v):
        """Parse datetime in multiple formats"""
        if v is None or v == '':
            return None
        
        if isinstance(v, datetime):
            return v
        
        if isinstance(v, str):
            # Prova vari formati
            formats = [
                '%Y-%m-%d',           # YYYY-MM-DD
                '%Y-%m-%dT%H:%M:%S',  # ISO senza timezone
                '%Y-%m-%d %H:%M:%S',  # YYYY-MM-DD HH:MM:SS
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
        
        return v
    
    @validator('data_compilazione', pre=True)
    def parse_data_compilazione(cls, v):
        return cls.parse_datetime_flexible(v)
    
    @validator('data_appuntamento', pre=True)
    def parse_data_appuntamento(cls, v):
        return cls.parse_datetime_flexible(v)
    
    @validator('data_fine_prevista', 'data_completamento', pre=True)
    def parse_optional_dates(cls, v):
        return cls.parse_datetime_flexible(v)




class WorkOrderCreate(WorkOrderBase):
    """Schema for creating a work order"""
    pass


class WorkOrderUpdate(BaseModel):
    """Schema for updating a work order - ALLINEATO AL MODEL DATABASE"""
    data_appuntamento: Optional[datetime] = None
    data_fine_prevista: Optional[datetime] = None
    data_completamento: Optional[datetime] = None
    priorita: Optional[str] = Field(None, max_length=20)
    valutazione_danno: Optional[str] = None
    sinistro: Optional[bool] = None
    ramo_sinistro_id: Optional[int] = None
    legale: Optional[str] = None
    autorita: Optional[str] = None
    numero_sinistro: Optional[str] = None
    compagnia_sinistro: Optional[str] = None
    compagnia_debitrice_sinistro: Optional[str] = None
    scoperto: Optional[float] = Field(None, ge=0)
    perc_franchigia: Optional[float] = Field(None, ge=0, le=100)
    stato: Optional[WorkOrderStatus] = None
    approvato_da: Optional[int] = None
    auto_cortesia_id: Optional[int] = None
    costo_stimato: Optional[float] = Field(None, ge=0)
    costo_finale: Optional[float] = Field(None, ge=0)
    
    @staticmethod
    def parse_datetime_flexible(v):
        """Parse datetime in multiple formats"""
        if v is None or v == '':
            return None
        
        if isinstance(v, datetime):
            return v
        
        if isinstance(v, str):
            # Prova vari formati
            formats = [
                '%Y-%m-%d',           # YYYY-MM-DD
                '%Y-%m-%dT%H:%M:%S',  # ISO senza timezone
                '%Y-%m-%d %H:%M:%S',  # YYYY-MM-DD HH:MM:SS
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
        
        return v
    
    @validator('data_appuntamento', 'data_fine_prevista', 'data_completamento', pre=True)
    def parse_dates(cls, v):
        return cls.parse_datetime_flexible(v)


class WorkOrderInDBBase(WorkOrderBase):
    """Base schema for work order in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    interventions: List[Intervention] = []  # Interventions caricate da GET /{id}
    
    class Config:
        from_attributes = True
        use_enum_values = True


class WorkOrder(WorkOrderInDBBase):
    """Schema for work order response"""
    parts_count: Optional[int] = 0
    labor_hours: Optional[float] = 0
    total_parts_cost: Optional[float] = 0
    total_labor_cost: Optional[float] = 0
    
    class Config:
        from_attributes = True


# Alias for compatibility
WorkOrderResponse = WorkOrder


class WorkOrderWithDetails(WorkOrder):
    """Schema for work order with full details"""
    customer: Optional['Customer'] = None
    vehicle: Optional['Vehicle'] = None
    technician: Optional['User'] = None
    parts: List['Part'] = []
    interventions: List[Any] = []  # Will be populated with Intervention objects at runtime


class WorkOrderSummary(BaseModel):
    """Schema for work order summary"""
    id: int
    numero_ordine: str
    data_ingresso: datetime
    stato: WorkOrderStatus
    customer_name: str
    vehicle_info: str
    importo_finale: Optional[float] = None
    
    class Config:
        from_attributes = True


class WorkOrderStats(BaseModel):
    """Schema for work order statistics"""
    total_orders: int
    open_orders: int
    in_progress_orders: int
    completed_orders: int
    average_completion_time: Optional[float] = None  # in days
    total_revenue: float
    average_order_value: float
    
    class Config:
        from_attributes = True