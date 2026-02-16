"""
Notification model for tracking sent notifications
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, enum.Enum):
    """Notification status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    """Notification model"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(NotificationType), nullable=False, index=True)
    destinatario = Column(String(200), nullable=False)
    oggetto = Column(String(200))
    messaggio = Column(Text, nullable=False)
    stato = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    data_invio = Column(DateTime(timezone=True), index=True)
    errore = Column(Text)
    riferimento_tipo = Column(String(50))
    riferimento_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Notification(tipo='{self.tipo}', destinatario='{self.destinatario}', stato='{self.stato}')>"