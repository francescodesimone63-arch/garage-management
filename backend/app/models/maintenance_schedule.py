"""
Maintenance schedule model for vehicle maintenance tracking
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MaintenanceType(str, enum.Enum):
    """Maintenance type enumeration"""
    ORDINARIA = "ordinaria"
    STRAORDINARIA = "straordinaria"


class MaintenanceStatus(str, enum.Enum):
    """Maintenance status enumeration"""
    ATTIVA = "attiva"
    COMPLETATA = "completata"
    ANNULLATA = "annullata"


class MaintenanceSchedule(Base):
    """Maintenance schedule model"""
    __tablename__ = "maintenance_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum(MaintenanceType), nullable=False)
    descrizione = Column(Text, nullable=False)
    km_scadenza = Column(Integer)
    data_scadenza = Column(Date, index=True)
    km_preavviso = Column(Integer, default=1000)
    giorni_preavviso = Column(Integer, default=30)
    stato = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.ATTIVA, index=True)
    ricorrente = Column(Boolean, default=False)
    intervallo_km = Column(Integer)
    intervallo_giorni = Column(Integer)
    ultima_notifica = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_schedules")
    
    def __repr__(self):
        return f"<MaintenanceSchedule(vehicle_id={self.vehicle_id}, tipo='{self.tipo}', stato='{self.stato}')>"