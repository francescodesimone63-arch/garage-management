"""
Endpoint per Google Calendar - gestione appuntamenti schede lavori
"""
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from app.core.deps import get_async_db, get_current_user_async
from app.models.user import User
from app.models.work_order import WorkOrder
from app import google_calendar as gc

router = APIRouter(prefix="/calendar", tags=["calendar"])


# ==================== DATA MODELS ====================

class CalendarEventResponse(BaseModel):
    """Risposta singolo evento calendario"""
    id: str
    title: str
    start: str  # ISO 8601 datetime
    end: str    # ISO 8601 datetime
    is_busy: bool = True


class CalendarEventsListResponse(BaseModel):
    """Lista eventi per periodo"""
    events: List[CalendarEventResponse]
    timezone: str
    period: dict


class BookAppointmentResponse(BaseModel):
    """Risposta prenotazione appuntamento"""
    confirmed: bool
    work_order_id: int
    google_event_id: Optional[str]
    appointment_date: str  # YYYY-MM-DD
    saved_at: str


class AppointmentInfo(BaseModel):
    """Info appuntamento per vista calendario (tutti i clienti)"""
    appointment_date: str  # YYYY-MM-DD
    work_order_id: int
    customer_name: str
    customer_id: int


class AllAppointmentsResponse(BaseModel):
    """Lista TUTTI gli appuntamenti di un periodo"""
    appointments: List[AppointmentInfo]
    period: dict


# ==================== ENDPOINTS ====================

@router.get(
    "/events",
    response_model=CalendarEventsListResponse,
    summary="Lista eventi Google Calendar per periodo"
)
async def list_calendar_events(
    timeMin: str = Query(
        ...,
        description="Inizio periodo (RFC3339, es. 2026-02-10T00:00:00+01:00)"
    ),
    timeMax: str = Query(
        ...,
        description="Fine periodo (RFC3339, es. 2026-02-17T23:59:59+01:00)"
    ),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_async)
):
    """
    Ritorna lista di TUTTI gli eventi Google Calendar nel periodo.
    
    - Espande eventi ricorrenti in istanze singole (singleEvents=True)
    - Ordina cronologicamente
    - Eventi occupati hanno is_busy=true (frontend li renderizza grigi)
    
    **Parametri:**
    - timeMin: datetime inizio (deve includere time + timezone offset)
    - timeMax: datetime fine (idem)
    
    **Errori:**
    - 400: timeMin/timeMax invalidi
    - 401: Non autenticato
    - 502: Errore Google Calendar API
    """
    
    # 1. Valida formato datetime
    try:
        # Accetta sia formato con + che con Z
        time_min_clean = timeMin.replace('Z', '+00:00')
        time_max_clean = timeMax.replace('Z', '+00:00')
        
        datetime.fromisoformat(time_min_clean)
        datetime.fromisoformat(time_max_clean)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato datetime non valido. Usa RFC3339 (es. 2026-02-10T00:00:00+01:00). Errore: {str(e)}"
        )
    
    # 2. Carica servizio Google Calendar
    try:
        service = await gc.get_calendar_service(db)
    except Exception as e:
        print(f"❌ Google Calendar error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Calendar non configurato: {str(e)}. Effettua prima il login OAuth."
        )
    
    # 3. Chiama API Google
    try:
        events_result = service.events().list(
            calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            timeMin=timeMin,
            timeMax=timeMax,
            singleEvents=True,       # Espandi ricorrenze
            orderBy="startTime",      # Ordina cronologicamente
            showDeleted=False,        # Escludi cancellati
            maxResults=100           # Limit API
        ).execute()
        
        raw_events = events_result.get('items', [])
        
    except Exception as e:
        print(f"❌ ERRORE Google Calendar API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Errore lettura Google Calendar: {str(e)}"
        )
    
    # 4. Mappa risposta
    events = []
    for event in raw_events:
        # Salta eventi all-day o con struttura differente
        start = event.get("start", {})
        end = event.get("end", {})
        
        start_dt = start.get("dateTime") or start.get("date")
        end_dt = end.get("dateTime") or end.get("date")
        
        if not start_dt or not end_dt:
            continue
        
        # Determina se occupato (default=True se non specificato)
        transparency = event.get("transparency", "opaque")
        is_busy = transparency == "opaque"
        
        events.append(CalendarEventResponse(
            id=event.get("id"),
            title=event.get("summary", "[Senza titolo]"),
            start=start_dt,
            end=end_dt,
            is_busy=is_busy
        ))
    
    return CalendarEventsListResponse(
        events=events,
        timezone="Europe/Rome",
        period={"from": timeMin, "to": timeMax}
    )


@router.get(
    "/appointments/month",
    response_model=AllAppointmentsResponse,
    summary="Ottiene TUTTI gli appuntamenti del mese (di tutti i clienti)"
)
async def get_all_appointments_for_month(
    month: int = Query(..., ge=1, le=12, description="Mese (1-12)"),
    year: int = Query(..., ge=2020, description="Anno"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_async)
):
    """
    Ritorna TUTTI gli appuntamenti del mese per TUTTI i clienti.
    Usato dal calendario modale per mostrare quali giorni sono già occupati.
    
    **Parametri:**
    - month: Mese (1-12)
    - year: Anno
    
    **Risposta:**
    ```json
    {
        "appointments": [
            {
                "appointment_date": "2026-02-20",
                "work_order_id": 1,
                "customer_name": "Mario Rossi",
                "customer_id": 5
            },
            ...
        ],
        "period": {"month": 2, "year": 2026}
    }
    ```
    """
    try:
        # Carica TUTTI gli appuntamenti del mese (di tutti i clienti)
        result = await db.execute(
            select(WorkOrder)
            .filter(
                WorkOrder.data_appuntamento.isnot(None),  # Solo quelli con appuntamento
            )
            .options(
                joinedload(WorkOrder.customer)
            )
        )
        all_work_orders = result.scalars().unique().all()
        
        # Filtra per il mese and anno specificato
        appointments = []
        for wo in all_work_orders:
            if wo.data_appuntamento and wo.customer:
                if wo.data_appuntamento.month == month and wo.data_appuntamento.year == year:
                    appointments.append(AppointmentInfo(
                        appointment_date=wo.data_appuntamento.isoformat(),  # YYYY-MM-DD
                        work_order_id=wo.id,
                        customer_name=wo.customer.full_name,
                        customer_id=wo.customer_id
                    ))
        
        # Ordina per data
        appointments.sort(key=lambda x: x.appointment_date)
        
        return AllAppointmentsResponse(
            appointments=appointments,
            period={"month": month, "year": year}
        )
        
    except Exception as e:
        print(f"❌ Errore caricamento appuntamenti mese: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore caricamento appuntamenti: {str(e)}"
        )


@router.post(
    "/book",
    response_model=BookAppointmentResponse,
    summary="Prenota appuntamento su Google Calendar e DB"
)
async def book_appointment(
    work_order_id: int = Query(..., description="ID scheda lavori"),
    appointment_date: str = Query(..., description="Data appuntamento (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_async)
):
    """
    Prenota appuntamento per una scheda lavori:
    1. Valida che il cliente non abbia già un appuntamento
    2. Crea evento su Google Calendar (tutto il giorno)
    3. Salva data_appuntamento nel DB (work_orders.data_appuntamento)
    
    **Validazioni:**
    - Un solo appuntamento per cliente
    - Data nel futuro
    - Scheda lavori esiste
    
    **Risposta success:**
    ```json
    {
        "confirmed": true,
        "work_order_id": 123,
        "google_event_id": "abc123def456",
        "appointment_date": "2026-02-20",
        "saved_at": "2026-02-13T10:15:00"
    }
    ```
    """
    # 1. Validazione data formato
    try:
        appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato data non valido. Usa YYYY-MM-DD"
        )
    
    if appt_date < datetime.now().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La data appuntamento deve essere nel futuro"
        )
    
    # 2. Carica scheda lavori con relazioni
    result = await db.execute(
        select(WorkOrder)
        .filter(WorkOrder.id == work_order_id)
        .options(
            joinedload(WorkOrder.customer),
            joinedload(WorkOrder.vehicle)
        )
    )
    work_order = result.scalars().unique().first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheda lavori {work_order_id} non trovata"
        )
    
    # 3. VALIDAZIONE: Controlla che il cliente non abbia già un appuntamento nello STESSO GIORNO
    # (Un cliente può avere più appuntamenti, ma in giorni diversi)
    customer_id = work_order.customer_id
    existing_appt = await db.execute(
        select(WorkOrder).filter(
            WorkOrder.customer_id == customer_id,
            WorkOrder.data_appuntamento == appt_date,  # Controlla LO STESSO GIORNO
            WorkOrder.id != work_order_id  # Escludi scheda attuale (per modifica)
        )
    )
    
    if existing_appt.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Questo cliente ha già un appuntamento il giorno stesso. Scegli un altro giorno."
        )
    
    try:
        # 4. Crea evento Google Calendar (all-day event)
        service = await gc.get_calendar_service(db)
        
        customer_name = work_order.customer.full_name if work_order.customer else "Cliente sconosciuto"
        vehicle_info = work_order.vehicle.targa if work_order.vehicle else "Veicolo sconosciuto"
        
        event_body = {
            "summary": f"Scheda #{work_order.numero_scheda} - {customer_name}",
            "description": f"Veicolo: {vehicle_info}\nDanno: {work_order.valutazione_danno or 'Non specificato'}",
            "start": {"date": appointment_date},        # All-day event
            "end": {"date": appointment_date},          # All-day event (same day)
            "transparency": "opaque",
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60}  # 1 giorno prima
                ]
            }
        }
        
        created_event = service.events().insert(
            calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            body=event_body
        ).execute()
        
        google_event_id = created_event.get("id")
        print(f"✅ Evento Google creato: {google_event_id}")
        
    except Exception as e:
        print(f"❌ ERRORE creazione evento Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Errore creazione evento Google Calendar: {str(e)}"
        )
    
    try:
        # 5. Aggiorna DB
        work_order.data_appuntamento = appt_date
        work_order.google_event_id = google_event_id
        # data_fine_prevista per ora la lasciamo vuota (gestita quando definiamo durata intervento)
        
        db.add(work_order)
        await db.commit()
        await db.refresh(work_order)
        
        print(f"✅ Scheda {work_order_id} appuntamento prenotato: {appointment_date}")
        
        return BookAppointmentResponse(
            confirmed=True,
            work_order_id=work_order_id,
            google_event_id=google_event_id,
            appointment_date=appointment_date,
            saved_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        await db.rollback()
        print(f"❌ ERRORE booking DB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il salvataggio: {str(e)}"
        )


class CancelAppointmentResponse(BaseModel):
    """Risposta cancellazione appuntamento"""
    cancelled: bool
    work_order_id: int
    cancelled_at: str


@router.post(
    "/cancel",
    response_model=CancelAppointmentResponse,
    summary="Cancella appuntamento da Google Calendar e DB"
)
async def cancel_appointment(
    work_order_id: int = Query(..., description="ID scheda lavori"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_async)
):
    """
    Cancella appuntamento:
    1. Legge scheda lavori e google_event_id
    2. Cancella evento da Google Calendar
    3. Resetta data_appuntamento e google_event_id nel DB
    """
    try:
        # 1. Carica scheda lavori
        result = await db.execute(
            select(WorkOrder).filter(WorkOrder.id == work_order_id)
        )
        work_order = result.scalars().first()
        
        if not work_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheda lavori {work_order_id} non trovata"
            )
        
        # 2. Se esiste google_event_id, cancella da Google Calendar
        if work_order.google_event_id:
            try:
                service = await gc.get_calendar_service(db)
                service.events().delete(
                    calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
                    eventId=work_order.google_event_id
                ).execute()
                print(f"✅ Evento Google cancellato: {work_order.google_event_id}")
            except Exception as e:
                print(f"⚠️ ERRORE cancellazione Google: {str(e)}")
                # Continua comunque a resettare il DB
        
        # 3. Resetta DB
        work_order.data_appuntamento = None
        work_order.data_fine_prevista = None
        work_order.google_event_id = None
        
        db.add(work_order)
        await db.commit()
        await db.refresh(work_order)
        
        print(f"✅ Scheda {work_order_id} appuntamento cancellato")
        
        return CancelAppointmentResponse(
            cancelled=True,
            work_order_id=work_order_id,
            cancelled_at=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"❌ ERRORE cancel DB: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la cancellazione: {str(e)}"
        )
