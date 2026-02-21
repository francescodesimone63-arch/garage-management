"""
User schemas for API requests and responses
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)  # Changed from EmailStr to accept .local domains
    nome: str = Field(..., min_length=1, max_length=100)
    cognome: str = Field(..., min_length=1, max_length=100)
    ruolo: str = Field(..., pattern="^(ADMIN|GENERAL_MANAGER|WORKSHOP|BODYSHOP|GM|CMM|CBM)$")
    telefono: Optional[str] = Field(None, max_length=20)
    attivo: bool = True


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=5, max_length=12)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cognome: Optional[str] = Field(None, min_length=1, max_length=100)
    ruolo: Optional[str] = Field(None, pattern="^(ADMIN|GENERAL_MANAGER|WORKSHOP|BODYSHOP)$")
    telefono: Optional[str] = Field(None, max_length=20)
    attivo: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=5, max_length=12)
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not any(char.isdigit() for char in v):
                raise ValueError('Password must contain at least one digit')
            if not any(char.isupper() for char in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(char.islower() for char in v):
                raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserInDBBase(UserBase):
    """Base schema for user in database"""
    id: int
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for user response"""
    pass


class UserResponse(BaseModel):
    """Schema for user response - TUTTO IN ITALIANO"""
    id: int
    email: str
    username: str
    nome: str
    cognome: str
    ruolo: str
    attivo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserInDBBase):
    """Schema for user in database with password"""
    password_hash: str


class Token(BaseModel):
    """Token response schema with permissions"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserResponse] = None
    permissions: Optional[list[str]] = None  # List of permission codes
    user: "UserResponse"


class LoginRequest(BaseModel):
    """Login request schema - accetta JSON"""
    # Accetta sia "username" che "email" come chiave JSON.
    # Grazie all'alias, il backend continua a usare l'attributo `username`,
    # ma una richiesta con body {"email": "..."} funziona comunque.
    model_config = ConfigDict(populate_by_name=True)
    username: str = Field(
        ...,
        alias="email",
        description="Email o username",
    )
    password: str = Field(..., description="Password")


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v