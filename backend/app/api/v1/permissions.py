"""
API Endpoints per gestione Permessi e Ruoli (RBAC)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.rbac import Permission, RolePermission

router = APIRouter(tags=["permissions"])



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verifica che l'utente sia admin"""
    if current_user.ruolo != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo admin può gestire permessi"
        )
    return current_user


def get_role_label(role: str) -> str:
    """Ritorna il label con emoji per un ruolo"""
    role_labels = {
        "ADMIN": "👑 Admin",
        "GENERAL_MANAGER": "🏢 General Manager",
        "GM_ASSISTANT": "👤 GM Assistant",
        "FRONTEND_MANAGER": "🖥️ Frontend Manager",
        "CMM": "🔧 Capo Meccanica",
        "CBM": "🎨 Capo Carrozzeria",
        "WORKSHOP": "🔨 Operatore Meccanica",
        "BODYSHOP": "🎨 Operatore Carrozzeria",
    }
    return role_labels.get(role, role)



# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/")
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista tutti i permessi disponibili
    """
    permissions = db.query(Permission).filter(
        Permission.attivo == True
    ).order_by(Permission.categoria).all()
    
    return {
        "count": len(permissions),
        "permissions": [
            {
                "id": p.id,
                "codice": p.codice,
                "nome": p.nome,
                "categoria": p.categoria,
                "descrizione": p.descrizione,
            }
            for p in permissions
        ]
    }


@router.get("/roles")
def get_available_roles(
    current_user: User = Depends(get_current_user)
):
    """
    Ritorna lista completa di tutti i ruoli disponibili nel sistema con labels
    """
    roles = [
        {
            "value": e.value,
            "label": get_role_label(e.value)
        }
        for e in UserRole
    ]
    return {
        "count": len(roles),
        "roles": roles
    }


@router.get("/matrix")
def get_permissions_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Ottieni la matrice completa Ruoli × Permessi
    
    Response:
    {
        "permissions": [
            {
                "id": 1,
                "codice": "customers.view",
                "nome": "Visualizza Clienti",
                "categoria": "Clienti",
                "roles": [
                    {"ruolo": "ADMIN", "granted": true},
                    {"ruolo": "GM", "granted": true},
                    {"ruolo": "CMM", "granted": false},
                    ...
                ]
            },
            ...
        ],
        "roles": ["ADMIN", "GENERAL_MANAGER", "GM_ASSISTANT", "CMM", "CBM", "WORKSHOP", "BODYSHOP"]
    }
    """
    # Prendi tutti i permessi
    permissions = db.query(Permission).filter(Permission.attivo == True).all()
    
    # Prendi tutti i ruoli
    all_roles = [e.value for e in UserRole]
    
    # Prendi tutti i mappamenti
    role_permissions_list = db.query(RolePermission).all()
    
    # Costruisci matrice
    permissions_data = []
    for perm in permissions:
        roles_data = []
        for role in all_roles:
            # Cerca il mappamento
            rp = next(
                (rp for rp in role_permissions_list 
                 if rp.permission_id == perm.id and rp.ruolo == role),
                None
            )
            
            roles_data.append({
                "ruolo": role,
                "granted": rp.granted if rp else False
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
        "roles": all_roles
    }


@router.put("/matrix")
def update_permissions_matrix(
    data: Dict[str, Dict[str, bool]],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Aggiorna la matrice Ruoli × Permessi
    
    Request body:
    {
        "ADMIN": {
            "customers.view": true,
            "customers.create": true,
            "system.manage_users": true,
            ...
        },
        "GM": {
            "customers.view": true,
            "customers.create": true,
            "system.manage_users": false,
            ...
        }
    }
    """
    try:
        updates_count = 0
        
        for ruolo, permissions_dict in data.items():
            # Valida ruolo
            valid_roles = [e.value for e in UserRole]
            if ruolo not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ruolo non valido: {ruolo}"
                )
            
            for perm_codice, granted in permissions_dict.items():
                # Prendi il permesso
                perm = db.query(Permission).filter(
                    Permission.codice == perm_codice
                ).first()
                
                if not perm:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Permesso non trovato: {perm_codice}"
                    )
                
                # Prendi o crea il mappamento
                rp = db.query(RolePermission).filter(
                    RolePermission.ruolo == ruolo,
                    RolePermission.permission_id == perm.id
                ).first()
                
                if rp:
                    # Aggiorna
                    rp.granted = granted
                    db.add(rp)
                    updates_count += 1
                else:
                    # Crea nuovo
                    new_rp = RolePermission(
                        ruolo=ruolo,
                        permission_id=perm.id,
                        granted=granted
                    )
                    db.add(new_rp)
                    updates_count += 1
        
        db.commit()
        
        return {
            "message": "Permessi aggiornati con successo",
            "updated": updates_count
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/user/me")
def get_user_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ottieni i permessi dell'utente corrente
    
    Questo è quello che torna dopo LOGIN
    """
    # Se admin, ritorna tutti i permessi
    if current_user.ruolo == UserRole.ADMIN:
        permissions = db.query(Permission).filter(Permission.attivo == True).all()
        permission_codes = [p.codice for p in permissions]
    else:
        # Altrimenti prendi solo quelli concessi
        permissions = db.query(Permission).join(
            RolePermission,
            Permission.id == RolePermission.permission_id
        ).filter(
            RolePermission.ruolo == current_user.ruolo.value,
            RolePermission.granted == True
        ).all()
        permission_codes = [p.codice for p in permissions]
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "ruolo": current_user.ruolo.value,
        "workshop_id": current_user.workshop_id,
        "permissions": permission_codes,
        "permission_count": len(permission_codes)
    }


@router.get("/role/{role_name}")
def get_role_permissions(
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ottieni tutti i permessi per un ruolo specifico
    """
    # Valida ruolo
    valid_roles = [e.value for e in UserRole]
    if role_name not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ruolo non valido: {role_name}"
        )
    
    permissions = db.query(Permission).join(
        RolePermission,
        Permission.id == RolePermission.permission_id
    ).filter(
        RolePermission.ruolo == role_name,
        RolePermission.granted == True
    ).order_by(Permission.categoria, Permission.codice).all()
    
    return {
        "role": role_name,
        "permissions": [
            {
                "codice": p.codice,
                "nome": p.nome,
                "categoria": p.categoria
            }
            for p in permissions
        ],
        "total": len(permissions)
    }
