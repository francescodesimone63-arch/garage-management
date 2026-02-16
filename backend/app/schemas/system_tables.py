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
