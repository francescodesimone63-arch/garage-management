import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

// Funzione helper per ottenere il token dal localStorage
function getAuthToken(): string {
  const token = localStorage.getItem('garage_access_token');
  if (!token) {
    throw new Error('Token di autenticazione non trovato. Effettua il login.');
  }
  return token;
}

// Crea axios instance con headers di autenticazione
function getAuthHeaders() {
  return {
    'Authorization': `Bearer ${getAuthToken()}`
  };
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;      // RFC3339 datetime
  end: string;
  is_busy: boolean;
}

export interface BookAppointmentPayload {
  work_order_id: number;
  appointment_date: string;    // YYYY-MM-DD
}

export interface AppointmentInfo {
  appointment_date: string;  // YYYY-MM-DD
  work_order_id: number;
  customer_name: string;
  customer_id: number;
}

export interface OAuthStatusResponse {
  configured: boolean;
  calendar_id?: string;
  configured_at?: string;
  message?: string;
  auth_url?: string;
}

/**
 * Verifica se Google Calendar OAuth è configurato
 */
export async function checkOAuthStatus(): Promise<OAuthStatusResponse> {
  try {
    const response = await axios.get(`${API_BASE}/google/oauth/status`, {
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error: any) {
    console.error('OAuth status check failed:', error);
    if (error.response?.status === 401) {
      throw new Error('Sessione scaduta. Effettua il login.');
    }
    // Se il check fallisce, assumiamo non configurato
    return {
      configured: false,
      message: 'Impossibile verificare lo stato OAuth.'
    };
  }
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
    const response = await axios.get(`${API_BASE}/calendar/events`, {
      params: { timeMin, timeMax },
      headers: getAuthHeaders()
    });
    return response.data.events;
  } catch (error: any) {
    console.error('Calendar fetch failed:', error);
    if (error.response?.status === 401) {
      throw new Error('Sessione scaduta. Effettua il login.');
    }
    if (error.response?.status === 502) {
      throw new Error('Google Calendar non configurato. Effettua il login OAuth.');
    }
    throw error;
  }
}

/**
 * Carica TUTTI gli appuntamenti del mese (di tutti i clienti)
 */
export async function fetchAllAppointmentsForMonth(
  month: number,
  year: number
): Promise<AppointmentInfo[]> {
  try {
    const response = await axios.get(`${API_BASE}/calendar/appointments/month`, {
      params: { month, year },
      headers: getAuthHeaders()
    });
    return response.data.appointments;
  } catch (error: any) {
    console.error('Fetch all appointments failed:', error);
    if (error.response?.status === 401) {
      throw new Error('Sessione scaduta. Effettua il login.');
    }
    throw error;
  }
}

/**
 * Prenota appuntamento (solo data, tutto il giorno)
 */
export async function bookAppointment(
  payload: BookAppointmentPayload
): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE}/calendar/book`, null, {
      params: {
        work_order_id: payload.work_order_id,
        appointment_date: payload.appointment_date
      },
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error: any) {
    console.error('Book appointment failed:', error);
    if (error.response?.status === 401) {
      throw new Error('Sessione scaduta. Effettua il login.');
    }
    if (error.response?.status === 502) {
      const detail = error.response?.data?.detail as string | undefined;
      if (detail?.includes('No Google OAuth token found')) {
        throw new Error('Google Calendar non è ancora collegato. Clicca su "Accedi con Google" nella finestra del calendario e completa il login, poi riprova.');
      }
      throw new Error(detail || 'Errore Google Calendar durante la prenotazione.');
    }
    if (error.response?.status === 409) {
      throw new Error(error.response?.data?.detail || 'Errore prenotazione appuntamento.');
    }
    throw error;
  }
}

/**
 * Cancella appuntamento (da Google + DB)
 */
export async function cancelAppointment(
  workOrderId: number
): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE}/calendar/cancel`, null, {
      params: {
        work_order_id: workOrderId
      },
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error: any) {
    console.error('Cancel appointment failed:', error);
    if (error.response?.status === 401) {
      throw new Error('Sessione scaduta. Effettua il login.');
    }
    throw error;
  }
}
