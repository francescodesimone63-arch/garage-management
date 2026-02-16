"""
Endpoint per gestione utenti
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_active_superuser
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core import security

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Ottieni lista utenti (solo admin/gm)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Crea nuovo utente (solo admin/gm)
    """
    # Verifica email univoca
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utente con questa email esiste già"
        )
    
    # Verifica username univoco
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Questo username è già in uso"
        )
    
    # Crea utente
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


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni informazioni utente corrente
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Aggiorna informazioni utente corrente
    """
    # Aggiorna solo i campi forniti
    if user_in.email is not None:
        # Verifica che l'email non sia già usata da altri
        existing = db.query(User).filter(
            User.email == user_in.email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questa email è già in uso"
            )
        current_user.email = user_in.email
    
    if user_in.username is not None:
        # Verifica che lo username non sia già usato da altri
        existing = db.query(User).filter(
            User.username == user_in.username,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo username è già in uso"
            )
        current_user.username = user_in.username
    
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    
    if user_in.password is not None:
        current_user.hashed_password = security.get_password_hash(user_in.password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Ottieni utente specifico per ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Solo admin/gm o l'utente stesso può vedere i dettagli
    if current_user.id != user_id and current_user.role not in ["admin", "gm"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """
    Aggiorna utente (solo admin/gm)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Aggiorna campi
    if user_in.email is not None:
        existing = db.query(User).filter(
            User.email == user_in.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questa email è già in uso"
            )
        user.email = user_in.email
    
    if user_in.username is not None:
        existing = db.query(User).filter(
            User.username == user_in.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questo username è già in uso"
            )
        user.username = user_in.username
    
    if user_in.nome is not None:
        user.nome = user_in.nome
    
    if user_in.cognome is not None:
        user.cognome = user_in.cognome
    
    if user_in.password is not None:
        user.password_hash = security.get_password_hash(user_in.password)
    
    if user_in.ruolo is not None:
        user.ruolo = user_in.ruolo
    
    if user_in.attivo is not None:
        user.attivo = user_in.attivo
    
    if user_in.telefono is not None:
        user.telefono = user_in.telefono
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """
    Elimina utente (solo admin/gm)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Non permettere eliminazione di se stessi
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi eliminare il tuo account"
        )
    
    db.delete(user)
    db.commit()
