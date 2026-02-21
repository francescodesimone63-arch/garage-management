"""
Endpoint per gestione permessi e ruoli
"""
from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_active_superuser
from app.core.permissions import require_permission
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/roles")
def get_roles(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Ottieni lista dei ruoli disponibili
    """
    # Ruoli disponibili (escludendo legacy si usa solo i moderni)
    roles = [
        {"label": "👤 Amministratore", "value": UserRole.ADMIN},
        {"label": "🏢 Direttore (GM)", "value": UserRole.GENERAL_MANAGER},
        {"label": "🤝 Assistente GM", "value": UserRole.GM_ASSISTANT},
        {"label": "🎯 Manager Front-End", "value": UserRole.FRONTEND_MANAGER},
        {"label": "🔧 Capo Officina CMM", "value": UserRole.CMM},
        {"label": "🚗 Capo Carrozzeria CBM", "value": UserRole.CBM},
        {"label": "⚙️ Operatore Officina", "value": UserRole.WORKSHOP},
        {"label": "🛠️ Operatore Carrozzeria", "value": UserRole.BODYSHOP},
    ]
    
    return {
        "roles": roles,
        "count": len(roles)
    }


@router.get("/me")
def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Ottieni i permessi dell'utente corrente
    """
    from app.models import Permission, RolePermission
    
    permissions = []
    
    if current_user.ruolo == UserRole.ADMIN:
        # Admin ha tutti i permessi
        perms = db.query(Permission).filter(Permission.attivo == True).all()
        permissions = [{"codice": p.codice, "nome": p.nome} for p in perms]
    else:
        # Prendi i permessi concessi dal mapping ruolo-permesso
        perms = db.query(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.ruolo == current_user.ruolo.value,
            RolePermission.granted == True
        ).all()
        permissions = [{"codice": p.codice, "nome": p.nome} for p in perms]
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "ruolo": current_user.ruolo.value,
        "permissions": permissions,
        "count": len(permissions)
    }


@router.get("/matrix")
def get_permissions_matrix(
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Ottieni la matrice permessi (solo admin)
    Ritorna tutti i permessi con il loro status per ogni ruolo
    """
    from app.models import Permission, RolePermission
    
    # Prendi tutti i ruoli attivi
    all_roles = [r.value for r in UserRole]
    
    # Prendi tutti i permessi attivi
    all_permissions = db.query(Permission).filter(Permission.attivo == True).all()
    
    # Per ogni permesso, costruisci la lista dei ruoli e il loro granted status
    permissions_data = []
    for perm in all_permissions:
        roles_data = []
        for role in all_roles:
            role_perm = db.query(RolePermission).filter(
                RolePermission.permission_id == perm.id,
                RolePermission.ruolo == role
            ).first()
            
            granted = role_perm.granted if role_perm else False
            roles_data.append({
                "ruolo": role,
                "granted": granted
            })
        
        permissions_data.append({
            "id": perm.id,
            "codice": perm.codice,
            "nome": perm.nome,
            "categoria": perm.categoria,
            "descrizione": perm.descrizione,
            "roles": roles_data
        })
    
    return {
        "permissions": permissions_data,
        "roles": all_roles,
        "count": len(permissions_data)
    }


@router.put("/matrix")
def update_permissions_matrix(
    matrix_data: Dict[str, Dict[str, bool]],
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Aggiorna la matrice permessi (solo admin)
    
    Atteso formato:
    {
      "ADMIN": {"permesso1": true, "permesso2": false, ...},
      "GM": {"permesso1": true, ...},
      ...
    }
    """
    from app.models import Permission, RolePermission
    
    updated_count = 0
    
    try:
        for role, permissions in matrix_data.items():
            for perm_codice, granted in permissions.items():
                # Trova il permesso
                permission = db.query(Permission).filter(
                    Permission.codice == perm_codice
                ).first()
                
                if not permission:
                    continue
                
                # Trova o crea il mapping ruolo-permesso
                role_perm = db.query(RolePermission).filter(
                    RolePermission.permission_id == permission.id,
                    RolePermission.ruolo == role
                ).first()
                
                if role_perm:
                    # Aggiorna il mapping esistente
                    role_perm.granted = granted
                else:
                    # Crea nuovo mapping
                    role_perm = RolePermission(
                        permission_id=permission.id,
                        ruolo=role,
                        granted=granted
                    )
                    db.add(role_perm)
                
                updated_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Matrice permessi aggiornata: {updated_count} mappamenti",
            "updated_count": updated_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore nell'aggiornamento della matrice: {str(e)}"
        )
