"""
Customer schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, root_validator

# Import at runtime to allow Pydantic to resolve forward references
# Circular imports are OK here because we use forward references with strings
if TYPE_CHECKING:
    pass


class CustomerBase(BaseModel):
    """Base customer schema - VALIDAZIONI SEMPLIFICATE"""
    tipo: str = Field(..., min_length=1, max_length=50)  # Tipo dinamico da tabella di sistema
    nome: Optional[str] = Field(None, max_length=100)
    cognome: Optional[str] = Field(None, max_length=100)
    ragione_sociale: Optional[str] = Field(None, max_length=200)
    codice_fiscale: Optional[str] = Field(None, min_length=11, max_length=16)  # OPZIONALE
    partita_iva: Optional[str] = Field(None, min_length=11, max_length=11)
    indirizzo: Optional[str] = Field(None, max_length=200)
    citta: Optional[str] = Field(None, max_length=100)
    cap: Optional[str] = Field(None, max_length=5)  # Rimosso pattern rigido
    provincia: Optional[str] = Field(None, min_length=2, max_length=2)
    telefono: Optional[str] = Field(None, max_length=20)
    cellulare: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    note: Optional[str] = None
    
    @root_validator(skip_on_failure=True)
    def validate_tipo_fields(cls, values):
        """Valida campi in base al tipo cliente - MENO RIGIDA"""
        tipo = values.get('tipo', '').lower()
        if tipo == 'privato':
            # Per privati: almeno nome o cognome
            if not values.get('nome') and not values.get('cognome'):
                raise ValueError('Nome o cognome sono richiesti per clienti privati')
        elif tipo == 'azienda':
            # Per aziende: almeno ragione sociale
            if not values.get('ragione_sociale'):
                raise ValueError('Ragione sociale è obbligatoria per aziende')
        # Altri tipi (es. interno): almeno nome o cognome o ragione_sociale
        elif not values.get('nome') and not values.get('cognome') and not values.get('ragione_sociale'):
            raise ValueError('Almeno nome, cognome o ragione sociale sono richiesti')
        return values
    
    @validator('partita_iva')
    def validate_partita_iva(cls, v):
        """Valida partita IVA se fornita"""
        if v and not v.isdigit():
            raise ValueError('Partita IVA deve contenere solo numeri')
        return v
    
    @validator('codice_fiscale')
    def validate_codice_fiscale(cls, v):
        """Valida codice fiscale se fornito - SEMPLIFICATA"""
        if not v:
            return v
        
        # Converti in maiuscolo
        v = v.upper()
        
        # Validazione base lunghezza
        if len(v) not in [11, 16]:
            raise ValueError('Codice fiscale deve essere di 11 o 16 caratteri')
        
        return v


class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer - TUTTI CAMPI OPZIONALI"""
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    nome: Optional[str] = Field(None, max_length=100)
    cognome: Optional[str] = Field(None, max_length=100)
    ragione_sociale: Optional[str] = Field(None, max_length=200)
    codice_fiscale: Optional[str] = Field(None, min_length=11, max_length=16)
    partita_iva: Optional[str] = Field(None, min_length=11, max_length=11)
    indirizzo: Optional[str] = Field(None, max_length=200)
    citta: Optional[str] = Field(None, max_length=100)
    cap: Optional[str] = Field(None, max_length=5)
    provincia: Optional[str] = Field(None, min_length=2, max_length=2)
    telefono: Optional[str] = Field(None, max_length=20)
    cellulare: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    note: Optional[str] = None


class CustomerInDBBase(CustomerBase):
    """Base schema for customer in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Customer(CustomerInDBBase):
    """Schema for customer response"""
    vehicles_count: Optional[int] = 0
    work_orders_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Alias for compatibility
CustomerResponse = Customer


class CustomerWithVehicles(Customer):
    """Schema for customer with vehicles"""
    vehicles: List['Vehicle'] = []


class CustomerStats(BaseModel):
    """Schema for customer statistics"""
    customer_id: int
    vehicles_count: int
    work_orders_count: int
    total_spent: float
    
    class Config:
        from_attributes = True


class CustomerWithStats(Customer):
    """Schema for customer with extended statistics"""
    total_spent: Optional[float] = 0.0
    last_visit: Optional[datetime] = None
    average_order_value: Optional[float] = 0.0
