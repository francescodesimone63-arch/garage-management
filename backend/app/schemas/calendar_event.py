"""
Calendar event schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr

if TYPE_CHECKING:
    from app.schemas.work_order import WorkOrder
else:
    WorkOrder = Any


class CalendarEventBase(BaseModel):
    """Base calendar event schema"""
    work_order_id: int
    titolo: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = None
    data_inizio: datetime
    data_fine: datetime
    partecipanti: Optional[List[EmailStr]] = []
    
    @validator('data_fine')
    def validate_date_range(cls, v, values):
        if 'data_inizio' in values and v < values['data_inizio']:
            raise ValueError('Data fine deve essere dopo data inizio')
        return v


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a calendar event"""
    pass


class CalendarEventUpdate(BaseModel):
    """Schema for updating a calendar event"""
    titolo: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = None
    data_inizio: Optional[datetime] = None
    data_fine: Optional[datetime] = None
    partecipanti: Optional[List[EmailStr]] = None


class CalendarEventInDBBase(CalendarEventBase):
    """Base schema for calendar event in database"""
    id: int
    google_event_id: Optional[str] = None
    sincronizzato: bool = False
    ultima_sincronizzazione: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CalendarEvent(CalendarEventInDBBase):
    """Schema for calendar event response"""
    durata_ore: Optional[float] = None
    stato_sincronizzazione: str  # 'sincronizzato', 'non_sincronizzato', 'errore'
    
    @validator('durata_ore', always=True)
    def calculate_durata(cls, v, values):
        if 'data_inizio' in values and 'data_fine' in values:
            delta = values['data_fine'] - values['data_inizio']
            return delta.total_seconds() / 3600
        return None
    
    @validator('stato_sincronizzazione', always=True)
    def determine_stato_sync(cls, v, values):
        if values.get('sincronizzato'):
            return 'sincronizzato'
        elif values.get('google_event_id'):
            return 'errore'
        else:
            return 'non_sincronizzato'
    
    class Config:
        from_attributes = True


class CalendarEventWithWorkOrder(CalendarEvent):
    """Schema for calendar event with work order info"""
    work_order: Optional['WorkOrder'] = None


class CalendarEventSync(BaseModel):
    """Schema for calendar sync request"""
    event_ids: Optional[List[int]] = None  # If None, sync all
    force_sync: bool = False


class CalendarEventSyncResult(BaseModel):
    """Schema for calendar sync result"""
    total_events: int
    synced_successfully: int
    sync_errors: int
    error_details: Optional[List[Dict[str, Any]]] = []


class GoogleCalendarConfig(BaseModel):
    """Schema for Google Calendar configuration"""
    calendar_id: str
    credentials_json: Dict[str, Any]
    sync_enabled: bool = True
    default_reminder_minutes: int = 60


class CalendarEventReminder(BaseModel):
    """Schema for event reminder"""
    event_id: int
    reminder_type: str  # 'email', 'popup'
    minutes_before: int = Field(..., ge=0, le=40320)  # Max 4 weeks
    
    @validator('reminder_type')
    def validate_reminder_type(cls, v):
        if v not in ['email', 'popup']:
            raise ValueError('Tipo reminder deve essere email o popup')
        return v


class CalendarView(BaseModel):
    """Schema for calendar view request"""
    start_date: datetime
    end_date: datetime
    user_ids: Optional[List[int]] = None
    include_completed: bool = False
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date deve essere dopo start date')
        # Max 3 months range
        if 'start_date' in values:
            delta = v - values['start_date']
            if delta.days > 90:
                raise ValueError('Range massimo 3 mesi')
        return v


# Aliases for endpoint compatibility
CalendarEventResponse = CalendarEvent
CalendarEventWithDetails = CalendarEventWithWorkOrder
