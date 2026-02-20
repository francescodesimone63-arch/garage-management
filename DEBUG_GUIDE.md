# 🔍 Guida al Debugging Efficiente - Garage Management System

## Indice
1. [Panoramica del sistema](#panoramica)
2. [Strumenti disponibili](#strumenti)
3. [Come debuggare errori API](#debug-api)
4. [Come debuggare errori di validazione](#debug-validazione)
5. [Come debuggare errori di rete](#debug-rete)
6. [Problemi comuni e soluzioni](#problemi-comuni)
7. [Best practices](#best-practices)

---

## Panoramica

Il sistema di debugging è costituito da tre componenti principali:

### Backend
- **Logger avanzato** (`app/utils/logger.py`): Traccia errori e richieste API
- **Debug Middleware** (`app/middleware/debug_middleware.py`): Logga tutte le richieste e risposte
- **Log files**: Salvati in `backend/logs/`

### Frontend
- **Error Tracker** (`src/utils/errorTracker.ts`): Traccia errori in tempo reale
- **Error Hook** (`src/hooks/useErrorTracking.ts`): Easy integration nei componenti
- **Debug Dashboard** (`src/components/DebugDashboard.tsx`): UI visiva per visualizzare errori

### Scripts
- **validate.sh**: Verifica lo stato del sistema e la configurazione

---

## Strumenti disponibili

### 1. Debug Dashboard (Frontend)

**Come aprire:**
- Premi **Ctrl+Shift+D** nel browser
- Oppure clicca il pulsante 🐛 in basso a destra

**Funzionalità:**
- Visualizza tutti gli errori in tempo reale
- Filtra per tipo (API, Validazione, Runtime, Network)
- Filtra per severità (Bassa, Media, Alta, Critica)
- Ricerca nel messaggio di errore
- Visualizza dettagli JSON di ogni errore
- Scarica i logs come JSON
- Statistiche in tempo reale

**Shortcut Log:**
```
Ctrl+Shift+D - Apri/Chiudi Debug Dashboard
```

---

### 2. Backend Logs

**Percorsi log:**
```
backend/logs/debug.log          # Log generale
backend/logs/vehicles.log       # Log veicoli
backend/logs/customers.log      # Log clienti
backend/logs/workorders.log     # Log schede lavoro
backend/logs/auth.log           # Log autenticazione
```

**Come visualizzare:**
```bash
# Ultimi 50 righe
tail -50 backend/logs/debug.log

# Segui i logs in tempo reale
tail -f backend/logs/debug.log

# Cerca un errore specifico
grep -i "ERROR" backend/logs/debug.log

# Conta errori per tipo
grep "API ERROR" backend/logs/debug.log | wc -l
```

---

### 3. Browser Console

I logs vengono stampati anche in console con colori:
```javascript
// Apri Console (F12) → Console tab
// Vedi errori colorati con tipo e severità
```

---

## Come debuggare errori API

### Caso 1: Errore 500 dal server

**Dalla Dashboard:**
1. Premi **Ctrl+Shift+D**
2. Filtra per "api" type
3. Filtra per "high" o "critical" severity
4. Clicca l'errore per vedere i dettagli JSON

**Ai log del backend:**
```bash
grep "500" backend/logs/debug.log
# Vedrai il messaggio di errore completo e lo stack trace
```

**Strategia:**
- Leggi il messaggio di errore nella Dashboard
- Vai ai log backend per lo stack trace dettagliato
- Locate il file e la riga del problema
- Fissa e riavvia il backend

---

### Caso 2: Errore 422 (Validazione)

**Dalla Dashboard:**
1. Apri Debug Dashboard (Ctrl+Shift+D)
2. Filtra per "api" type
3. Seleziona l'errore 422
4. Visualizza il JSON - conterrà il campo e il motivo dell'errore

**Esempio dashboard output:**
```json
{
  "type": "api",
  "severity": "medium",
  "message": "API Error: /api/v1/vehicles/",
  "details": {
    "endpoint": "/api/v1/vehicles/",
    "method": "POST",
    "status": 422,
    "error": "Validation error..."
  }
}
```

**Strategia:**
- Leggi l'errore di validazione
- Controlla i dati che stai inviando nel JSON
- Verifica lo schema Pydantic backend
- Fissa i dati o lo schema

---

### Caso 3: Errore 401 (Non Autenticato)

**Dalla Dashboard:**
1. Apri Debug Dashboard
2. Cerca errori 401
3. Controlla se il token è presente

**Strategia:**
- Login di nuovo
- Verifica che il token sia salvato in localStorage
- Controlla se il token è scaduto (durata: 24h)

---

## Come debuggare errori di validazione

### Nel Frontend

```typescript
// Nel componente, usa l'hook:
import { useErrorTracking } from '@/hooks/useErrorTracking'

function MyComponent() {
  const { trackValidationError } = useErrorTracking()
  
  // Quando trovi un errore di validazione:
  trackValidationError('email', 'Email non valida', {
    value: email,
    component: 'ProfileForm'
  })
}
```

**Dalla Dashboard:**
1. Filtra per "validation" type
2. Visualizza i dettagli
3. Vedi il campo, il valore e il contesto

---

### Nel Backend

I validatori Pydantic sono automaticamente loggati:

```bash
grep "VALIDATION ERROR" backend/logs/debug.log
```

---

## Come debuggare errori di rete

### Errore: "Access to XMLHttpRequest blocked by CORS policy"

**Dalla Dashboard:**
1. Premi Ctrl+Shift+D
2. Guarda gli errori di tipo "network"
3. Severity sarà "critical"

**Verificare CORS:**
```bash
# Test CORS headers
curl -i -X OPTIONS http://localhost:8000/api/v1/vehicles/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"

# Dovresti vedere nel response:
# access-control-allow-origin: http://localhost:3000
# access-control-allow-credentials: true
```

**Se CORS non funziona:**
1. Riavvia il backend: `bash STOP.sh && bash START.sh`
2. Ripulisci la cache browser: **Ctrl+Shift+R**
3. Prova di nuovo

---

### Errore: "ERR_FAILED" con status 500

**Significato:** Il request ha iniziato ma il server ha avuto un errore

**Debug:**
1. Apri Backend logs: `tail -f backend/logs/debug.log`
2. Prova di nuovo l'azione
3. Leggi il messaggio di errore nei logs

---

## Problemi comuni e soluzioni

### Problema: Vehicle creation fallisce con 422

**Symptoms:**
- Dashboard mostra errore 422 per POST /vehicles/
- Message contiene "Field required"

**Soluzione:**
1. Apri Debug Dashboard
2. Clicca sull'errore 422
3. Leggi JSON → `details.data`
4. Vedi quale campo manca
5. Frontend: Verifica che il form includa quel campo
6. Backend: Controlla se il campo è veramente obbligatorio in `schemas/vehicle.py`

---

### Problema: CORS error persiste dopo riavvio

**Symptoms:**
- Backend logs non mostrano errori
- Frontend riceve CORS error
- Curl test mostra CORS headers corretti

**Soluzione:**
1. **Questa è una cache browser!**
2. Cancella cache: **Cmd+Shift+Delete** (Chrome/Firefox)
3. Hard refresh: **Ctrl+Shift+R**
4. O apri in **modalità anonima**

---

### Problema: Backend non risponde

**Debug:**
```bash
# Verifica se processi stanno girando
ps aux | grep -E 'uvicorn|node'

# Riavvia da zero
bash STOP.sh && sleep 3 && bash START.sh

# Controlla logs
tail backend/backend.log
tail frontend/frontend.log
```

---

### Problema: Database locked

**Symptoms:**
- Error contiene "database is locked"

**Soluzione:**
```bash
# Chiudi tutti i processi
bash STOP.sh

# Rimuovi lock (se presente)
cd backend && rm -f db.sqlite3-wal db.sqlite3-shm

# Riavvia
bash START.sh
```

---

## Best Practices

### 1. Prima di segnalare un bug

Segui questa checklist:

```
[ ] Ho pulito la cache browser (Ctrl+Shift+R)
[ ] Ho riavviato il backend (bash STOP.sh && bash START.sh)
[ ] Ho aperto il Debug Dashboard (Ctrl+Shift+D)
[ ] Ho scaricato i logs JSON
[ ] Ho controllato i logs backend (tail -f backend/logs/debug.log)
[ ] Ho cercato il problema nei logs comuni
```

---

### 2. Debugging efficiente - Workflow

**Quando trovi un errore:**

1. **Frontend**: Apri Debug Dashboard (Ctrl+Shift+D)
2. **Vedi il tipo di errore**: API? Validazione? Network?
3. **Se API error**: 
   - Guarda lo status code (422, 500, 401, etc.)
   - Guarda il JSON response
4. **Se non capisce**: Vai ai logs
5. **Backend logs**: `tail -f backend/logs/debug.log`
6. **Leggi lo stack trace**
7. **Identifica il file e la riga**
8. **Fissa il problema**
9. **Riavvia backend**
10. **Pulisci cache browser**
11. **Testa di nuovo**

---

### 3. Registrare errori custom

Nel tuo componente React:

```typescript
import { useErrorTracking } from '@/hooks/useErrorTracking'

function MyComponent() {
  const { trackAPIError, trackValidationError, trackRuntimeError } = useErrorTracking()
  
  const handleSave = async () => {
    try {
      const response = await api.post('/endpoint', data)
    } catch (error) {
      // ✅ BUONO: Traccia l'errore con contesto
      trackAPIError(
        '/endpoint',
        'POST',
        error.response?.status,
        error,
        { data, component: 'MyComponent' }
      )
    }
  }
}
```

---

### 4. Script di validazione

Prima di iniziare debug profondo, esegui:

```bash
bash validate.sh
```

Questo verifica:
- ✅ Backend installato correttamente
- ✅ Frontend installato correttamente
- ✅ Services in running
- ✅ CORS configurato
- ✅ API endpoints rispondono

---

## Comandi Utili

```bash
# Pulisci cache Python
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Pulisci cache Vite frontend
rm -rf frontend/.vite frontend/dist node_modules/.vite

# Visualizza ultimi 100 errori
tail -100 backend/logs/debug.log

# Conta errori per tipo
grep -c "API ERROR" backend/logs/debug.log
grep -c "DATABASE ERROR" backend/logs/debug.log

# Export logs
curl -s http://localhost:3000 # Poi Ctrl+Shift+D → Scarica Logs

# Real-time monitoring
tail -f backend/logs/debug.log | grep "ERROR"
```

---

## Contatti Rapide per Problemi

| Problema | Dove guardare | Comando |
|----------|--------------|---------|
| API Error 500 | `tail -f backend/logs/debug.log` | Debug tutto |
| API Error 422 | Dashboard JSON | Check validazione |
| CORS Error | Browser cache | `Ctrl+Shift+R` |
| Network Error | Backend running? | `bash START.sh` |
| DB Locked | `backend/logs/debug.log` | Restart system |

---

**Ultima modifica:** 2026-02-20  
**Versione:** 1.0
