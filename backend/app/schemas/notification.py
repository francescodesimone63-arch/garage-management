"""
Notification schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.notification import NotificationType

if TYPE_CHECKING:
    from app.schemas.user import User
else:
    User = Any


class NotificationBase(BaseModel):
    """Base notification schema"""
    user_id: int
    tipo: NotificationType
    titolo: str = Field(..., min_length=1, max_length=200)
    messaggio: str
    letta: bool = False
    priorita: str = Field(..., pattern="^(alta|media|bassa)$")
    link_azione: Optional[str] = Field(None, max_length=500)
    dati_aggiuntivi: Optional[Dict[str, Any]] = None
    
    @validator('link_azione')
    def validate_link(cls, v):
        if v and not (v.startswith('/') or v.startswith('http')):
            raise ValueError('Link deve iniziare con / o http')
        return v


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    letta: Optional[bool] = None
    priorita: Optional[str] = Field(None, pattern="^(alta|media|bassa)$")


class NotificationInDBBase(NotificationBase):
    """Base schema for notification in database"""
    id: int
    created_at: datetime
    data_lettura: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class Notification(NotificationInDBBase):
    """Schema for notification response"""
    tempo_trascorso: Optional[str] = None
    
    @validator('tempo_trascorso', always=True)
    def calculate_tempo_trascorso(cls, v, values):
        if 'created_at' in values:
            from datetime import datetime
            delta = datetime.now() - values['created_at']
            
            if delta.days > 0:
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


class NotificationWithUser(Notification):
    """Schema for notification with user info"""
    user: Optional['User'] = None


class NotificationBulkCreate(BaseModel):
    """Schema for creating multiple notifications"""
    user_ids: List[int]
    tipo: NotificationType
    titolo: str = Field(..., min_length=1, max_length=200)
    messaggio: str
    priorita: str = Field(..., pattern="^(alta|media|bassa)$")
    link_azione: Optional[str] = Field(None, max_length=500)
    dati_aggiuntivi: Optional[Dict[str, Any]] = None


class NotificationMarkRead(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: List[int]


class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    totali: int
    non_lette: int
    alta_priorita: int
    per_tipo: Dict[str, int]
    
    class Config:
        from_attributes = True


class NotificationPreferences(BaseModel):
    """Schema for user notification preferences"""
    user_id: int
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    tipi_abilitati: List[NotificationType] = []
    orario_non_disturbare_inizio: Optional[str] = None  # HH:MM format
    orario_non_disturbare_fine: Optional[str] = None  # HH:MM format
    
    @validator('orario_non_disturbare_inizio', 'orario_non_disturbare_fine')
    def validate_orario(cls, v):
        if v:
            try:
                hour, minute = v.split(':')
                if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                    raise ValueError
            except:
                raise ValueError('Formato orario non valido (HH:MM)')
        return v


# Aliases for endpoint compatibility
NotificationResponse = Notification
