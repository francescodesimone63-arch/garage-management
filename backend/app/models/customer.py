"""
Customer model for client management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False, default='privato')  # privato | azienda
    nome = Column(String(100))
    cognome = Column(String(100))
    ragione_sociale = Column(String(200))
    codice_fiscale = Column(String(16))
    partita_iva = Column(String(11))
    telefono = Column(String(20), index=True)
    cellulare = Column(String(20))
    email = Column(String(100), index=True)
    indirizzo = Column(Text)
    citta = Column(String(100))
    cap = Column(String(10))
    provincia = Column(String(2))
    preferenze_notifica = Column(JSON)  # {"email": true, "sms": false, "whatsapp": true}
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="customer")
    car_assignments = relationship("CarAssignment", back_populates="customer")
    documents = relationship("Document", back_populates="customer")
    
    def __repr__(self):
        if self.ragione_sociale:
            return f"<Customer(ragione_sociale='{self.ragione_sociale}')>"
        return f"<Customer(nome='{self.nome}', cognome='{self.cognome}')>"
    
    @property
    def full_name(self):
        """Get full name or business name"""
        if self.ragione_sociale:
            return self.ragione_sociale
        return f"{self.nome or ''} {self.cognome or ''}".strip()