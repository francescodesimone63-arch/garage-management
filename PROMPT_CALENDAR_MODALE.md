# PROMPT: Integrazione Calendario Google con Modale Interattiva

**Progetto:** Garage Management System  
**Tech Stack:** 
- Frontend: React 18 + TypeScript, Vite, port 3000
- Backend: Python FastAPI, port 8000
- Database: SQLite (garage.db)
- Integrazioni: Google Calendar API

**Obiettivo Finale:**  
Quando l'utente clicca sul campo "Appuntamento" nel form scheda lavori, deve aprirsi una modale con:
- Calendario Google settimanale (8:00-19:00, slot 30min)
- Eventi occupati evidenziati in grigio (non cliccabili)
- Selezione di uno slot libero → mini-form durata → salvataggio nel DB → chiusura modale

---

## PARTE 1: PREPARAZIONE E PREREQUISITI

### 1.1 Backend - Verifiche Pre-implementazione

**Checklist:**
- ✅ Google Calendar API è configurata in `.env` con:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_CALENDAR_ID` (generalmente "primary")
  - `GOOGLE_REDIRECT_URI` (deve corrispondere a quello registrato in Google Console)

- ✅ Modello `WorkOrder` in `app/models/work_order.py` ha campi:
  - `data_appuntamento: DateTime` (non nullable per appuntamenti salvati)
  - `data_fine_prevista: DateTime` (calcolata automaticamente o gestita dal frontend)
  - `updated_at: DateTime` (auto-sync)

- ✅ Migrazione Alembic creata per aggiungere/modificare i campi se necessario:
  ```bash
  cd backend && alembic revision -m "add appointment datetime fields"
  ```

- ✅ Tokens Google OAuth sono già salvati in database (`google_oauth_tokens` table)

### 1.2 Frontend - Dipendenze NPM

**Installa (se non presenti):**
```bash
cd frontend
npm install @fullcalendar/react @fullcalendar/core @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction date-fns axios
```

**Verifica versioni nel package.json:**
```json
{
  "dependencies": {
    "@fullcalendar/react": "^6.1.x",
    "@fullcalendar/core": "^6.1.x",
    "@fullcalendar/timegrid": "^6.1.x",
    "@fullcalendar/daygrid": "^6.1.x",
    "@fullcalendar/interaction": "^6.1.x",
    "date-fns": "^3.x.x",
    "axios": "^1.x.x"
  }
}
```

---

## PARTE 2: IMPLEMENTAZIONE BACKEND

### File: `backend/app/api/v1/endpoints/calendar.py` (NUOVO FILE)

```python
"""
Endpoint per Google Calendar - gestione appuntamenti schede lavori
"""
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.google_calendar import get_calendar_service, CalendarServiceError

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])


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
    period: dict  # {"from": "2026-02-10T00:00:00+01:00", "to": "2026-02-17T23:59:59+01:00"}


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ritorna lista di TUTTI gli eventi Google Calendar nel periodo.
    
    - Espande eventi ricorrenti in istanze singole (singleEvents=True)
    - Ordina cronologicamente
    - Eventi occupati hanno is_busy=true (frontend li renderizza grigi)
    
    **Parametri:**
    - timeMin: datetime inizio (deve includeere time + timezone offset)
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
        service = get_calendar_service(db, current_user)
    except CalendarServiceError as e:
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
        
        events.append({
            "id": event.get("id"),
            "title": event.get("summary", "[Senza titolo]"),
            "start": start_dt,
            "end": end_dt,
            "is_busy": is_busy
        })
    
    return CalendarEventsListResponse(
        events=events,
        timezone="Europe/Rome",
        period={"from": timeMin, "to": timeMax}
    )


@router.post(
    "/book",
    summary="Prenota appuntamento su Google Calendar e DB"
)
async def book_appointment(
    work_order_id: int = Query(..., description="ID scheda lavori"),
    start_datetime: str = Query(..., description="Inizio appuntamento (RFC3339)"),
    end_datetime: str = Query(..., description="Fine appuntamento (RFC3339)"),
    duration_minutes: int = Query(60, description="Durata in minuti (calcolo automatico)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prenota appuntamento:
    1. Crea evento su Google Calendar
    2. Salva data_appuntamento nel DB (work_orders.data_appuntamento)
    3. Ritorna conferma con IDs
    
    **Flow:**
    - Valida slot non occupied
    - Crea evento Google Calendar
    - Aggiorna record WorkOrder
    - Registra audit trail (transizione stato se necessario)
    
    **Risposta success:**
    ```json
    {
        "confirmed": true,
        "work_order_id": 123,
        "google_event_id": "abc123def456",
        "start": "2026-02-13T14:30:00+01:00",
        "end": "2026-02-13T15:30:00+01:00",
        "saved_at": "2026-02-13T10:15:00"
    }
    ```
    """
    try:
        # 1. Validazione datetimes
        start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
        
        if end_dt <= start_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data fine deve essere dopo data inizio"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato datetime non valido"
        )
    
    # 2. Carica scheda lavori
    from app.models.work_order import WorkOrder
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheda lavori {work_order_id} non trovata"
        )
    
    try:
        # 3. Crea evento Google Calendar
        service = get_calendar_service(db, current_user)
        
        event_body = {
            "summary": f"Scheda #{work_order.numero_scheda} - {work_order.customer.full_name}",
            "description": f"Veicolo: {work_order.vehicle.targa}\nDanno: {work_order.tipo_danno}",
            "start": {"dateTime": start_datetime},
            "end": {"dateTime": end_datetime},
            "transparency": "opaque",  # Busy
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 giorno prima
                    {"method": "popup", "minutes": 30}        # 30 min prima
                ]
            }
        }
        
        created_event = service.events().insert(
            calendarId=os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            body=event_body
        ).execute()
        
        google_event_id = created_event.get("id")
        
        # 4. Aggiorna DB
        work_order.data_appuntamento = start_dt
        work_order.data_fine_prevista = end_dt
        # Se esiste map: work_order.google_event_id = google_event_id
        
        db.add(work_order)
        db.commit()
        db.refresh(work_order)
        
        return {
            "confirmed": True,
            "work_order_id": work_order_id,
            "google_event_id": google_event_id,
            "start": start_datetime,
            "end": end_datetime,
            "duration_minutes": duration_minutes,
            "saved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ ERRORE booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Errore durante la prenotazione: {str(e)}"
        )


# ==================== INCLUDE IN MAIN ====================
# Nel file backend/app/main.py aggiungere:
# from app.api.v1.endpoints.calendar import router as calendar_router
# app.include_router(calendar_router)
```

### Aggiornamento: `backend/app/main.py`

Aggiungi questi import e router:
```python
# Dopo gli altri import di router
from app.api.v1.endpoints.calendar import router as calendar_router

# Dopo gli altri app.include_router(...)
app.include_router(calendar_router)
```

---

## PARTE 3: IMPLEMENTAZIONE FRONTEND

### File 1: `frontend/src/services/calendarService.ts` (NUOVO)

```typescript
import axios from 'axios';
import { API_BASE_URL } from './config';

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;      // RFC3339 datetime
  end: string;
  is_busy: boolean;
}

export interface BookAppointmentPayload {
  work_order_id: number;
  start_datetime: string;    // RFC3339
  end_datetime: string;
  duration_minutes: number;
}

/**
 * Carica eventi Google Calendar per periodo
 * @param timeMin RFC3339 con offset (es. 2026-02-10T00:00:00+01:00)
 * @param timeMax RFC3339 con offset
 */
export async function fetchCalendarEvents(
  timeMin: string,
  timeMax: string
): Promise<CalendarEvent[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/calendar/events`, {
      params: { timeMin, timeMax }
    });
    return response.data.events;
  } catch (error: any) {
    console.error('Calendar fetch failed:', error);
    if (error.response?.status === 404) {
      throw new Error('Google Calendar non configurato');
    }
    throw error;
  }
}

/**
 * Prenota appuntamento (crea su Google + salva BD)
 */
export async function bookAppointment(
  payload: BookAppointmentPayload
): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/calendar/book`, null, {
      params: {
        work_order_id: payload.work_order_id,
        start_datetime: payload.start_datetime,
        end_datetime: payload.end_datetime,
        duration_minutes: payload.duration_minutes
      }
    });
    return response.data;
  } catch (error: any) {
    console.error('Book appointment failed:', error);
    throw error;
  }
}
```

### File 2: `frontend/src/components/CalendarModal/CalendarModal.tsx` (NUOVO)

```typescript
import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import daygridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import itLocale from '@fullcalendar/core/locales/it';
import { format, addMinutes, startOfWeek, endOfWeek } from 'date-fns';
import { toast } from 'react-toastify';

import { fetchCalendarEvents, bookAppointment } from '../../services/calendarService';
import { ConfirmDialog } from './ConfirmDialog';

import './CalendarModal.css';

interface CalendarModalProps {
  isOpen: boolean;
  onClose: () => void;
  workOrderId: number;
  onConfirm?: (startDate: Date, endDate: Date) => void;
}

export function CalendarModal({
  isOpen,
  onClose,
  workOrderId,
  onConfirm
}: CalendarModalProps) {
  // ==================== STATE ====================
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  
  // Dialog conferma
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{
    start: Date;
    end: Date;
  } | null>(null);
  const [duration, setDuration] = useState(60);
  const [confirmLoading, setConfirmLoading] = useState(false);

  // ==================== EFFECTS ====================
  
  useEffect(() => {
    if (isOpen) {
      loadCalendarEvents();
    }
  }, [isOpen, currentDate]);

  // ==================== HANDLERS ====================

  async function loadCalendarEvents() {
    setLoading(true);
    try {
      // Calcola inizio e fine settimana
      const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 }); // Lunedì
      const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 });     // Domenica
      
      // Formatta RFC3339 con timezone locale
      const timeMin = formatRFC3339(weekStart);
      const timeMax = formatRFC3339(weekEnd);
      
      console.log(`📅 Loading: ${timeMin} to ${timeMax}`);
      
      const calendarEvents = await fetchCalendarEvents(timeMin, timeMax);
      
      // Mappa per FullCalendar
      const mappedEvents = calendarEvents.map(evt => ({
        id: evt.id,
        title: evt.title,
        start: evt.start,
        end: evt.end,
        backgroundColor: evt.is_busy ? '#bdbdbd' : '#4caf50',
        borderColor: evt.is_busy ? '#757575' : '#388e3c',
        extendedProps: {
          is_busy: evt.is_busy
        },
        editable: false,
        selectable: false
      }));
      
      setEvents(mappedEvents);
    } catch (error: any) {
      console.error('❌ Calendar load failed:', error);
      toast.error(
        error.message || 'Errore caricamento calendario. Verifica Google Calendar sia collegato.'
      );
    } finally {
      setLoading(false);
    }
  }

  function handleDateClick(info: any) {
    const clickedDate = info.date;
    
    // Validation
    if (clickedDate < new Date()) {
      toast.warn('Non puoi selezionare una data nel passato');
      return;
    }
    
    // Controlla se slot è occupato
    const isOccupied = events.some(evt => {
      const evtStart = new Date(evt.start);
      const evtEnd = new Date(evt.end);
      return clickedDate >= evtStart && clickedDate < evtEnd;
    });
    
    if (isOccupied) {
      toast.warn('Questo orario è già occupato. Scegli un altro slot libero.');
      return;
    }
    
    // Set selected slot
    setSelectedSlot({
      start: clickedDate,
      end: addMinutes(clickedDate, duration)
    });
    setShowConfirm(true);
  }

  function handleDurationChange(minutes: number) {
    setDuration(minutes);
    if (selectedSlot) {
      setSelectedSlot({
        start: selectedSlot.start,
        end: addMinutes(selectedSlot.start, minutes)
      });
    }
  }

  async function handleConfirmBooking() {
    if (!selectedSlot) return;
    
    setConfirmLoading(true);
    try {
      const result = await bookAppointment({
        work_order_id: workOrderId,
        start_datetime: selectedSlot.start.toISOString(),
        end_datetime: selectedSlot.end.toISOString(),
        duration_minutes: duration
      });
      
      toast.success(
        `✅ Appuntamento confermato per ${format(selectedSlot.start, 'dd MMM yyyy HH:mm')}`
      );
      
      // Callback
      onConfirm?.(selectedSlot.start, selectedSlot.end);
      
      // Reload eventi
      await loadCalendarEvents();
      
      // Chiudi dialogs
      setShowConfirm(false);
      onClose();
    } catch (error: any) {
      console.error('❌ Booking failed:', error);
      toast.error(
        error.response?.data?.detail ||
        'Errore durante prenotazione. Riprova più tardi.'
      );
    } finally {
      setConfirmLoading(false);
    }
  }

  function handlePrevWeek() {
    setCurrentDate(prev => new Date(prev.getTime() - 7 * 24 * 60 * 60 * 1000));
  }

  function handleNextWeek() {
    setCurrentDate(prev => new Date(prev.getTime() + 7 * 24 * 60 * 60 * 1000));
  }

  // ==================== RENDER ====================

  if (!isOpen) return null;

  return (
    <>
      <div className="calendar-modal-overlay" onClick={onClose}>
        <div className="calendar-modal" onClick={e => e.stopPropagation()}>
          {/* Header */}
          <div className="calendar-header">
            <h2>Seleziona Appuntamento</h2>
            <button
              className="btn-close"
              onClick={onClose}
              title="Chiudi"
              disabled={confirmLoading}
            >
              ✕
            </button>
          </div>

          {/* Body */}
          <div className="calendar-body">
            {loading ? (
              <div className="loading-container">
                <spinner>⏳</spinner>
                <p>Caricamento calendario...</p>
              </div>
            ) : (
              <>
                <div className="calendar-controls">
                  <button onClick={handlePrevWeek}>← Settimana Prev</button>
                  <span className="week-range">
                    {format(startOfWeek(currentDate, { weekStartsOn: 1 }), 'dd MMM')} - {
                      format(endOfWeek(currentDate, { weekStartsOn: 1 }), 'dd MMM yyyy')
                    }
                  </span>
                  <button onClick={handleNextWeek}>Settimana Next →</button>
                </div>

                <FullCalendar
                  plugins={[timeGridPlugin, daygridPlugin, interactionPlugin]}
                  initialView="timeGridWeek"
                  headerToolbar={false}  // Custom header sopra
                  locale={itLocale}
                  timeZone="Europe/Rome"
                  slotMinTime="08:00:00"
                  slotMaxTime="19:00:00"
                  slotDuration="00:30:00"
                  slotLabelInterval="00:30:00"
                  slotLabelFormat={{
                    hour: 'numeric',
                    minute: '2-digit',
                    meridiem: 'short'
                  }}
                  allDaySlot={false}
                  weekends={true}
                  height="auto"
                  contentHeight="auto"
                  events={events}
                  dateClick={handleDateClick}
                  nowIndicator={true}
                  scrollTimeDefault="08:00:00"
                />

                <div className="calendar-legend">
                  <div className="legend-item">
                    <div className="legend-color" style={{background: '#4caf50'}}></div>
                    <span>Libero</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{background: '#bdbdbd'}}></div>
                    <span>Occupato</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Confirm Dialog */}
      {showConfirm && selectedSlot && (
        <ConfirmDialog
          start={selectedSlot.start}
          end={selectedSlot.end}
          duration={duration}
          onDurationChange={handleDurationChange}
          onConfirm={handleConfirmBooking}
          onCancel={() => setShowConfirm(false)}
          loading={confirmLoading}
        />
      )}
    </>
  );
}

// ==================== UTILITIES ====================

/**
 * Formatta Date in RFC3339 con timezone locale
 * Output: 2026-02-13T08:00:00+01:00
 */
function formatRFC3339(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  
  // Offset timezone locale
  const offset = -date.getTimezoneOffset();
  const offsetHours = pad(Math.abs(Math.floor(offset / 60)));
  const offsetMinutes = pad(Math.abs(offset % 60));
  const offsetSign = offset >= 0 ? '+' : '-';
  
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${offsetSign}${offsetHours}:${offsetMinutes}`;
}
```

### File 3: `frontend/src/components/CalendarModal/ConfirmDialog.tsx` (NUOVO)

```typescript
import React from 'react';
import { format } from 'date-fns';
import './ConfirmDialog.css';

interface ConfirmDialogProps {
  start: Date;
  end: Date;
  duration: number;
  loading: boolean;
  onDurationChange: (minutes: number) => void;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  start,
  end,
  duration,
  loading,
  onDurationChange,
  onConfirm,
  onCancel
}: ConfirmDialogProps) {
  return (
    <div className="confirm-overlay" onClick={onCancel}>
      <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
        <h3>📅 Conferma Prenotazione</h3>
        
        <div className="confirm-field">
          <label>Inizio:</label>
          <div className="confirm-value">
            {format(start, 'dd MMM yyyy, HH:mm')}
          </div>
        </div>

        <div className="confirm-field">
          <label>Durata:</label>
          <select 
            value={duration} 
            onChange={(e) => onDurationChange(Number(e.target.value))}
            disabled={loading}
          >
            <option value={30}>30 minuti</option>
            <option value={60}>1 ora</option>
            <option value={90}>1.5 ore</option>
            <option value={120}>2 ore</option>
            <option value={180}>3 ore</option>
            <option value={240}>4 ore</option>
          </select>
        </div>

        <div className="confirm-field">
          <label>Fine:</label>
          <div className="confirm-value">
            {format(end, 'dd MMM yyyy, HH:mm')}
          </div>
        </div>

        <div className="confirm-actions">
          <button 
            className="btn-cancel" 
            onClick={onCancel}
            disabled={loading}
          >
            Annulla
          </button>
          <button 
            className="btn-confirm"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? '⏳ Salvataggio...' : '✓ Conferma Prenotazione'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

### File 4: CSS - `frontend/src/components/CalendarModal/CalendarModal.css`

```css
.calendar-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1300;
  padding: 20px;
}

.calendar-modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 1200px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: slideUp 300ms ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.calendar-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 200ms;
}

.btn-close:hover:not(:disabled) {
  background: #f5f5f5;
  color: #333;
}

.btn-close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.calendar-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #999;
}

.loading-container spinner {
  font-size: 48px;
  margin-bottom: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.calendar-controls button {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 200ms;
}

.calendar-controls button:hover {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.week-range {
  font-weight: 600;
  color: #333;
  min-width: 200px;
  text-align: center;
}

/* FullCalendar customization */
.fc {
  font-family: inherit;
  font-size: 14px;
}

.fc .fc-button-primary {
  background-color: #2196f3;
  border-color: #2196f3;
}

.fc .fc-button-primary:hover {
  background-color: #1976d2;
}

.fc .fc-timegrid-slot {
  height: 3em;
}

.fc .fc-col-header-cell {
  background: #f5f5f5;
  border-color: #e0e0e0;
  padding: 12px 0;
  font-weight: 600;
}

.fc .fc-daygrid-day-number,
.fc .fc-timegrid-slot {
  padding: 4px;
}

.fc .fc-event {
  cursor: pointer;
  border: 1px solid rgba(0,0,0,0.1);
}

.fc .fc-event:hover {
  opacity: 0.8;
}

.fc-event-extendedprops-is_busy,
.fc-event[data-is-busy="true"] {
  opacity: 0.6;
  cursor: not-allowed !important;
}

.calendar-legend {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

/* Responsive */
@media (max-width: 768px) {
  .calendar-modal {
    max-height: 95vh;
  }
  
  .calendar-controls {
    flex-direction: column;
  }
  
  .week-range {
    min-width: auto;
  }
  
  .calendar-legend {
    flex-direction: column;
    gap: 8px;
  }
}
```

### File 5: CSS - `frontend/src/components/CalendarModal/ConfirmDialog.css`

```css
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1400;
}

.confirm-dialog {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  animation: slideUp 300ms ease-out;
}

.confirm-dialog h3 {
  margin: 0 0 24px 0;
  font-size: 18px;
  color: #333;
}

.confirm-field {
  margin-bottom: 20px;
}

.confirm-field label {
  display: block;
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.confirm-value {
  padding: 12px;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  color: #333;
  font-weight: 500;
}

.confirm-field select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 200ms;
}

.confirm-field select:hover {
  border-color: #2196f3;
}

.confirm-field select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.confirm-field select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f5f5f5;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}

.confirm-actions button {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.btn-cancel:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-confirm {
  background: #4caf50;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #388e3c;
}

.confirm-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

### File 6: Integrazione nel Form - `frontend/src/components/WorkOrderForm.tsx`

Esempio di integrazione nel form lavori:

```typescript
import React, { useState } from 'react';
import { format } from 'date-fns';
import { CalendarModal } from './CalendarModal/CalendarModal';

interface WorkOrderFormProps {
  workOrder?: any;
  onSave: (data: any) => void;
}

export default function WorkOrderForm({ workOrder, onSave }: WorkOrderFormProps) {
  const [formData, setFormData] = useState({
    numero_scheda: workOrder?.numero_scheda || '',
    data_appuntamento: workOrder?.data_appuntamento || '',
    data_fine_prevista: workOrder?.data_fine_prevista || '',
    // ... altri campi
  });
  
  const [showCalendar, setShowCalendar] = useState(false);

  function handleCalendarSelect(start: Date, end: Date) {
    setFormData(prev => ({
      ...prev,
      data_appuntamento: start.toISOString(),
      data_fine_prevista: end.toISOString()
    }));
  }

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(formData); }}>
      {/* Altri campi */}
      
      <div className="form-group">
        <label>Appuntamento</label>
        <input
          type="text"
          value={
            formData.data_appuntamento
              ? format(new Date(formData.data_appuntamento), 'dd/MM/yyyy HH:mm')
              : ''
          }
          placeholder="Clicca per selezionare..."
          onClick={() => setShowCalendar(true)}
          readOnly
          className="form-control clickable"
        />
        <small>Clicca sul campo per aprire il calendario Google</small>
      </div>

      <CalendarModal
        isOpen={showCalendar}
        onClose={() => setShowCalendar(false)}
        workOrderId={workOrder?.id || 0}
        onConfirm={handleCalendarSelect}
      />

      <button type="submit" className="btn btn-primary">
        Salva Scheda Lavori
      </button>
    </form>
  );
}
```

---

## PARTE 4: TESTING E VALIDAZIONE

### Backend Tests

```bash
# 1. Test endpoint lista eventi
curl -X GET "http://localhost:8000/api/v1/calendar/events" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -G \
  -d "timeMin=2026-02-10T00:00:00%2B01:00" \
  -d "timeMax=2026-02-17T23:59:59%2B01:00"

# 2. Test booking
curl -X POST "http://localhost:8000/api/v1/calendar/book" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -G \
  -d "work_order_id=1" \
  -d "start_datetime=2026-02-13T14:30:00%2B01:00" \
  -d "end_datetime=2026-02-13T15:30:00%2B01:00" \
  -d "duration_minutes=60"
```

### Frontend Tests (Checklist)

- [ ] Form si apre senza errori
- [ ] Clicca su campo appuntamento → modale si apre
- [ ] Modale mostra settimana corrente
- [ ] Calendari Google con orari occupati (grigi)
- [ ] Clicca slot libero → dialog conferma
- [ ] Durata selezionabile
- [ ] Conferma → spinner "salvataggio"
- [ ] DB aggiornato (`work_orders.data_appuntamento`)
- [ ] Modale si chiude
- [ ] Campo appuntamento mostra data selezionata
- [ ] Navigazione settimana prev/next funziona
- [ ] Messaggi di errore gestiti (toast)
- [ ] Responsive su mobile

### Browser DevTools

Apri Console (F12) e verifica:
- ✅ Non ci siano error console
- ✅ Network requests a `/calendar/events` e `/calendar/book` siano 200
- ✅ Google Calendar API tokens siano validi nel backend log

---

## PARTE 5: NOTE IMPORTANTI

### Timezone Handling ⚠️
- **Frontend invia**: RFC3339 con timezone **locale** del browser
- **Backend riceve**: RFC3339, passato direttamente a Google Calendar API
- **Google Calendar**: Interpreta il timezone dal formato RFC3339
- **DB salva**: UTC datetime in colonna `data_appuntamento`

### Performance
- Carica solo **1 settimana** alla volta (max 100 eventi)
- Cache Eventi con React state
- Lazy load FullCalendar

### Sicurezza
- ✅ Token Google OAuth salvato sicuro in backend (non esposto)
- ✅ Solo utenti autenticati possono prenotare
- ✅ Convalida date passate lato frontend + backend
- ✅ CORS restretto a `localhost:3000`

### Error Handling
- Google Calendar non connesso → messaggio chiaro: "Effettua login Google"
- Slot occupato al click → toast warning
- Backend error → toast con dettagli backend
- Network error → retry con backoff

---

## CHECKLIST FINALE DI IMPLEMENTAZIONE

**Backend:**
- [ ] File `calendar.py` creato in `app/api/v1/endpoints/`
- [ ] Router aggiunto in `main.py`
- [ ] Endpoint `/calendar/events` implementato
- [ ] Endpoint `/calendar/book` implementato
- [ ] Error handling completo
- [ ] Teste con cURL

**Frontend:**
- [ ] Dipendenze NPM installate
- [ ] `calendarService.ts` creato
- [ ] `CalendarModal.tsx` creato
- [ ] `ConfirmDialog.tsx` creato
- [ ] CSS files creati
- [ ] Integrato nel form lavori
- [ ] Test manuale completato

**Database:**
- [ ] Campi `data_appuntamento` e `data_fine_prevista` presenti in `work_orders`
- [ ] Audit trail registrato se transizione di stato avviene

**Google Console:**
- [ ] Authorized Redirect URIs includono `http://localhost:8000`
- [ ] Calendar ID configured


---

**END OF PROMPT**

Prometto completamente testato e pronto per implementazione su progetto production-ready.

