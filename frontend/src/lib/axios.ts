import axios from 'axios'
import { message } from 'antd'
import { API_URL, TOKEN_KEY } from '@/config/api'
import { errorTracker } from '@/utils/errorTracker'

// Crea istanza axios
const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor - aggiungi token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (config.url?.includes('login')) {
      console.log('🔐 Login request to:', config.baseURL + config.url)
      console.log('📤 Request data:', config.data)
      console.log('📋 Request headers:', config.headers)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - gestione errori
axiosInstance.interceptors.response.use(
  (response) => {
    if (response.config.url?.includes('login')) {
      console.log('✅ Login response:', response.data)
      console.log('📌 Response status:', response.status)
      console.log('📌 Response headers:', response.headers)
    }
    return response
  },
  (error) => {
    if (error.config?.url?.includes('login')) {
      console.error('❌ Login error details:', {
        message: error.message,
        code: error.code,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers,
      })
    }
    
    const url = error.config?.url || 'unknown'
    const method = error.config?.method?.toUpperCase() || 'unknown'
    const status = error.response?.status
    
    // Traccia l'errore nel sistema di debug
    errorTracker.trackAPIError(url, method, status, error, {
      data: error.response?.data,
      endpoint: url,
      method: method,
    })
    
    console.error('❌ API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    })

    // Errore di rete - ma NON mostrare messaggio per alcuni endpoint non-critici
    if (!error.response) {
      // Url non-critiche che non devono mostrare errore di connessione
      const nonCriticalUrls = [
        'available-transitions',  // Caricamento transizioni
        'audit-trail',  // Caricamento audit trail
      ]
      
      const isNonCritical = nonCriticalUrls.some(url => error.config?.url?.includes(url))
      
      if (!isNonCritical) {
        message.error('Errore di connessione al server')
      }
      return Promise.reject(error)
    }

    const { status: statusCode, data } = error.response

    switch (statusCode) {
      case 400:
        message.error(data.detail || 'Richiesta non valida')
        break
      case 401:
        message.error('Sessione scaduta. Effettua nuovamente il login.')
        localStorage.removeItem(TOKEN_KEY)
        window.location.href = '/login'
        break
      case 403:
        message.error('Non hai i permessi per eseguire questa operazione')
        break
      case 404:
        message.error('Risorsa non trovata')
        break
      case 422:
        // Validation errors
        if (data.detail && Array.isArray(data.detail)) {
          const errors = data.detail.map((err: any) => err.msg).join(', ')
          message.error(errors)
        } else {
          message.error(data.detail || 'Errore di validazione')
        }
        break
      case 500:
        message.error('Errore interno del server')
        break
      default:
        message.error(data.detail || 'Si è verificato un errore')
    }

    return Promise.reject(error)
  }
)

export default axiosInstance
