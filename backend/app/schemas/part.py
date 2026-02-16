"""
Part schemas for API requests and responses
ALLINEATO AL MODELLO DATABASE
"""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from app.schemas.work_order import WorkOrder


class PartBase(BaseModel):
    """Base part schema - ALLINEATO AL MODELLO DATABASE"""
    codice: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    descrizione: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=100)
    modello: Optional[str] = Field(None, max_length=100)
    quantita: Decimal = Field(default=0, ge=0)
    quantita_minima: Decimal = Field(default=5, ge=0)
    prezzo_acquisto: Optional[Decimal] = Field(None, ge=0)
    prezzo_vendita: Optional[Decimal] = Field(None, ge=0)
    fornitore: Optional[str] = Field(None, max_length=200)
    posizione_magazzino: Optional[str] = Field(None, max_length=100)
    tipo: str = Field(default="ricambio", pattern="^(ricambio|fornitura)$")
    unita_misura: Optional[str] = Field(default="pz", max_length=10)
    note: Optional[str] = None


class PartCreate(PartBase):
    """Schema for creating a part - ALLINEATO AL MODELLO"""
    pass


class PartUpdate(BaseModel):
    """Schema for updating a part - CAMPI TUTTI OPZIONALI"""
    codice: Optional[str] = Field(None, min_length=1, max_length=50)
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descrizione: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=100)
    modello: Optional[str] = Field(None, max_length=100)
    quantita: Optional[Decimal] = Field(None, ge=0)
    quantita_minima: Optional[Decimal] = Field(None, ge=0)
    prezzo_acquisto: Optional[Decimal] = Field(None, ge=0)
    prezzo_vendita: Optional[Decimal] = Field(None, ge=0)
    fornitore: Optional[str] = Field(None, max_length=200)
    posizione_magazzino: Optional[str] = Field(None, max_length=100)
    tipo: Optional[str] = Field(None, pattern="^(ricambio|fornitura)$")
    unita_misura: Optional[str] = Field(None, max_length=10)
    note: Optional[str] = None


class PartInDBBase(PartBase):
    """Base schema for part in database"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Part(PartInDBBase):
    """Schema for part response"""
    class Config:
        from_attributes = True


class PartWithWorkOrder(Part):
    """Schema for part with work order info"""
    work_order: Optional['WorkOrder'] = None


class PartInventory(BaseModel):
    """Schema for part inventory tracking"""
    id: int
    codice: str
    nome: str
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    quantita: Decimal
    quantita_minima: Decimal
    prezzo_acquisto: Optional[Decimal] = None
    prezzo_vendita: Optional[Decimal] = None
    fornitore: Optional[str] = None
    
    class Config:
        from_attributes = True


# Alias per compatibilità con gli endpoint
PartResponse = Part
PartInDB = Part


class PartWithStats(Part):
    """Schema for part with usage statistics"""
    total_used: Decimal = 0
    work_orders_count: int = 0
    inventory_value: float = 0.0
    turnover_rate: float = 0.0


class PartInventoryItem(BaseModel):
    """Schema for inventory item with alert status - ALLINEATO AL MODELLO"""
    id: int
    codice: str
    nome: str
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    quantita: Decimal
    quantita_minima: Decimal
    prezzo_acquisto: Optional[Decimal] = None
    prezzo_vendita: Optional[Decimal] = None
    fornitore: Optional[str] = None
    alert_status: str  # 'ok', 'low', 'out'
    needs_reorder: bool
    
    class Config:
        from_attributes = True
