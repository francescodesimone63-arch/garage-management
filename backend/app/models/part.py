"""
Part and stock movement models for inventory management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PartType(str, enum.Enum):
    """Part type enumeration"""
    RICAMBIO = "ricambio"
    FORNITURA = "fornitura"


class MovementType(str, enum.Enum):
    """Stock movement type enumeration"""
    CARICO = "carico"
    SCARICO = "scarico"
    RETTIFICA = "rettifica"


class Part(Base):
    """Part model for inventory"""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True, index=True)
    codice = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    descrizione = Column(Text)
    categoria = Column(String(100), index=True)
    marca = Column(String(100))
    modello = Column(String(100))
    quantita = Column(DECIMAL(10, 2), default=0, index=True)
    quantita_minima = Column(DECIMAL(10, 2), default=5)
    prezzo_acquisto = Column(DECIMAL(10, 2))
    prezzo_vendita = Column(DECIMAL(10, 2))
    fornitore = Column(String(200))
    posizione_magazzino = Column(String(100))
    tipo = Column(Enum(PartType), default=PartType.RICAMBIO)
    unita_misura = Column(String(10), default="pz")
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    work_order_parts = relationship("WorkOrderPart", back_populates="part")
    stock_movements = relationship("StockMovement", back_populates="part", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Part(codice='{self.codice}', nome='{self.nome}')>"
    
    @property
    def is_low_stock(self):
        """Check if part is below minimum quantity"""
        return self.quantita < self.quantita_minima


class StockMovement(Base):
    """Stock movement model for tracking inventory changes"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    tipo = Column(Enum(MovementType), nullable=False)
    quantita = Column(DECIMAL(10, 2), nullable=False)
    quantita_precedente = Column(DECIMAL(10, 2))
    quantita_nuova = Column(DECIMAL(10, 2))
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    data_movimento = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    note = Column(Text)
    utente_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    part = relationship("Part", back_populates="stock_movements")
    work_order = relationship("WorkOrder")
    user = relationship("User")
    
    def __repr__(self):
        return f"<StockMovement(part_id={self.part_id}, tipo='{self.tipo}', quantita={self.quantita})>"