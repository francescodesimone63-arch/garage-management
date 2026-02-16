"""
System lookup tables models for master data management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class DamageType(Base):
    """Damage type enumeration - dynamic lookup table"""
    __tablename__ = "damage_types"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DamageType(id={self.id}, nome='{self.nome}')>"


class CustomerType(Base):
    """Customer type enumeration - dynamic lookup table"""
    __tablename__ = "customer_types"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CustomerType(id={self.id}, nome='{self.nome}')>"


class WorkOrderStatusType(Base):
    """Work order status type - dynamic lookup table"""
    __tablename__ = "work_order_status_types"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<WorkOrderStatusType(id={self.id}, nome='{self.nome}')>"


class PriorityType(Base):
    """Priority type - dynamic lookup table"""
    __tablename__ = "priority_types"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PriorityType(id={self.id}, nome='{self.nome}')>"
