"""
Permission checking dependencies for FastAPI endpoints
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.rbac import Permission, RolePermission


def require_permission(permission_codice: str):
    """
    Factory che crea una dependency per verificare un permesso specifico.
    
    Uso:
    @router.post("/customers", dependencies=[Depends(require_permission("customers.create"))])
    def create_customer(data: CustomerCreate):
        ...
    """
    def check(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Se admin, consenti sempre (ADMIN ha tutti i permessi)
        if current_user.ruolo == "ADMIN":
            return current_user
        
        # Altrimenti verifica nel database
        result = db.query(RolePermission).join(
            Permission, RolePermission.permission_id == Permission.id
        ).filter(
            and_(
                RolePermission.ruolo == current_user.ruolo,
                Permission.codice == permission_codice,
                RolePermission.granted == True
            )
        ).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permesso negato: {permission_codice}"
            )
        
        return current_user
    
    return check


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifica che l'utente sia admin"""
    if current_user.ruolo != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin possono accedere a questa risorsa"
        )
    return current_user


def require_workshop_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifica che l'utente sia un manager di officina (CMM, CBM, GM)"""
    manager_roles = ["ADMIN", "GENERAL_MANAGER", "CMM", "CBM"]
    
    if current_user.ruolo not in manager_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo manager di officina possono accedere a questa risorsa"
        )
    return current_user


def require_workshop_permission(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifica che l'utente sia assegnato a un workshop (officina specifica)"""
    if not current_user.workshop_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non assegnato a nessun workshop"
        )
    return current_user
