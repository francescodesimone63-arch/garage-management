"""
User model for authentication and authorization
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration"""
    ADMIN = "ADMIN"                    # Administrator
    GENERAL_MANAGER = "GENERAL_MANAGER"  # General Manager (GM)
    WORKSHOP = "WORKSHOP"                # Legacy - Meccanica
    BODYSHOP = "BODYSHOP"                # Legacy - Carrozzeria
    CMM = "CMM"                          # Capo Meccanica
    CBM = "CBM"                          # Capo Carrozzeria
    
    # Legacy alias for compatibility
    GM = "GENERAL_MANAGER"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    ruolo = Column(Enum(UserRole), nullable=False, index=True)
    nome = Column(String(100))
    cognome = Column(String(100))
    attivo = Column(Boolean, default=True)
    ultimo_accesso = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    created_documents = relationship("Document", back_populates="creator")
    activity_logs = relationship("ActivityLog", back_populates="user")
    
    # Properties for compatibility with English naming
    @property
    def role(self):
        """Alias for ruolo"""
        return self.ruolo
    
    @role.setter
    def role(self, value):
        self.ruolo = value
    
    @property
    def is_active(self):
        """Alias for attivo"""
        return self.attivo
    
    @is_active.setter
    def is_active(self, value):
        self.attivo = value
    
    @property
    def last_login(self):
        """Alias for ultimo_accesso"""
        return self.ultimo_accesso
    
    @last_login.setter
    def last_login(self, value):
        self.ultimo_accesso = value
    
    @property
    def full_name(self):
        """Get full name combining nome and cognome"""
        if self.nome and self.cognome:
            return f"{self.nome} {self.cognome}"
        elif self.nome:
            return self.nome
        elif self.cognome:
            return self.cognome
        return self.username
    
    @property
    def is_superuser(self):
        """Check if user is superuser (ADMIN)"""
        return self.ruolo == UserRole.ADMIN
    
    def __repr__(self):
        return f"<User(username='{self.username}', ruolo='{self.ruolo}')>"
