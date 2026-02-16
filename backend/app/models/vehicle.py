"""
Vehicle model for managing cars (customer and courtesy)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class VehicleType(str, enum.Enum):
    """Vehicle type enumeration"""
    CLIENTE = "cliente"
    CORTESIA = "cortesia"


class Vehicle(Base):
    """Vehicle model"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    targa = Column(String(10), unique=True, nullable=False, index=True)
    telaio = Column(String(17))
    marca = Column(String(50))
    modello = Column(String(50))
    anno = Column(Integer)
    colore = Column(String(30))
    
    # Dati tecnici (da verifica targa)
    cilindrata = Column(String(20))  # es. "1598 cc"
    kw = Column(Integer)  # potenza in kW
    cv = Column(Integer)  # potenza in CV
    porte = Column(Integer)  # numero porte (3 o 5)
    carburante = Column(String(30))  # Benzina, Diesel, GPL, etc.
    prima_immatricolazione = Column(String(10))  # YYYY-MM-DD
    
    km_attuali = Column(Integer)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    tipo = Column(Enum(VehicleType), default=VehicleType.CLIENTE, index=True)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    work_orders = relationship("WorkOrder", back_populates="vehicle")
    tires = relationship("Tire", back_populates="vehicle", cascade="all, delete-orphan")
    courtesy_car = relationship("CourtesyCar", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    maintenance_schedules = relationship("MaintenanceSchedule", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle(targa='{self.targa}', tipo='{self.tipo}')>"
    
    @property
    def display_name(self):
        """Get display name for vehicle"""
        if self.marca and self.modello:
            return f"{self.marca} {self.modello} - {self.targa}"
        return self.targa