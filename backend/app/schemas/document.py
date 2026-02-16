"""
Document schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.document import DocumentType

if TYPE_CHECKING:
    from app.schemas.customer import Customer
    from app.schemas.work_order import WorkOrder
    from app.schemas.user import User
else:
    Customer = Any
    WorkOrder = Any
    User = Any


class DocumentBase(BaseModel):
    """Base document schema"""
    tipo: DocumentType
    numero: str = Field(..., min_length=1, max_length=50)
    data_documento: datetime
    customer_id: Optional[int] = None
    work_order_id: Optional[int] = None
    descrizione: Optional[str] = None
    importo_totale: Optional[float] = Field(None, ge=0)
    doc_metadata: Optional[Dict[str, Any]] = None
    
    @validator('numero')
    def validate_numero(cls, v, values):
        # Format based on document type
        if 'tipo' in values:
            tipo = values['tipo']
            if tipo == DocumentType.FATTURA:
                # Ensure fattura number format (e.g., "2024/001")
                if '/' not in v:
                    raise ValueError('Numero fattura deve contenere anno/numero')
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    file_path: Optional[str] = Field(None, max_length=500)
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    tipo: Optional[DocumentType] = None
    numero: Optional[str] = Field(None, min_length=1, max_length=50)
    data_documento: Optional[datetime] = None
    customer_id: Optional[int] = None
    work_order_id: Optional[int] = None
    descrizione: Optional[str] = None
    importo_totale: Optional[float] = Field(None, ge=0)
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentInDBBase(DocumentBase):
    """Base schema for document in database"""
    id: int
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class Document(DocumentInDBBase):
    """Schema for document response"""
    file_size_mb: Optional[float] = None
    is_pdf: bool = False
    has_file: bool = False
    
    @validator('file_size_mb', always=True)
    def calculate_size_mb(cls, v, values):
        if 'file_size' in values and values['file_size']:
            return round(values['file_size'] / (1024 * 1024), 2)
        return None
    
    @validator('is_pdf', always=True)
    def check_is_pdf(cls, v, values):
        if 'mime_type' in values and values['mime_type']:
            return values['mime_type'] == 'application/pdf'
        return False
    
    @validator('has_file', always=True)
    def check_has_file(cls, v, values):
        return bool(values.get('file_path'))
    
    class Config:
        from_attributes = True


class DocumentWithRelations(Document):
    """Schema for document with related entities"""
    customer: Optional['Customer'] = None
    work_order: Optional['WorkOrder'] = None
    creator: Optional['User'] = None


class DocumentUpload(BaseModel):
    """Schema for document upload"""
    document_id: int
    file_name: str
    file_size: int
    mime_type: str


class DocumentFilter(BaseModel):
    """Schema for document filtering"""
    tipo: Optional[DocumentType] = None
    customer_id: Optional[int] = None
    work_order_id: Optional[int] = None
    data_da: Optional[datetime] = None
    data_a: Optional[datetime] = None
    importo_min: Optional[float] = None
    importo_max: Optional[float] = None
    cerca_testo: Optional[str] = None
    
    @validator('data_a')
    def validate_date_range(cls, v, values):
        if v and 'data_da' in values and values['data_da'] and v < values['data_da']:
            raise ValueError('Data a deve essere dopo data da')
        return v


class DocumentStats(BaseModel):
    """Schema for document statistics"""
    totale_documenti: int
    per_tipo: Dict[str, int]
    totale_fatturato: float
    documenti_questo_mese: int
    spazio_utilizzato_mb: float
    
    class Config:
        from_attributes = True


class DocumentTemplate(BaseModel):
    """Schema for document template"""
    tipo: DocumentType
    nome_template: str
    contenuto_html: str
    variabili_disponibili: List[str]
    is_default: bool = False


# Aliases for endpoint compatibility
DocumentResponse = Document
DocumentWithDetails = DocumentWithRelations
