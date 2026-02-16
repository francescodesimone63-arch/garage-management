"""
Document model for managing various types of documents
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PREVENTIVO = "preventivo"
    FATTURA = "fattura"
    RICEVUTA = "ricevuta"
    CONTRATTO = "contratto"
    REPORT = "report"
    ALTRO = "altro"


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(DocumentType), nullable=False, index=True)
    numero = Column(String(50), unique=True, nullable=False, index=True)
    data_documento = Column(DateTime(timezone=True), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    work_order_id = Column(Integer, ForeignKey("work_orders.id", ondelete="SET NULL"))
    descrizione = Column(Text)
    importo_totale = Column(Float)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    doc_metadata = Column(Text)  # JSON field for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")
    work_order = relationship("WorkOrder", back_populates="documents")
    creator = relationship("User", back_populates="created_documents")
    
    def __repr__(self):
        return f"<Document(tipo={self.tipo}, numero='{self.numero}', customer_id={self.customer_id})>"