"""
Activity log schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, validator, IPvAnyAddress

if TYPE_CHECKING:
    from app.schemas.user import User
else:
    User = Any


class ActivityLogBase(BaseModel):
    """Base activity log schema"""
    azione: str = Field(..., min_length=1, max_length=100)
    entita: Optional[str] = Field(None, max_length=50)
    entita_id: Optional[int] = None
    descrizione: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    dettagli: Optional[Dict[str, Any]] = None
    
    @validator('entita')
    def validate_entita(cls, v):
        valid_entities = [
            'user', 'customer', 'vehicle', 'work_order', 
            'part', 'tire', 'courtesy_car', 'maintenance_schedule',
            'notification', 'calendar_event', 'document'
        ]
        if v and v not in valid_entities:
            raise ValueError(f'Entità deve essere una di: {", ".join(valid_entities)}')
        return v


class ActivityLogCreate(ActivityLogBase):
    """Schema for creating an activity log"""
    user_id: Optional[int] = None  # Can be None for system actions


class ActivityLogInDBBase(ActivityLogBase):
    """Base schema for activity log in database"""
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ActivityLog(ActivityLogInDBBase):
    """Schema for activity log response"""
    tempo_trascorso: Optional[str] = None
    
    @validator('tempo_trascorso', always=True)
    def calculate_tempo_trascorso(cls, v, values):
        if 'timestamp' in values:
            from datetime import datetime
            delta = datetime.now() - values['timestamp']
            
            if delta.days > 365:
                years = delta.days // 365
                return f"{years} anni fa"
            elif delta.days > 30:
                months = delta.days // 30
                return f"{months} mesi fa"
            elif delta.days > 0:
                return f"{delta.days} giorni fa"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} ore fa"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} minuti fa"
            else:
                return "Adesso"
        return None
    
    class Config:
        from_attributes = True


class ActivityLogWithUser(ActivityLog):
    """Schema for activity log with user info"""
    user: Optional['User'] = None


class ActivityLogFilter(BaseModel):
    """Schema for activity log filtering"""
    user_id: Optional[int] = None
    azione: Optional[str] = None
    entita: Optional[str] = None
    entita_id: Optional[int] = None
    data_da: Optional[datetime] = None
    data_a: Optional[datetime] = None
    ip_address: Optional[str] = None
    cerca_testo: Optional[str] = None
    
    @validator('data_a')
    def validate_date_range(cls, v, values):
        if v and 'data_da' in values and values['data_da'] and v < values['data_da']:
            raise ValueError('Data a deve essere dopo data da')
        return v


class ActivityLogStats(BaseModel):
    """Schema for activity log statistics"""
    totale_attivita: int
    attivita_oggi: int
    attivita_settimana: int
    attivita_mese: int
    per_azione: Dict[str, int]
    per_entita: Dict[str, int]
    utenti_attivi: int
    ore_piu_attive: List[Dict[str, Any]]  # [{"ora": 14, "count": 123}, ...]
    
    class Config:
        from_attributes = True


class ActivitySummary(BaseModel):
    """Schema for activity summary"""
    user_id: int
    username: str
    totale_azioni: int
    ultima_attivita: Optional[datetime] = None
    azioni_frequenti: List[str]
    entita_modificate: Dict[str, int]
    
    class Config:
        from_attributes = True


class AuditTrail(BaseModel):
    """Schema for audit trail of a specific entity"""
    entita: str
    entita_id: int
    storia_modifiche: List[ActivityLog]
    prima_creazione: Optional[datetime] = None
    ultima_modifica: Optional[datetime] = None
    totale_modifiche: int
    utenti_coinvolti: List[int]
    
    class Config:
        from_attributes = True


# Aliases for endpoint compatibility
ActivityLogResponse = ActivityLog
ActivityLogWithDetails = ActivityLogWithUser
