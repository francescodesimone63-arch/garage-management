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


class InterventionStatusType(Base):
    """
    Intervention status type - dynamic lookup table
    
    Stati predefiniti:
    - preso_in_carico: L'intervento è in lavorazione
    - attesa_componente: È stato richiesto l'acquisto di un componente
    - sospeso: Intervento sospeso (richiede nota descrittiva)
    - concluso: L'intervento è stato completato
    """
    __tablename__ = "intervention_status_types"
    
    id = Column(Integer, primary_key=True, index=True)
    codice = Column(String(30), unique=True, nullable=False, index=True)
    nome = Column(String(50), nullable=False)
    descrizione = Column(Text)
    richiede_nota = Column(Boolean, default=False)  # True per stato "sospeso"
    attivo = Column(Boolean, default=True)
    ordine = Column(Integer, default=0)  # Per ordinamento visualizzazione
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<InterventionStatusType(id={self.id}, codice='{self.codice}', nome='{self.nome}')>"

class InsuranceBranchType(Base):
    """Insurance branch type - dynamic lookup table for claim branches"""
    __tablename__ = "insurance_branch_types"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    codice = Column(String(30), unique=True, nullable=False, index=True)
    descrizione = Column(Text)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<InsuranceBranchType(id={self.id}, nome='{self.nome}')>"