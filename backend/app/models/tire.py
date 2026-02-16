"""
Tire model for seasonal tire management
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TireSeason(str, enum.Enum):
    """Tire season enumeration"""
    ESTIVO = "estivo"
    INVERNALE = "invernale"


class TireStatus(str, enum.Enum):
    """Tire status enumeration"""
    DEPOSITATI = "depositati"
    MONTATI = "montati"


class TirePosition(str, enum.Enum):
    """Tire position enumeration"""
    ANTERIORE_SINISTRO = "anteriore_sinistro"
    ANTERIORE_DESTRO = "anteriore_destro"
    POSTERIORE_SINISTRO = "posteriore_sinistro"
    POSTERIORE_DESTRO = "posteriore_destro"
    RUOTA_DI_SCORTA = "ruota_di_scorta"


class TireCondition(str, enum.Enum):
    """Tire condition enumeration"""
    NUOVO = "nuovo"
    BUONO = "buono"
    DISCRETO = "discreto"
    USATO = "usato"
    CONSUNTO = "consunto"


class Tire(Base):
    """Tire model for seasonal tire storage"""
    __tablename__ = "tires"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    tipo_stagione = Column(Enum(TireSeason), nullable=False)
    marca = Column(String(50))
    modello = Column(String(50))
    misura = Column(String(30))
    data_deposito = Column(DateTime(timezone=True))
    data_ultimo_cambio = Column(DateTime(timezone=True))
    data_prossimo_cambio = Column(DateTime(timezone=True), index=True)
    stato = Column(Enum(TireStatus), default=TireStatus.DEPOSITATI)
    posizione_deposito = Column(String(50))
    note = Column(String)
    
    # Additional fields for tire management
    posizione = Column(Enum(TirePosition))
    condizione = Column(Enum(TireCondition), default=TireCondition.BUONO)
    profondita_battistrada = Column(Integer)  # in mm
    data_produzione = Column(DateTime(timezone=True))
    data_ultima_rotazione = Column(DateTime(timezone=True))
    km_ultima_rotazione = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="tires")
    
    def __repr__(self):
        return f"<Tire(vehicle_id={self.vehicle_id}, tipo_stagione='{self.tipo_stagione}', stato='{self.stato}')>"