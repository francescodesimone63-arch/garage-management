import { useState, useEffect, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import daygridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import itLocale from '@fullcalendar/core/locales/it';
import { message, Modal } from 'antd';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { it } from 'date-fns/locale';

import { fetchCalendarEvents, bookAppointment, cancelAppointment } from '../../services/calendarService';

import './CalendarModal.css';

interface CalendarModalProps {
  onCancel: () => void;
  onConfirm?: (appointmentData: { appointment_date: string }) => void;
  workOrderId?: number;
  returnUrl?: string;
  currentAppointmentDate?: string;  // Current appointment date in YYYY-MM-DD format
}

export function CalendarModal({
  onCancel,
  onConfirm,
  workOrderId = 1,
  returnUrl,
  currentAppointmentDate
}: CalendarModalProps) {
  // ==================== REFS ====================
  // Track if we've already navigated to appointment week
  const navigationAttemptedRef = useRef(false);
  
  // ==================== STATE ====================
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState(() => {
    if (currentAppointmentDate) {
      const dateStr = currentAppointmentDate.split('T')[0] || currentAppointmentDate.split(' ')[0];
      return new Date(dateStr + 'T00:00:00Z');
    }
    return new Date();
  });
  const [oauthError, setOauthError] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);

  // ==================== EFFECTS ====================
  
  useEffect(() => {
    loadCalendarEvents();
  }, [currentDate]);

  // ==================== HANDLERS ====================

  async function loadCalendarEvents() {
    setLoading(true);
    setOauthError(false);
    try {
      // Calcola inizio e fine settimana
      const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 }); // Lunedì
      const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 });     // Domenica
      
      // Formatta RFC3339 con timezone locale
      const timeMin = formatRFC3339(weekStart);
      const timeMax = formatRFC3339(weekEnd);
      
      console.log(`📅 Loading: ${timeMin} to ${timeMax}`);
      console.log(`📅 Current appointment date prop: ${currentAppointmentDate}`);
      
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
      
      // Aggiungi evento visuale per la data di appuntamento attuale se presente
      if (currentAppointmentDate) {
        // Parse appointment date - handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:mm:ss" formats
        const dateStr = currentAppointmentDate.split('T')[0] || currentAppointmentDate.split(' ')[0];
        console.log(`📅 Parsed appointment date: ${dateStr}`);
        
        // Create appointment date range (all day event)
        const appointmentStart = new Date(dateStr + 'T00:00:00Z');
        const appointmentEnd = new Date(dateStr + 'T23:59:59Z');
        
        // Normalize week dates to UTC for comparison
        const weekStartUTC = new Date(weekStart);
        weekStartUTC.setUTCHours(0, 0, 0, 0);
        const weekEndUTC = new Date(weekEnd);
        weekEndUTC.setUTCHours(23, 59, 59, 999);
        
        const appointmentDateOnly = new Date(appointmentStart);
        appointmentDateOnly.setUTCHours(0, 0, 0, 0);
        
        console.log(`📅 Week range: ${weekStartUTC.toISOString()} to ${weekEndUTC.toISOString()}`);
        console.log(`📅 Appointment: ${appointmentDateOnly.toISOString()}`);
        
        // Verifica se la data di appuntamento è nella settimana attuale
        if (appointmentDateOnly >= weekStartUTC && appointmentDateOnly <= weekEndUTC) {
          console.log('✅ Appointment is in current week - adding to calendar');
          mappedEvents.push({
            id: 'current-appointment',
            title: '📅 Prenotato',
            start: appointmentStart,
            end: appointmentEnd,
            backgroundColor: '#E3F2FD',
            borderColor: '#1976D2',
            textColor: '#1976D2',
            extendedProps: {
              is_current: true
            },
            editable: false,
            selectable: false
          });
        } else {
          console.log('❌ Appointment is NOT in current week');
        }
      }
      
      console.log(`📅 Total events to display: ${mappedEvents.length}`);
      setEvents(mappedEvents);
    } catch (error: any) {
      console.error('❌ Calendar load failed:', error);
      
      // Rileva errore OAuth
      if (error.message?.includes('Google Calendar non configurato') || 
          error.message?.includes('Effettua')) {
        setOauthError(true);
        setEvents([]);
        return;
      }
      
      message.error(
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
      message.warning('Non puoi selezionare una data nel passato');
      return;
    }
    
    // Controlla se la data cliccata è la stessa dell'appuntamento attuale
    const isCurrentAppointmentDate = currentAppointmentDate && (() => {
      const dateStr = currentAppointmentDate.split('T')[0] || currentAppointmentDate.split(' ')[0];
      const appointmentDate = new Date(dateStr);
      const clickedDateOnly = new Date(clickedDate);
      // Confronta solo la data, non l'orario
      return appointmentDate.toISOString().split('T')[0] === clickedDateOnly.toISOString().split('T')[0];
    })();
    
    // Se è una data diversa, controlla se slot è occupato (escludendo l'appuntamento attuale)
    if (!isCurrentAppointmentDate) {
      const isOccupied = events.some(event => {
        // Ignora l'evento dell'appuntamento attuale
        if (event.id === 'current-appointment') return false;
        
        const evtStart = new Date(event.start);
        const evtEnd = new Date(event.end);
        return clickedDate >= evtStart && clickedDate < evtEnd;
      });
      
      if (isOccupied) {
        message.warning('Questo orario è già occupato. Scegli un altro slot libero.');
        return;
      }
    }
    
    // Se c'è un appuntamento precedente, cancellalo prima di creare il nuovo
    // (sia che sia la stessa data con ore diverse, sia data diversa)
    if (currentAppointmentDate && workOrderId) {
      handleCancelAndRebook(clickedDate);
    } else {
      // Nessun appuntamento precedente, procedi normalmente
      setSelectedSlot({
        start: clickedDate,
        end: addMinutes(clickedDate, duration)
      });
      setShowConfirm(true);
    }
  }

  async function handleCancelAndRebook(newDate: Date) {
    try {
      console.log('📅 Cancellazione appuntamento precedente e rebook con new date...');
      await cancelAppointment(workOrderId);
      
      // Set selected slot con la nuova data
      setSelectedSlot({
        start: newDate,
        end: addMinutes(newDate, duration)
      });
      setShowConfirm(true);
    } catch (error: any) {
      console.error('❌ Cancel failed:', error);
      message.error('Errore cancellazione appuntamento precedente. Riprova.');
    }
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
      await bookAppointment({
        work_order_id: workOrderId,
        start_datetime: selectedSlot.start.toISOString(),
        end_datetime: selectedSlot.end.toISOString(),
        duration_minutes: duration
      });
      
      message.success(
        `✅ Appuntamento confermato per ${format(selectedSlot.start, 'dd MMM yyyy HH:mm', { locale: it })}`
      );
      
      // Callback with ISO strings
      onConfirm?.({
        start_datetime: selectedSlot.start.toISOString(),
        end_datetime: selectedSlot.end.toISOString()
      });
      
      // Reload eventi
      await loadCalendarEvents();
      
      // Chiudi dialogs
      setShowConfirm(false);
      onCancel();
    } catch (error: any) {
      console.error('❌ Booking failed:', error);
      message.error(
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

  return (
    <>
      <div className="calendar-modal-overlay" onClick={onCancel}>
        <div className="calendar-modal" onClick={e => e.stopPropagation()}>
          {/* Header */}
          <div className="calendar-header">
            <h2>Seleziona Appuntamento</h2>
            <button
              className="btn-close"
              onClick={onCancel}
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
                <div className="spinner">⏳</div>
                <p>Caricamento calendario...</p>
              </div>
            ) : oauthError ? (
              <div className="oauth-error-container">
                <div className="error-icon">🔐</div>
                <h3>Google Calendar non configurato</h3>
                <p>Per selezionare gli appuntamenti, devi collegare Google Calendar.</p>
                <button
                  className="btn-oauth"
                  onClick={() => {
                    // Use provided returnUrl, or fall back to current location
                    const urlToReturn = returnUrl || (window.location.pathname + (window.location.search || ''));
                    
                    // Remove any previous calendar_auth parameter (handles both ? and & prefixes)
                    // This regex removes the parameter even if it was malformed with & prefix
                    const cleanUrl = urlToReturn.replace(/[?&]?calendar_auth=[^&]*/g, '').replace(/\?&/, '?');
                    
                    const encodedReturn = encodeURIComponent(cleanUrl);
                    
                    // Reindirizza a Google OAuth con return_url nel backend
                    window.location.href = `http://localhost:8000/api/v1/google/oauth/authorize?return_url=${encodedReturn}`;
                  }}
                >
                  🔗 Accedi con Google
                </button>
              </div>
            ) : (
              <>
                <div className="calendar-controls">
                  <button onClick={handlePrevWeek} disabled={loading}>← Settimana Prev</button>
                  <span className="week-range">
                    {format(startOfWeek(currentDate, { weekStartsOn: 1 }), 'dd MMM', { locale: it })} - {
                      format(endOfWeek(currentDate, { weekStartsOn: 1 }), 'dd MMM yyyy', { locale: it })
                    }
                  </span>
                  <button onClick={handleNextWeek} disabled={loading}>Settimana Next →</button>
                </div>

                <FullCalendar
                  plugins={[timeGridPlugin, daygridPlugin, interactionPlugin]}
                  initialView="timeGridWeek"
                  headerToolbar={{}}
                  locale={itLocale}
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
                  events={events}
                  dateClick={handleDateClick}
                  nowIndicator={true}
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
                  {currentAppointmentDate && (
                    <div className="legend-item">
                      <div className="legend-color" style={{background: '#E3F2FD', border: '2px solid #1976D2'}}></div>
                      <span>Data Appuntamento Attuale</span>
                    </div>
                  )}
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
