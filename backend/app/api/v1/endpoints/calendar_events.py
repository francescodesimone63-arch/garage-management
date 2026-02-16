"""
API endpoints per la gestione degli eventi del calendario (Calendar Events).
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.calendar_event import CalendarEvent
from app.schemas.calendar_event import (
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    CalendarEventWithDetails
)

router = APIRouter()


@router.get("/", response_model=List[CalendarEventResponse])
def get_calendar_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera eventi calendario con filtri.
    """
    query = db.query(CalendarEvent)
    
    # Filtro tipo evento
    if event_type:
        query = query.filter(CalendarEvent.event_type == event_type)
    
    # Filtro status
    if status_filter:
        query = query.filter(CalendarEvent.status == status_filter)
    
    # Filtro utente assegnato
    if user_id:
        query = query.filter(CalendarEvent.assigned_to_id == user_id)
    
    # Filtro periodo
    if start_date:
        query = query.filter(CalendarEvent.start_datetime >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(CalendarEvent.end_datetime <= datetime.combine(end_date, datetime.max.time()))
    
    query = query.order_by(CalendarEvent.start_datetime.asc())
    events = query.offset(skip).limit(limit).all()
    
    return events


@router.post("/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea nuovo evento calendario.
    """
    # Verifica validità date
    if event_data.end_datetime and event_data.end_datetime < event_data.start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data fine deve essere successiva a data inizio"
        )
    
    # Crea evento
    event = CalendarEvent(**event_data.model_dump(), created_by_id=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # TODO: Sincronizza con Google Calendar se configurato
    
    return event


@router.get("/view", response_model=List[CalendarEventResponse])
def get_calendar_view(
    view_type: str = Query("month", regex="^(day|week|month)$"),
    reference_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera eventi per vista calendario (giorno/settimana/mese).
    
    view_type:
    - day: eventi del giorno
    - week: eventi della settimana
    - month: eventi del mese
    """
    from datetime import timedelta
    
    if view_type == "day":
        start = datetime.combine(reference_date, datetime.min.time())
        end = datetime.combine(reference_date, datetime.max.time())
    elif view_type == "week":
        # Inizio settimana (lunedì)
        start = datetime.combine(reference_date - timedelta(days=reference_date.weekday()), datetime.min.time())
        end = start + timedelta(days=7)
    else:  # month
        start = datetime.combine(reference_date.replace(day=1), datetime.min.time())
        # Ultimo giorno del mese
        if reference_date.month == 12:
            end = datetime.combine(reference_date.replace(year=reference_date.year + 1, month=1, day=1), datetime.min.time())
        else:
            end = datetime.combine(reference_date.replace(month=reference_date.month + 1, day=1), datetime.min.time())
    
    events = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.start_datetime >= start,
            CalendarEvent.start_datetime < end
        )
    ).order_by(CalendarEvent.start_datetime.asc()).all()
    
    return events


@router.get("/{event_id}", response_model=CalendarEventWithDetails)
def get_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera dettagli evento calendario.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento ID {event_id} non trovato"
        )
    
    # Info utente assegnato
    assigned_user_info = None
    if event.assigned_to:
        assigned_user_info = {
            "id": event.assigned_to.id,
            "full_name": event.assigned_to.full_name,
            "email": event.assigned_to.email
        }
    
    # Info creatore
    creator_info = None
    if event.created_by:
        creator_info = {
            "id": event.created_by.id,
            "full_name": event.created_by.full_name,
            "email": event.created_by.email
        }
    
    return CalendarEventWithDetails(
        **event.__dict__,
        assigned_user_info=assigned_user_info,
        creator_info=creator_info
    )


@router.put("/{event_id}", response_model=CalendarEventResponse)
def update_calendar_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna evento calendario.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento ID {event_id} non trovato"
        )
    
    # Verifica permessi (creatore o admin)
    if event.created_by_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a modificare questo evento"
        )
    
    # Aggiorna campi
    update_data = event_data.model_dump(exclude_unset=True)
    
    # Verifica validità date se modificate
    start = update_data.get("start_datetime", event.start_datetime)
    end = update_data.get("end_datetime", event.end_datetime)
    if end and end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data fine deve essere successiva a data inizio"
        )
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    # TODO: Sincronizza con Google Calendar
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina evento calendario.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento ID {event_id} non trovato"
        )
    
    # Verifica permessi
    if event.created_by_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.GENERAL_MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a eliminare questo evento"
        )
    
    db.delete(event)
    db.commit()
    
    # TODO: Rimuovi da Google Calendar
    
    return None


@router.patch("/{event_id}/status", response_model=CalendarEventResponse)
def update_event_status(
    event_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna status evento.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento ID {event_id} non trovato"
        )
    
    event.status = new_status
    db.commit()
    db.refresh(event)
    
    return event


@router.post("/sync", response_model=dict)
def sync_with_google_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.GENERAL_MANAGER]))
):
    """
    Sincronizza eventi con Google Calendar.
    Richiede ruolo: ADMIN, GENERAL_MANAGER
    """
    # TODO: Implementare integrazione Google Calendar API
    # 1. Autenticazione OAuth2
    # 2. Recupera eventi da Google Calendar
    # 3. Sincronizza con database locale
    # 4. Push eventi locali non sincronizzati
    
    return {
        "success": True,
        "message": "Sincronizzazione con Google Calendar non ancora implementata",
        "synced_events": 0
    }


@router.get("/stats/summary", response_model=dict)
def get_calendar_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche eventi calendario.
    """
    from datetime import timedelta
    
    total_events = db.query(func.count(CalendarEvent.id)).scalar() or 0
    
    # Conta per status
    status_stats = db.query(
        CalendarEvent.status,
        func.count(CalendarEvent.id)
    ).group_by(CalendarEvent.status).all()
    
    # Eventi oggi
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    today_events = db.query(func.count(CalendarEvent.id)).filter(
        and_(
            CalendarEvent.start_datetime >= today_start,
            CalendarEvent.start_datetime <= today_end
        )
    ).scalar() or 0
    
    # Eventi settimana prossima
    week_start = today_start
    week_end = today_start + timedelta(days=7)
    upcoming_week = db.query(func.count(CalendarEvent.id)).filter(
        and_(
            CalendarEvent.start_datetime >= week_start,
            CalendarEvent.start_datetime < week_end
        )
    ).scalar() or 0
    
    return {
        "total_events": total_events,
        "today_events": today_events,
        "upcoming_week": upcoming_week,
        "by_status": {
            stat[0].value if stat[0] else "unknown": stat[1]
            for stat in status_stats
        }
    }
