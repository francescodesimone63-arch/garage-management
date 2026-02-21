"""
Endpoint per autenticazione e gestione accessi
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    OAuth2 compatible token login - ottieni access token + permessi
    """
    # Cerca utente per email O username
    from sqlalchemy import or_
    user = db.query(User).filter(
        or_(
            User.email == login_data.username,
            User.username == login_data.username
        )
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica password
    if not security.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password non corretti",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica che l'utente sia attivo
    if not user.attivo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente disattivato"
        )
    
    # Crea access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Aggiorna last_login
    from datetime import datetime as dt
    user.ultimo_accesso = dt.utcnow()
    db.commit()
    
    # Ottieni i permessi dell'utente
    from app.models import Permission, RolePermission
    from app.models.user import UserRole
    
    permissions = []
    if user.ruolo == UserRole.ADMIN:
        # Admin ha tutti i permessi
        perms = db.query(Permission).filter(Permission.attivo == True).all()
        permissions = [p.codice for p in perms]
    else:
        # Prendi i permessi concessi
        perms = db.query(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.ruolo == user.ruolo.value,
            RolePermission.granted == True
        ).all()
        permissions = [p.codice for p in perms]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": UserResponse.from_orm(user),
        "permissions": permissions
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Registrazione nuovo utente
    """
    # Verifica che l'email non sia già usata
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utente con questa email esiste già"
        )
    
    # Verifica che lo username non sia già usato
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo username è già in uso"
        )
    
    # Crea nuovo utente
    user = User(
        email=user_in.email,
        username=user_in.username,
        nome=user_in.nome,
        cognome=user_in.cognome,
        password_hash=security.get_password_hash(user_in.password),
        ruolo=user_in.ruolo,
        attivo=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Rinnova access token con permessi aggiornati
    """
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = security.create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    
    # Ottieni i permessi dell'utente (aggiornati)
    from app.models import Permission, RolePermission
    from app.models.user import UserRole
    
    permissions = []
    if current_user.ruolo == UserRole.ADMIN:
        # Admin ha tutti i permessi
        perms = db.query(Permission).filter(Permission.attivo == True).all()
        permissions = [p.codice for p in perms]
    else:
        # Prendi i permessi concessi
        perms = db.query(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.ruolo == current_user.ruolo.value,
            RolePermission.granted == True
        ).all()
        permissions = [p.codice for p in perms]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "user": UserResponse.from_orm(current_user),
        "permissions": permissions
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout utente (placeholder - con JWT stateless)
    In produzione implementare token blacklist
    """
    return {"message": "Logout effettuato con successo"}


@router.post("/password-reset")
def password_reset(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Richiesta reset password - invia email con token
    TODO: Implementare invio email
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Non rivelare se l'email esiste o meno per sicurezza
        return {"message": "Se l'email esiste, riceverai le istruzioni per il reset"}
    
    # TODO: Generare token reset e inviare email
    # Per ora solo placeholder
    
    return {"message": "Se l'email esiste, riceverai le istruzioni per il reset"}


@router.post("/password-reset-confirm")
def password_reset_confirm(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Conferma reset password con token
    TODO: Implementare validazione token
    """
    # TODO: Validare token e aggiornare password
    return {"message": "Password aggiornata con successo"}


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni informazioni utente corrente
    """
    return current_user
