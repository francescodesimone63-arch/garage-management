"""
Schemas for system lookup tables
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Damage Type Schemas
class DamageTypeCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descrizione: Optional[str] = None


class DamageTypeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descrizione: Optional[str] = None
    attivo: Optional[bool] = None


class DamageTypeResponse(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer Type Schemas
class CustomerTypeCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)
    descrizione: Optional[str] = None


class CustomerTypeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=50)
    descrizione: Optional[str] = None
    attivo: Optional[bool] = None


class CustomerTypeResponse(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Work Order Status Type Schemas
class WorkOrderStatusTypeCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)
    descrizione: Optional[str] = None


class WorkOrderStatusTypeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=50)
    descrizione: Optional[str] = None
    attivo: Optional[bool] = None


class WorkOrderStatusTypeResponse(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Priority Type Schemas
class PriorityTypeCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)
    descrizione: Optional[str] = None


class PriorityTypeUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=50)
    descrizione: Optional[str] = None
    attivo: Optional[bool] = None


class PriorityTypeResponse(BaseModel):
    id: int
    nome: str
    descrizione: Optional[str]
    attivo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Intervention Status Type Schemas
class InterventionStatusTypeCreate(BaseModel):
    codice: str = Field(..., min_length=1, max_length=30, description="Codice univoco (es: preso_in_carico)")
    nome: str = Field(..., min_length=1, max_length=50, description="Nome visualizzato (es: Preso in carico)")
    descrizione: Optional[str] = None
    richiede_nota: bool = Field(default=False, description="Se True, richiede nota obbligatoria")
    ordine: int = Field(default=0, description="Ordine di visualizzazione")


class InterventionStatusTypeUpdate(BaseModel):
    codice: Optional[str] = Field(None, min_length=1, max_length=30)
    nome: Optional[str] = Field(None, min_length=1, max_length=50)
    descrizione: Optional[str] = None
    richiede_nota: Optional[bool] = None
    attivo: Optional[bool] = None
    ordine: Optional[int] = None


class InterventionStatusTypeResponse(BaseModel):
    id: int
    codice: str
    nome: str
    descrizione: Optional[str]
    richiede_nota: bool
    attivo: bool
    ordine: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
