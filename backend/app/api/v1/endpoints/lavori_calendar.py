"""
Work order calendar endpoints

POST /api/v1/lavori/{lavoro_id}/calendar - Create calendar event
PATCH /api/v1/lavori/{lavoro_id}/calendar - Update calendar event
DELETE /api/v1/lavori/{lavoro_id}/calendar - Delete calendar event
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_active_superuser
from app.models.user import User
from app.models.work_order import WorkOrder
from app import google_calendar as gc


router = APIRouter(prefix="/lavori", tags=["work-order-calendar"])


class CalendarEventCreate(BaseModel):
    """Request model for creating calendar event"""
    summary: Optional[str] = None  # Falls back to "Lavoro {id}"
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarEventUpdate(BaseModel):
    """Request model for updating calendar event"""
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    data_appuntamento: Optional[str] = None  # ISO 8601 with timezone
    data_fine_prevista: Optional[str] = None  # ISO 8601 with timezone


class CalendarEventResponse(BaseModel):
    """Response model for calendar operations"""
    google_event_id: str
    html_link: str
    summary: str
    description: Optional[str]
    start: dict
    end: dict
    
    class Config:
        from_attributes = True


@router.post("/{lavoro_id}/calendar", response_model=CalendarEventResponse)
def create_calendar_event(
    lavoro_id: int,
    payload: CalendarEventCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Create Google Calendar event for work order.
    
    - Validates data_appuntamento and data_fine_prevista are set and valid
    - Creates event with default summary "Lavoro {lavoro_id}" or custom summary
    - Stores event ID in DB and returns event details
    
    Args:
        lavoro_id: Work order ID
        payload: Optional custom summary/description/location
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        Calendar event details
        
    Raises:
        404: Work order not found
        400: Missing or invalid dates
        500: Calendar API error
    """
    # Fetch work order
    lavoro = db.query(WorkOrder).filter(WorkOrder.id == lavoro_id).first()
    if not lavoro:
        raise HTTPException(status_code=404, detail=f"Work order with ID {lavoro_id} not found")
    
    # Validate dates
    if not lavoro.data_appuntamento or not lavoro.data_fine_prevista:
        raise HTTPException(
            status_code=400,
            detail="data_appuntamento and data_fine_prevista must be set before creating calendar event",
        )
    
    if lavoro.data_fine_prevista <= lavoro.data_appuntamento:
        raise HTTPException(
            status_code=400,
            detail="data_fine_prevista must be after data_appuntamento",
        )
    
    # Prepare event details
    summary = payload.summary if payload and payload.summary else f"Lavoro {lavoro.numero_scheda}"
    description = (
        payload.description if payload and payload.description else f"Officina garage - Lavoro {lavoro.numero_scheda}"
    )
    location = payload.location if payload and payload.location else None
    
    # Get calendar service
    try:
        service = gc.get_calendar_service_sync(db)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Create event
    event = gc.create_calendar_event(
        service=service,
        summary=summary,
        description=description,
        start_datetime=lavoro.data_appuntamento,
        end_datetime=lavoro.data_fine_prevista,
        location=location,
        calendar_id=gc.GOOGLE_CALENDAR_ID,
    )
    
    if not event:
        raise HTTPException(status_code=500, detail="Failed to create calendar event")
    
    # Save event ID to DB
    lavoro.google_event_id = event["id"]
    db.commit()
    db.refresh(lavoro)
    
    return {
        "google_event_id": event["id"],
        "html_link": event.get("htmlLink", ""),
        "summary": event["summary"],
        "description": event.get("description"),
        "start": event["start"],
        "end": event["end"],
    }


@router.patch("/{lavoro_id}/calendar", response_model=CalendarEventResponse)
def update_calendar_event(
    lavoro_id: int,
    payload: CalendarEventUpdate,
    send_updates: str = Query("none", description="'all', 'externalOnly', or 'none'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Update Google Calendar event for work order.
    
    Patch semantics: only provided fields are updated.
    
    Args:
        lavoro_id: Work order ID
        payload: Fields to update (partial update allowed)
        send_updates: Notification option for attendees
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        Updated calendar event details
        
    Raises:
        404: Work order or event not found
        409: No event associated with work order
        400: Invalid datetime format or logic
        500: Calendar API error
    """
    # Fetch work order
    lavoro = db.query(WorkOrder).filter(WorkOrder.id == lavoro_id).first()
    if not lavoro:
        raise HTTPException(status_code=404, detail=f"Work order with ID {lavoro_id} not found")
    
    # Check if event exists
    if not lavoro.google_event_id:
        raise HTTPException(
            status_code=409,
            detail="No Google Calendar event associated with this work order",
        )
    
    # Parse datetime fields if provided
    start_datetime = None
    end_datetime = None
    
    if payload.data_appuntamento:
        try:
            start_datetime = datetime.fromisoformat(payload.data_appuntamento)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid data_appuntamento format. Use ISO 8601 with timezone.",
            )
    else:
        start_datetime = lavoro.data_appuntamento
    
    if payload.data_fine_prevista:
        try:
            end_datetime = datetime.fromisoformat(payload.data_fine_prevista)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid data_fine_prevista format. Use ISO 8601 with timezone.",
            )
    else:
        end_datetime = lavoro.data_fine_prevista
    
    # Validate end > start
    if end_datetime <= start_datetime:
        raise HTTPException(
            status_code=400,
            detail="data_fine_prevista must be after data_appuntamento",
        )
    
    # Get calendar service
    try:
        service = gc.get_calendar_service_sync(db)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Update event
    event = gc.update_calendar_event(
        service=service,
        event_id=lavoro.google_event_id,
        summary=payload.summary,
        description=payload.description,
        location=payload.location,
        start_datetime=start_datetime if payload.data_appuntamento else None,
        end_datetime=end_datetime if payload.data_fine_prevista else None,
        send_updates=send_updates,
        calendar_id=gc.GOOGLE_CALENDAR_ID,
    )
    
    if not event:
        raise HTTPException(status_code=502, detail="Failed to update calendar event")
    
    # Update work order timestamps
    if payload.data_appuntamento:
        lavoro.data_appuntamento = start_datetime
    if payload.data_fine_prevista:
        lavoro.data_fine_prevista = end_datetime
    
    db.commit()
    db.refresh(lavoro)
    
    return {
        "google_event_id": event["id"],
        "html_link": event.get("htmlLink", ""),
        "summary": event["summary"],
        "description": event.get("description"),
        "start": event["start"],
        "end": event["end"],
    }


@router.delete("/{lavoro_id}/calendar", status_code=204)
def delete_calendar_event(
    lavoro_id: int,
    send_updates: str = Query("none", description="'all', 'externalOnly', or 'none'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Delete Google Calendar event for work order.
    
    Args:
        lavoro_id: Work order ID
        send_updates: Notification option for attendees
        db: Database session
        current_user: Current authenticated admin user
        
    Raises:
        404: Work order not found
        400: No event associated with work order
        500: Calendar API error
    """
    # Fetch work order
    lavoro = db.query(WorkOrder).filter(WorkOrder.id == lavoro_id).first()
    if not lavoro:
        raise HTTPException(status_code=404, detail=f"Work order with ID {lavoro_id} not found")
    
    # Check if event exists
    if not lavoro.google_event_id:
        raise HTTPException(
            status_code=400,
            detail="No Google Calendar event associated with this work order",
        )
    
    # Get calendar service
    try:
        service = gc.get_calendar_service_sync(db)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Delete event
    success = gc.delete_calendar_event(
        service=service,
        event_id=lavoro.google_event_id,
        send_updates=send_updates,
        calendar_id=gc.GOOGLE_CALENDAR_ID,
    )
    
    if not success:
        raise HTTPException(status_code=502, detail="Failed to delete calendar event")
    
    # Clear event ID from DB
    lavoro.google_event_id = None
    db.commit()
