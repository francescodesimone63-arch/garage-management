"""
Intervention (Intervento) schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class InterventionBase(BaseModel):
    """Base intervention schema"""
    progressivo: int = Field(..., ge=1, description="Progressivo dell'intervento (1, 2, 3...)")
    descrizione_intervento: str = Field(..., min_length=1, max_length=1000, description="Descrizione dell'intervento")
    durata_stimata: float = Field(0, ge=0, le=100, description="Durata stimata in ore (es: 1.5 per 1h30)")
    tipo_intervento: str = Field(..., description="Tipo intervento: 'Meccanico' o 'Carrozziere'")
    
    @validator('tipo_intervento')
    def validate_tipo_intervento(cls, v):
        """Valida che il tipo sia uno di quelli consentiti"""
        if v not in ['Meccanico', 'Carrozziere']:
            raise ValueError('tipo_intervento deve essere "Meccanico" o "Carrozziere"')
        return v


class InterventionCreate(BaseModel):
    """Schema for creating an intervention - progressivo is auto-calculated"""
    progressivo: Optional[int] = Field(None, ge=1, description="Progressivo dell'intervento (auto-calcolato se non fornito)")
    descrizione_intervento: str = Field(..., min_length=1, max_length=1000, description="Descrizione dell'intervento")
    durata_stimata: float = Field(0, ge=0, le=100, description="Durata stimata in ore (es: 1.5 per 1h30)")
    tipo_intervento: str = Field(..., description="Tipo intervento: 'Meccanico' o 'Carrozziere'")
    
    @validator('tipo_intervento')
    def validate_tipo_intervento(cls, v):
        """Valida che il tipo sia uno di quelli consentiti"""
        if v not in ['Meccanico', 'Carrozziere']:
            raise ValueError('tipo_intervento deve essere "Meccanico" o "Carrozziere"')
        return v


class InterventionUpdate(BaseModel):
    """Schema for updating an intervention"""
    progressivo: Optional[int] = Field(None, ge=1)
    descrizione_intervento: Optional[str] = Field(None, min_length=1, max_length=1000)
    durata_stimata: Optional[float] = Field(None, ge=0, le=100)
    tipo_intervento: Optional[str] = None
    
    @validator('tipo_intervento')
    def validate_tipo_intervento(cls, v):
        """Valida che il tipo sia uno di quelli consentiti"""
        if v is not None and v not in ['Meccanico', 'Carrozziere']:
            raise ValueError('tipo_intervento deve essere "Meccanico" o "Carrozziere"')
        return v


class InterventionInDBBase(InterventionBase):
    """Base schema for intervention in database"""
    id: int
    work_order_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Intervention(InterventionInDBBase):
    """Schema for intervention response"""
    pass
