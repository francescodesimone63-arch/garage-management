"""
Calendar event model for Google Calendar integration
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class CalendarEvent(Base):
    """Calendar event model"""
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="CASCADE"), unique=True, nullable=False)
    google_event_id = Column(String(255), unique=True, index=True)
    titolo = Column(String(200), nullable=False)
    descrizione = Column(Text)
    data_inizio = Column(DateTime(timezone=True), nullable=False)
    data_fine = Column(DateTime(timezone=True), nullable=False)
    partecipanti = Column(Text)  # JSON array
    sincronizzato = Column(Boolean, default=False)
    ultima_sincronizzazione = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="calendar_event")
    
    def __repr__(self):
        return f"<CalendarEvent(work_order_id={self.work_order_id}, google_event_id='{self.google_event_id}')>"