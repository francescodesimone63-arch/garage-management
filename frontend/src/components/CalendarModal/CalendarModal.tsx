import { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import daygridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import itLocale from '@fullcalendar/core/locales/it';
import { message, Modal, Button } from 'antd';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { it } from 'date-fns/locale';

import { bookAppointment, cancelAppointment, fetchAllAppointmentsForMonth, checkOAuthStatus } from '../../services/calendarService';

import './CalendarModal.css';

interface CalendarModalProps {
  onCancel: () => void;
  onConfirm?: (appointmentData: { appointment_date: string }) => void;
  workOrderId?: number;
  returnUrl?: string;
  currentAppointmentDate?: string;
  customerName?: string;
  currentCustomerId?: number;  // Per distinguere gli appuntamenti del cliente corrente
}

export function CalendarModal({
  onCancel,
  onConfirm,
  workOrderId = 1,
  returnUrl,
  currentAppointmentDate,
  customerName,
  currentCustomerId
}: CalendarModalProps) {
  // ==================== STATE ====================
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [oauthError, setOauthError] = useState(false);
  const [confirmLoading, setConfirmLoading] = useState(false);

  // ==================== HELPERS ====================

  const redirectToGoogleOAuth = () => {
    const urlToReturn = returnUrl || (window.location.pathname + (window.location.search || ''));
    const cleanUrl = urlToReturn
      .replace(/[?&]?calendar_auth=[^&]*/g, '')
      .replace(/\?&/, '?');
    const encodedReturn = encodeURIComponent(cleanUrl);
    window.location.href = `http://localhost:8000/api/v1/google/oauth/authorize?return_url=${encodedReturn}`;
  };

  // ==================== EFFECTS ====================

  useEffect(() => {
    loadCalendarEvents();
  }, [currentDate, currentAppointmentDate, customerName, currentCustomerId]);

  // Navigate to appointment month when it's provided
  useEffect(() => {
    if (currentAppointmentDate) {
      const apptDateStr = currentAppointmentDate.split('T')[0] || currentAppointmentDate.split(' ')[0];
      try {
        const apptDate = new Date(apptDateStr + 'T00:00:00');
        // Navigate to the appointment month if it's different from current
        setCurrentDate(new Date(apptDate.getFullYear(), apptDate.getMonth(), 1));
      } catch (error) {
        console.error('❌ Error parsing appointment date:', error);
      }
    }
  }, [currentAppointmentDate]);

  // ==================== HANDLERS ====================

  async function loadCalendarEvents() {
    setLoading(true);
    setOauthError(false);
    
    try {
      // Prima controlla se Google OAuth è configurato
      const oauthStatus = await checkOAuthStatus();
      if (!oauthStatus.configured) {
        console.log('🔑 Google OAuth non configurato');
        setOauthError(true);
        setLoading(false);
        return;
      }

      const calendarEvents: any[] = [];
      
      // 1. Carica il mese corrente
      const month = currentDate.getMonth() + 1;  // getMonth() è 0-based
      const year = currentDate.getFullYear();
      
      // 2. Carica TUTTI gli appuntamenti del mese
      const allAppointments = await fetchAllAppointmentsForMonth(month, year);
      console.log(`📅 Appuntamenti totali nel mese: ${allAppointments.length}`, allAppointments);
      
      // 3. Aggiungi appuntamenti di ALTRI clienti (NON cliccabili)
      for (const appt of allAppointments) {
        if (appt.customer_id !== currentCustomerId) {
          // Appuntamento di un altro cliente - VISIBILE ma NON cliccabile
          calendarEvents.push({
            id: `other-appointment-${appt.work_order_id}`,
            title: `📅 ${appt.customer_name}`,
            date: appt.appointment_date,
            backgroundColor: '#F5F5F5',        // Grigio chiaro
            borderColor: '#BDBDBD',            // Bordo grigio
            textColor: '#757575',              // Testo grigio
            editable: false,
            selectable: false,
            // Impedisci click su eventi di altri clienti
            eventClick: () => {}
          });
        }
      }
      
      // 4. Aggiungi appuntamento del cliente CORRENTE (CLICCABILE)
      if (currentAppointmentDate) {
        const dateStr = currentAppointmentDate.split('T')[0] || currentAppointmentDate.split(' ')[0];
        const eventTitle = customerName ? `📅 ${customerName}` : '📅 Prenotato';
        console.log(`📅 Appointment date: ${dateStr} - Customer: ${customerName || 'N/A'}`);
        
        calendarEvents.push({
          id: 'current-appointment',
          title: eventTitle,
          date: dateStr,
          backgroundColor: '#E3F2FD',
          borderColor: '#1976D2',
          textColor: '#1976D2',
          editable: false,
          selectable: false
        });
      }
      
      setEvents(calendarEvents);
    } catch (error: any) {
      console.error('❌ Calendar load failed:', error);

      const msg = error?.message as string | undefined;
      const isOAuthMissing =
        msg?.includes('Google Calendar non è ancora collegato') ||
        msg?.includes('Google Calendar non configurato') ||
        error?.response?.status === 502;

      if (isOAuthMissing) {
        setOauthError(true);
      } else {
        message.error(
          msg || 'Errore caricamento calendario. Verifica Google Calendar sia collegato.'
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function handleDateClick(info: any) {
    const clickedDate = info.date;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    console.log(`📅 Clicked date: ${clickedDate.toISOString().split('T')[0]}`);
    
    // Validation: no past dates
    if (clickedDate < today) {
      message.warning('Non puoi selezionare una data nel passato');
      return;
    }
    
    // Format the clicked date as YYYY-MM-DD
    const formattedDate = format(clickedDate, 'yyyy-MM-dd');
    
    // Get current appointment date in YYYY-MM-DD format
    const currentApptDateStr = currentAppointmentDate?.split('T')[0] || currentAppointmentDate?.split(' ')[0];
    
    // Check if clicking same date as appointment
    if (currentApptDateStr && currentApptDateStr === formattedDate) {
      // Stesso giorno, solo conferma
      console.log('📅 Stessa data - semplice conferma');
      Modal.confirm({
        title: 'Conferma Appuntamento',
        content: `Confermi l'appuntamento per il ${format(clickedDate, 'dd MMMM yyyy', { locale: it })}?`,
        okText: 'Conferma',
        cancelText: 'Annulla',
        loading: confirmLoading,
        onOk: () => handleBookAppointment(formattedDate)
      });
    } else if (currentApptDateStr) {
      // Data diversa - cancella il vecchio e prenota il nuovo
      console.log('📅 Data diversa - cancella vecchio e prenota nuovo');
      Modal.confirm({
        title: 'Modifica Appuntamento',
        content: `Vuoi spostare l'appuntamento dal ${currentApptDateStr} al ${format(clickedDate, 'dd MMMM yyyy', { locale: it })}?`,
        okText: 'Sposta',
        cancelText: 'Annulla',
        loading: confirmLoading,
        onOk: () => handleCancelAndRebook(formattedDate)
      });
    } else {
      // Nessun appuntamento precedente
      console.log('📅 Primo appuntamento');
      Modal.confirm({
        title: 'Prenota Appuntamento',
        content: `Prenota per il ${format(clickedDate, 'dd MMMM yyyy', { locale: it })}?`,
        okText: 'Prenota',
        cancelText: 'Annulla',
        loading: confirmLoading,
        onOk: () => handleBookAppointment(formattedDate)
      });
    }
  }

  async function handleBookAppointment(appointmentDate: string) {
    setConfirmLoading(true);
    try {
      await bookAppointment({
        work_order_id: workOrderId,
        appointment_date: appointmentDate
      });
      
      message.success(`✅ Appuntamento confermato per ${appointmentDate}`);
      
      onConfirm?.({
        appointment_date: appointmentDate
      });
      
      await loadCalendarEvents();
      onCancel();
    } catch (error: any) {
      console.error('❌ Booking failed:', error);
      const msg = error?.message as string | undefined;

      if (msg?.includes('Google Calendar non è ancora collegato')) {
        Modal.confirm({
          title: 'Collega Google Calendar',
          content:
            'Per prenotare un appuntamento devi prima collegare Google Calendar. Vuoi procedere al login con Google?',
          okText: 'Accedi con Google',
          cancelText: 'Annulla',
          onOk: () => redirectToGoogleOAuth(),
        });
      } else {
        message.error(msg || 'Errore durante la prenotazione.');
      }
    } finally {
      setConfirmLoading(false);
    }
  }

  async function handleCancelAndRebook(newDate: string) {
    setConfirmLoading(true);
    try {
      // Cancel previous
      await cancelAppointment(workOrderId);
      message.info('Appuntamento precedente cancellato');
      
      // Book new
      await bookAppointment({
        work_order_id: workOrderId,
        appointment_date: newDate
      });
      
      message.success(`✅ Appuntamento spostato per ${newDate}`);
      
      onConfirm?.({
        appointment_date: newDate
      });
      
      await loadCalendarEvents();
      onCancel();
    } catch (error: any) {
      console.error('❌ Cancel and rebook failed:', error);
      const msg = error?.message as string | undefined;

      if (msg?.includes('Google Calendar non è ancora collegato')) {
        Modal.confirm({
          title: 'Collega Google Calendar',
          content:
            'Per modificare l’appuntamento devi prima collegare Google Calendar. Vuoi procedere al login con Google?',
          okText: 'Accedi con Google',
          cancelText: 'Annulla',
          onOk: () => redirectToGoogleOAuth(),
        });
      } else {
        message.error(msg || 'Errore durante la modifica appuntamento.');
      }
    } finally {
      setConfirmLoading(false);
    }
  }

  function handlePrevMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  }

  function handleNextMonth() {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  }

  function handleEventClick(info: any) {
    // Se clicca sull'evento dell'appuntamento attuale
    if (info.event.id === 'current-appointment') {
      Modal.confirm({
        title: 'Cancella Appuntamento',
        content: `Cancellare l'appuntamento?`,
        okText: 'Cancella',
        cancelText: 'Annulla',
        okButtonProps: { danger: true },
        onOk: () => handleDeleteAppointment()
      });
    }
  }

  async function handleDeleteAppointment() {
    setConfirmLoading(true);
    try {
      await cancelAppointment(workOrderId);
      message.success('✅ Appuntamento cancellato');
      
      // Notifica al padre che l'appuntamento è stato cancellato
      onConfirm?.({
        appointment_date: null as any
      });
      
      await loadCalendarEvents();
    } catch (error: any) {
      console.error('❌ Delete failed:', error);
      const msg = error?.message as string | undefined;

      if (msg?.includes('Google Calendar non è ancora collegato')) {
        Modal.confirm({
          title: 'Collega Google Calendar',
          content:
            'Per cancellare l’appuntamento devi prima collegare Google Calendar. Vuoi procedere al login con Google?',
          okText: 'Accedi con Google',
          cancelText: 'Annulla',
          onOk: () => redirectToGoogleOAuth(),
        });
      } else {
        message.error(msg || 'Errore durante la cancellazione appuntamento.');
      }
    } finally {
      setConfirmLoading(false);
    }
  }

  // ==================== RENDER ====================

  return (
    <>
      <div className="calendar-modal-overlay" onClick={onCancel}>
        <div className="calendar-modal" onClick={e => e.stopPropagation()}>
          {/* Header */}
          <div className="calendar-header">
            <h2>Seleziona Data Appuntamento</h2>
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
                  onClick={redirectToGoogleOAuth}
                >
                  🔗 Accedi con Google
                </button>
              </div>
            ) : (
              <>
                <div className="calendar-controls">
                  <button onClick={handlePrevMonth} disabled={loading}>← Mese Prev</button>
                  <span className="month-range">
                    {format(currentDate, 'MMMM yyyy', { locale: it }).toUpperCase()}
                  </span>
                  <button onClick={handleNextMonth} disabled={loading}>Mese Next →</button>
                </div>

                <FullCalendar
                  key={currentDate.toISOString()}
                  plugins={[daygridPlugin, interactionPlugin]}
                  initialView="dayGridMonth"
                  headerToolbar={{}}
                  locale={itLocale}
                  allDaySlot={false}
                  weekends={true}
                  events={events}
                  dateClick={handleDateClick}
                  eventClick={handleEventClick}
                  initialDate={currentDate}
                />

                <div className="calendar-legend">
                  <div className="legend-item">
                    <div className="legend-color" style={{background: '#E3F2FD', border: '2px solid #1976D2'}}></div>
                    <span>Appuntamento Cliente Attuale (Cliccabile)</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color" style={{background: '#F5F5F5', border: '2px solid #BDBDBD'}}></div>
                    <span>Appuntamenti Altri Clienti (Non Cliccabili)</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
