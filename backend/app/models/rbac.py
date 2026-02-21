"""
RBAC (Role-Based Access Control) models
Defines permissions, role-permission mappings, and workshops
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.models.user import UserRole


class Workshop(Base):
    """Workshop/Officina model for multi-workshop support"""
    __tablename__ = "workshops"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # "meccanica" o "carrozzeria"
    responsabile_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    indirizzo = Column(Text, nullable=True)
    attivo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="workshop", foreign_keys="User.workshop_id")
    
    def __repr__(self):
        return f"<Workshop(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"


class Permission(Base):
    """Permission/Action model - catalog of available permissions"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    codice = Column(String(100), unique=True, nullable=False, index=True)  # es: "customers.create"
    nome = Column(String(200), nullable=False)  # es: "Crea Cliente"
    categoria = Column(String(50), nullable=False, index=True)  # es: "Clienti"
    descrizione = Column(Text, nullable=True)
    attivo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission(codice='{self.codice}', nome='{self.nome}')>"


class RolePermission(Base):
    """Role-Permission mapping - dynamic matrix of which roles have which permissions"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    ruolo = Column(String(50), nullable=False, index=True)  # es: "GM", "CMM", "ADMIN"
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    granted = Column(Boolean, default=True)  # True = concesso, False = negato
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Unique constraint: un permesso per un ruolo
    __table_args__ = (
        UniqueConstraint('ruolo', 'permission_id', name='uq_role_permission'),
    )
    
    # Relationships
    permission = relationship("Permission", back_populates="role_permissions")
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        status = "✅" if self.granted else "❌"
        return f"<RolePermission(ruolo='{self.ruolo}', permission_id={self.permission_id}, granted={status})>"
