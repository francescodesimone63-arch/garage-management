"""
API endpoints per la consultazione dei log attività (Activity Logs).
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse, ActivityLogWithDetails

router = APIRouter()


@router.get("/", response_model=List[ActivityLogResponse])
def get_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Recupera log attività con filtri.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    
    I log sono read-only, generati automaticamente dal sistema.
    """
    query = db.query(ActivityLog)
    
    # Filtro utente
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    # Filtro azione
    if action:
        query = query.filter(ActivityLog.action == action)
    
    # Filtro entità
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(ActivityLog.entity_id == entity_id)
    
    # Filtro periodo
    if start_date:
        query = query.filter(ActivityLog.timestamp >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(ActivityLog.timestamp <= datetime.combine(end_date, datetime.max.time()))
    
    query = query.order_by(ActivityLog.timestamp.desc())
    logs = query.offset(skip).limit(limit).all()
    
    return logs


@router.get("/{log_id}", response_model=ActivityLogWithDetails)
def get_activity_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Recupera dettagli log attività specifico.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log ID {log_id} non trovato"
        )
    
    # Info utente
    user_info = None
    if log.user:
        user_info = {
            "id": log.user.id,
            "full_name": log.user.full_name,
            "email": log.user.email,
            "role": log.user.role.value
        }
    
    return ActivityLogWithDetails(
        **log.__dict__,
        user_info=user_info
    )


@router.get("/audit/{entity_type}/{entity_id}", response_model=List[ActivityLogResponse])
def get_entity_audit_trail(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Recupera trail di audit completo per un'entità specifica.
    
    Mostra tutte le modifiche effettuate sull'entità nel tempo.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    logs = db.query(ActivityLog).filter(
        and_(
            ActivityLog.entity_type == entity_type,
            ActivityLog.entity_id == entity_id
        )
    ).order_by(ActivityLog.timestamp.desc()).all()
    
    return logs


@router.get("/user/{user_id}/history", response_model=List[ActivityLogResponse])
def get_user_activity_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Recupera storico attività di un utente specifico.
    
    days: numero di giorni di storico (default 30)
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(ActivityLog).filter(
        and_(
            ActivityLog.user_id == user_id,
            ActivityLog.timestamp >= cutoff_date
        )
    ).order_by(ActivityLog.timestamp.desc()).all()
    
    return logs


@router.get("/recent/all", response_model=List[ActivityLogResponse])
def get_recent_activity(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Recupera attività recenti del sistema.
    
    Utile per dashboard e monitoring.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    logs = db.query(ActivityLog).order_by(
        ActivityLog.timestamp.desc()
    ).limit(limit).all()
    
    return logs


@router.get("/stats/summary", response_model=dict)
def get_activity_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Statistiche attività sistema.
    
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    total_activities = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.timestamp >= cutoff_date
    ).scalar() or 0
    
    # Conta per azione
    action_stats = db.query(
        ActivityLog.action,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.timestamp >= cutoff_date
    ).group_by(ActivityLog.action).all()
    
    # Conta per utente (top 10)
    user_stats = db.query(
        ActivityLog.user_id,
        func.count(ActivityLog.id).label('count')
    ).filter(
        ActivityLog.timestamp >= cutoff_date
    ).group_by(ActivityLog.user_id).order_by(
        func.count(ActivityLog.id).desc()
    ).limit(10).all()
    
    # Formatta stats utenti con info
    top_users = []
    for user_id, count in user_stats:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            top_users.append({
                "user_id": user_id,
                "full_name": user.full_name,
                "activity_count": count
            })
    
    # Conta per entità
    entity_stats = db.query(
        ActivityLog.entity_type,
        func.count(ActivityLog.id)
    ).filter(
        ActivityLog.timestamp >= cutoff_date
    ).group_by(ActivityLog.entity_type).all()
    
    # Attività per giorno (ultimi 7 giorni)
    daily_stats = []
    for i in range(7):
        day_start = datetime.utcnow() - timedelta(days=i)
        day_start = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = db.query(func.count(ActivityLog.id)).filter(
            and_(
                ActivityLog.timestamp >= day_start,
                ActivityLog.timestamp < day_end
            )
        ).scalar() or 0
        
        daily_stats.append({
            "date": day_start.date().isoformat(),
            "count": count
        })
    
    daily_stats.reverse()  # Ordine cronologico
    
    return {
        "period_days": days,
        "total_activities": total_activities,
        "daily_average": round(total_activities / days, 2),
        "by_action": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in action_stats
        },
        "by_entity": {
            stat[0] if stat[0] else "unknown": stat[1]
            for stat in entity_stats
        },
        "top_users": top_users,
        "daily_stats": daily_stats
    }


@router.get("/stats/user-activity", response_model=dict)
def get_user_activity_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Statistiche attività per utente.
    
    Mostra distribuzione attività tra gli utenti del sistema.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Conta attività per ogni utente
    user_stats = db.query(
        User.id,
        User.full_name,
        User.email,
        User.role,
        func.count(ActivityLog.id).label('activity_count')
    ).outerjoin(
        ActivityLog,
        and_(
            ActivityLog.user_id == User.id,
            ActivityLog.timestamp >= cutoff_date
        )
    ).group_by(User.id).all()
    
    users_data = []
    for user_id, full_name, email, role, count in user_stats:
        users_data.append({
            "user_id": user_id,
            "full_name": full_name,
            "email": email,
            "role": role.value,
            "activity_count": count or 0
        })
    
    # Ordina per conteggio attività
    users_data.sort(key=lambda x: x['activity_count'], reverse=True)
    
    return {
        "period_days": days,
        "users": users_data
    }
