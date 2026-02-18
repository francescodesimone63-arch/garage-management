"""
Courtesy car models for managing loaner vehicles
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ContractType(str, enum.Enum):
    """Contract type enumeration"""
    LEASING = "leasing"
    AFFITTO = "affitto"
    PROPRIETA = "proprieta"


class CourtesyCarStatus(str, enum.Enum):
    """Courtesy car status enumeration"""
    DISPONIBILE = "disponibile"
    ASSEGNATA = "assegnata"
    MANUTENZIONE = "manutenzione"
    FUORI_SERVIZIO = "fuori_servizio"


class AssignmentStatus(str, enum.Enum):
    """Assignment status enumeration"""
    PRENOTATA = "prenotata"
    IN_CORSO = "in_corso"
    COMPLETATA = "completata"
    ANNULLATA = "annullata"


class CourtesyCar(Base):
    """Courtesy car model"""
    __tablename__ = "courtesy_cars"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), unique=True, nullable=False)
    contratto_tipo = Column(Enum(ContractType), nullable=False)
    fornitore_contratto = Column(String(200))
    data_inizio_contratto = Column(Date)
    data_scadenza_contratto = Column(Date)
    canone_mensile = Column(DECIMAL(10, 2))
    km_inclusi_anno = Column(Integer)
    stato = Column(Enum(CourtesyCarStatus), default=CourtesyCarStatus.DISPONIBILE, index=True)
    note = Column(String)
    contratto_firmato = Column(String(500))  # Path al file PDF
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="courtesy_car_rel")
    assignments = relationship("CarAssignment", back_populates="courtesy_car")
    
    def __repr__(self):
        return f"<CourtesyCar(vehicle_id={self.vehicle_id}, stato='{self.stato}')>"


class CarAssignment(Base):
    """Car assignment model for tracking courtesy car usage"""
    __tablename__ = "car_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    courtesy_car_id = Column(Integer, ForeignKey("courtesy_cars.id"), nullable=False)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    data_inizio = Column(DateTime(timezone=True), nullable=False, index=True)
    data_fine_prevista = Column(DateTime(timezone=True), nullable=False, index=True)
    data_fine_effettiva = Column(DateTime(timezone=True))
    km_inizio = Column(Integer)
    km_fine = Column(Integer)
    stato = Column(Enum(AssignmentStatus), default=AssignmentStatus.PRENOTATA)
    note = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    courtesy_car = relationship("CourtesyCar", back_populates="assignments")
    work_order = relationship("WorkOrder", back_populates="car_assignment")
    customer = relationship("Customer", back_populates="car_assignments")
    
    def __repr__(self):
        return f"<CarAssignment(courtesy_car_id={self.courtesy_car_id}, stato='{self.stato}')>"