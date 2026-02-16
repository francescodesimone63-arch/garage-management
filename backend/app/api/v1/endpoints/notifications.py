"""
API endpoints per la gestione delle notifiche (Notifications).
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationBulkCreate, NotificationMarkRead
)

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = None,
    notification_type: Optional[NotificationType] = None,
    status_filter: Optional[NotificationStatus] = None,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera notifiche con filtri.
    
    Se user_id non specificato, mostra notifiche dell'utente corrente.
    """
    query = db.query(Notification)
    
    # Filtro utente (default: utente corrente)
    target_user_id = user_id if user_id else current_user.id
    query = query.filter(Notification.user_id == target_user_id)
    
    # Filtro tipo
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    # Filtro status
    if status_filter:
        query = query.filter(Notification.status == status_filter)
    
    # Solo non lette
    if unread_only:
        query = query.filter(Notification.status == NotificationStatus.PENDING)
    
    query = query.order_by(Notification.created_at.desc())
    notifications = query.offset(skip).limit(limit).all()
    
    return notifications


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Crea nuova notifica.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    # Crea notifica
    notification = Notification(**notification_data.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # TODO: Inviare notifica tramite canali specificati (email, SMS, push)
    
    return notification


@router.post("/bulk", response_model=dict)
def create_bulk_notifications(
    bulk_data: NotificationBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Crea notifiche multiple per più utenti.
    """
    created_count = 0
    failed_count = 0
    
    for user_id in bulk_data.user_ids:
        try:
            notification = Notification(
                user_id=user_id,
                notification_type=bulk_data.notification_type,
                title=bulk_data.title,
                message=bulk_data.message,
                channels=bulk_data.channels,
                priority=bulk_data.priority
            )
            db.add(notification)
            created_count += 1
        except Exception as e:
            failed_count += 1
            continue
    
    db.commit()
    
    return {
        "success": True,
        "created": created_count,
        "failed": failed_count,
        "total_users": len(bulk_data.user_ids)
    }


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli notifica.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notifica ID {notification_id} non trovata"
        )
    
    # Verifica accesso (solo proprie notifiche o admin)
    if notification.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato ad accedere a questa notifica"
        )
    
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Aggiorna notifica.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notifica ID {notification_id} non trovata"
        )
    
    # Aggiorna campi
    update_data = notification_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina notifica (solo proprie notifiche o admin).
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notifica ID {notification_id} non trovata"
        )
    
    # Verifica accesso
    if notification.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato ad eliminare questa notifica"
        )
    
    db.delete(notification)
    db.commit()
    
    return None


@router.patch("/mark-read", response_model=dict)
def mark_notifications_read(
    mark_data: NotificationMarkRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Segna notifiche come lette.
    
    Se notification_ids vuoto, segna tutte le notifiche dell'utente come lette.
    """
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.PENDING
    )
    
    # Filtra per IDs specifici se forniti
    if mark_data.notification_ids:
        query = query.filter(Notification.id.in_(mark_data.notification_ids))
    
    # Aggiorna status
    updated_count = query.update(
        {
            "status": NotificationStatus.READ,
            "read_at": datetime.utcnow()
        },
        synchronize_session=False
    )
    
    db.commit()
    
    return {
        "success": True,
        "updated_count": updated_count
    }


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Segna singola notifica come letta.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notifica ID {notification_id} non trovata"
        )
    
    # Verifica accesso
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato"
        )
    
    notification.status = NotificationStatus.READ
    notification.read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    
    return notification


@router.get("/me/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Conta notifiche non lette dell'utente corrente.
    """
    unread_count = db.query(func.count(Notification.id)).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.status == NotificationStatus.PENDING
        )
    ).scalar() or 0
    
    # Conta per tipo
    type_counts = db.query(
        Notification.notification_type,
        func.count(Notification.id)
    ).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.status == NotificationStatus.PENDING
        )
    ).group_by(Notification.notification_type).all()
    
    return {
        "unread_total": unread_count,
        "by_type": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in type_counts
        }
    }


@router.get("/stats/summary", response_model=dict)
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Statistiche generali notifiche (solo admin).
    """
    total_notifications = db.query(func.count(Notification.id)).scalar() or 0
    
    # Conta per status
    status_stats = db.query(
        Notification.status,
        func.count(Notification.id)
    ).group_by(Notification.status).all()
    
    # Conta per tipo
    type_stats = db.query(
        Notification.notification_type,
        func.count(Notification.id)
    ).group_by(Notification.notification_type).all()
    
    # Tasso di lettura
    read_count = db.query(func.count(Notification.id)).filter(
        Notification.status == NotificationStatus.READ
    ).scalar() or 0
    
    read_rate = round((read_count / total_notifications * 100) if total_notifications > 0 else 0, 2)
    
    return {
        "total_notifications": total_notifications,
        "read_rate": read_rate,
        "by_status": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in status_stats
        },
        "by_type": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in type_stats
        }
    }
