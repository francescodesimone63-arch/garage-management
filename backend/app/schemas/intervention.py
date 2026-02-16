"""
Intervention (Intervento) schemas for API requests and responses
"""
from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class InterventionStatusTypeInline(BaseModel):
    """Schema inline per lo stato intervento"""
    id: int
    codice: str
    nome: str
    richiede_nota: bool
    
    class Config:
        from_attributes = True


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
    stato_intervento_id: Optional[int] = Field(None, description="ID dello stato intervento")
    note_intervento: Optional[str] = Field(None, max_length=2000, description="Note sull'intervento")
    
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
    stato_intervento_id: Optional[int] = Field(None, description="ID dello stato intervento")
    note_intervento: Optional[str] = Field(None, max_length=2000)
    note_sospensione: Optional[str] = Field(None, max_length=1000, description="Nota obbligatoria se stato = sospeso")
    ore_effettive: Optional[float] = Field(None, ge=0, le=1000)
    data_inizio: Optional[datetime] = None
    data_fine: Optional[datetime] = None
    
    @validator('tipo_intervento')
    def validate_tipo_intervento(cls, v):
        """Valida che il tipo sia uno di quelli consentiti"""
        if v is not None and v not in ['Meccanico', 'Carrozziere']:
            raise ValueError('tipo_intervento deve essere "Meccanico" o "Carrozziere"')
        return v


class InterventionStatusUpdate(BaseModel):
    """Schema per aggiornare solo lo stato di un intervento (per CMM/CBM)"""
    stato_intervento_id: int = Field(..., description="ID del nuovo stato")
    note_intervento: Optional[str] = Field(None, max_length=2000)
    note_sospensione: Optional[str] = Field(None, max_length=1000, description="Obbligatoria se stato = sospeso")


class InterventionInDBBase(BaseModel):
    """Base schema for intervention in database"""
    id: int
    work_order_id: int
    progressivo: int
    descrizione_intervento: str
    durata_stimata: float
    tipo_intervento: str
    stato_intervento_id: Optional[int]
    note_intervento: Optional[str]
    note_sospensione: Optional[str]
    ore_effettive: Optional[float]
    data_inizio: Optional[datetime]
    data_fine: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Intervention(InterventionInDBBase):
    """Schema for intervention response"""
    stato_intervento: Optional[InterventionStatusTypeInline] = None
