# 🎯 Integrazione Google Calendar - Riepilogo Implementazione

## ✅ Cosa è Stato Implementato

### 1. **Modelli Database** 
- ✨ **GoogleOAuthToken** - Tabella per memorizzare token di autorizzazione
- ✏️ **WorkOrder** - Aggiunto campo `google_event_id` (indicizzato)

### 2. **Flusso OAuth2 Completo**
- Autorizzazione utente (web server authorization code flow)
- Validazione stato con HMAC e scadenza (10 minuti)
- Salvataggio automatico refresh_token nel database
- Auto-refresh access_token scaduto

### 3. **API Google Calendar**
- **Creare evento**: POST /api/v1/lavori/{id}/calendar
- **Modificare evento**: PATCH /api/v1/lavori/{id}/calendar
- **Cancellave evento**: DELETE /api/v1/lavori/{id}/calendar

### 4. **Endpoints OAuth**
- **GET /api/v1/google/oauth/start** - Inizia flusso autorizzazione
- **GET /api/v1/google/oauth/callback** - Gestisce redirect di Google (automatico)

---

## 📁 File Creati/Modificati

```
backend/
├── app/
│   ├── models/
│   │   ├── work_order.py ..................... ✏️ +google_event_id
│   │   └── google_oauth.py .................. ✨ NUOVO
│   ├── google_calendar.py ................... ✨ NUOVO (OAuth + Calendar service)
│   ├── api/v1/endpoints/
│   │   ├── google_oauth.py .................. ✨ NUOVO (OAuth endpoints)
│   │   ├── lavori_calendar.py ............... ✨ NUOVO (Calendar endpoints)
│   │   └── api.py ........................... ✏️ Router importati
│   ├── models/__init__.py ................... ✏️ Esportazione GoogleOAuthToken
│   ├── core/config.py ....................... ✏️ GOOGLE_OAUTH_STATE_SECRET
│   └── core/deps.py ......................... ✓ Già presente
├── .env .................................... ✏️ Variabili Google
├── alembic/versions/
│   └── add_google_calendar_support.py ....... ✨ NUOVO (Migrazione DB)
├── garage.db ............................... 🔄 Aggiornato
├── test_google_calendar.sh ................. ✨ NUOVO (Esempi curl)
├── setup_google_calendar_db.py ............. ✨ NUOVO (Setup schema)
├── GOOGLE_CALENDAR_SETUP.md ................ ✨ NUOVO (Guida completa)
└── GOOGLE_CALENDAR_INTEGRATION.md .......... ✨ NUOVO (Riepilogo tecnico)
```

---

## 🚀 Come Usarlo

### Passo 1: Configurare Google Cloud
1. Vai a https://console.cloud.google.com
2. Crea progetto "Garage Calendar"
3. Abilita "Google Calendar API"
4. Crea credenziali OAuth2 (Web application)
5. Aggiungi Redirect URI: `http://localhost:8000/api/v1/google/oauth/callback`
6. Scarica le credenziali

### Passo 2: File `.env`
```dotenv
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google/oauth/callback
GOOGLE_CALENDAR_ID=primary
GOOGLE_OAUTH_STATE_SECRET=dev-secret-key-change-in-production
```

### Passo 3: Setup Database
```bash
cd backend
python setup_google_calendar_db.py
```

### Passo 4: Avvia Backend
```bash
uvicorn app.main:app --reload --port 8000
```

### Passo 5: Autorizza con Google
```bash
# Vai a questo URL nel browser:
http://localhost:8000/api/v1/google/oauth/start

# Clicca "Authorizza" → Reindirizzato a callback
# ✅ Tokens salvati in database
```

---

## 📝 Esempi API

### Creare Evento Calendario

```bash
curl -X POST http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Riparazione motore",
    "description": "Analisi completa motore",
    "location": "Officina Via Roma 123"
  }'
```

**Requisiti:**
- work_order.data_appuntamento ≠ null (inizio evento)
- work_order.data_fine_prevista ≠ null (fine evento)
- data_fine_prevista > data_appuntamento

**Risposta (200):**
```json
{
  "google_event_id": "abc123def456_0",
  "html_link": "https://calendar.google.com/calendar/...",
  "summary": "Riparazione motore",
  "start": {
    "dateTime": "2026-02-15T10:00:00+01:00",
    "timeZone": "Europe/Rome"
  },
  "end": {
    "dateTime": "2026-02-15T13:00:00+01:00",
    "timeZone": "Europe/Rome"
  }
}
```

### Modificare Evento

```bash
curl -X PATCH http://localhost:8000/api/v1/lavori/1/calendar?send_updates=none \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Riparazione motore - URGENTE",
    "data_appuntamento": "2026-02-16T14:00:00+01:00",
    "data_fine_prevista": "2026-02-16T17:00:00+01:00"
  }'
```

**Semantica patch:** Solo i campi forniti vengono aggiornati

**Query params:**
- `send_updates`: "none" (default), "all", "externalOnly"

### Cancellare Evento

```bash
curl -X DELETE http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔐 Sicurezza

✅ **CSRF Protection** - State parameter con HMAC-SHA256 + scadenza  
✅ **Token Security** - Refresh token crittografato in DB  
✅ **Auto-refresh** - Access token rinnovato automaticamente  
✅ **JWT Auth** - Solo utenti autenticati ADMIN possono accedere  
✅ **No logging** - Token mai registrati nei log  

---

## 🛠️ Stack Tecnologie

| Componente | Libreria | Versione |
|-----------|----------|----------|
| OAuth2 | google-auth-oauthlib | 1.2.0 |
| Calendar API | google-api-python-client | 2.115.0 |
| Auth | google-auth | 2.26.2 |
| Crypto | cryptography | ✓ (incluso in python-jose) |
| Database | SQLAlchemy + SQLite | 2.0.23 |

---

## 🧪 Test Rapido

```bash
# 1. Autorizzare con Google
curl http://localhost:8000/api/v1/google/oauth/start
# → Apri URL nel browser, autorizza

# 2. Ottenere JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin&password=admin"
# → Copia il token

# 3. Creare evento
JWT_TOKEN="your-token-here"
curl -X POST http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"summary": "Test"}'

# 4. Verificare su Google Calendar
# https://calendar.google.com/ → L'evento dovrebbe apparire!
```

---

## 📊 Schema Database

### Tabella: google_oauth_tokens
```
id                    INTEGER PRIMARY KEY (sempre 1)
refresh_token        TEXT NOT NULL          ← Long-lived token
access_token         TEXT                    ← Short-lived, cache
access_token_expiry  DATETIME               ← Scadenza access_token
calendar_id          TEXT DEFAULT 'primary' ← ID calendario
created_at           DATETIME               ← Timestamp creazione
updated_at           DATETIME               ← Timestamp aggiornamento
```

### Campo aggiunto: work_orders.google_event_id
```
google_event_id TEXT INDEXED ← ID evento Google (nullable)
```

---

## 🔧 Variabili d'Ambiente

```dotenv
# ID e secret da Google Cloud Console
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret-here

# API Callback endpoint
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google/oauth/callback

# Calendario (di solito "primary" = calendario predefinito)
GOOGLE_CALENDAR_ID=primary

# Secret per firmare il state parameter OAuth (256+ bit recommended)
GOOGLE_OAUTH_STATE_SECRET=change-this-to-random-long-string
```

---

## 🌐 Flusso OAuth Visualizzato

```
┌────────────┐                                    ┌─────────────────────┐
│  Browser   │                                    │  Google OAuth       │
└─────┬──────┘                                    └─────────────────────┘
      │                                                    △
      │ 1. Clicca "Autorizza"                            │
      ├──────────────────────────────────────────────────>│
      │   GET /api/v1/google/oauth/start                │
      │                                                   │
      │                    2. Crea state firmato         │
      │                       e redirect URL            │
      │<────────────────────────────────────────────────┤
      │ Reindirizza a:                                  │
      │ https://accounts.google.com/o/oauth2/auth?...  │
      │                                                  │
      ├──────────────────────────────────────────────────>│
      │ (Utente autorizza su Google)                    │
      │                                                  │
      │  3. Authorization code                          │
      │<────────────────────────────────────────────────┤
      │   Reindirizza a callback con:                   │
      │   ?code=4/0AX4XfW...&state=xxx                  │
      │                                                  │
├─────┴──────────────────────────┬──────────────────────┤
│ Backend                         │
│                                 │
│ 4. Valida state (firma + exp)  │
│ 5. Scambia code → tokens       │
│ 6. Salva refresh_token in DB   │
│                                 │
│ ✅ Pronto per usare Calendar   │
└─────────────────────────────────┘
```

---

## 🔄 Flusso Creazione Evento

```
Frontend         API Backend          Database       Google Calendar
   │                 │                    │                │
   │ POST /calendar  │                    │                │
   ├────────────────>│                    │                │
   │                 │ 1. Valida date    │                │
   │                 ├─────────────────>│                 │
   │                 │<─────────────────┤                 │
   │                 │ 2. Leggi tokens   │                │
   │                 ├─────────────────>│                 │
   │                 │<─────────────────┤                 │
   │                 │ 3. Crea event     │                │
   │                 ├──────────────────────────────────>│
   │                 │<──────────────────────────────────┤
   │ 4. Salva ID     │ 5. Return event   │                │
   │                 ├─────────────────>│                 │
   │<────────────────┤<─────────────────┤                 │
   │ { google_event_ │                    │                │
   │   id, html_... } │                   │                │
   │                 │                    │                │
   ✓ Evento visibile su Google Calendar   │                │
```

---

## ⚠️ Error Handling

| Errore | Status | Causa | Soluzione |
|--------|--------|-------|-----------|
| No OAuth token | 500 | OAuth non completato | Autorizza via `/oauth/start` |
| Invalid state | 400 | State scaduto/tampered | Rifai OAuth |
| Missing dates | 400 | date_appuntamento/fine nulle | Imposta date nella scheda |
| Date logic error | 400 | fine_prevista ≤ appuntamento | fine deve essere dopo inizio |
| Event not found | 409 | Nessun event associato | Crea evento prima di modificare |
| Google API 403 | 502 | Calendar API disabilitata | Abilita in Cloud Console |

---

## 📚 Documentazione

- **Setup completo**: Vedi `GOOGLE_CALENDAR_SETUP.md`  
- **Tecnichì dettagliati**: Vedi `GOOGLE_CALENDAR_INTEGRATION.md`  
- **Test curl examples**: Vedi `test_google_calendar.sh`  

---

## ✨ Funzionalità Bonus Implementate

✅ Validazione rigorosa date/orari  
✅ Patch semantics (solo campi forniti)  
✅ Timezone awareness (Europe/Rome)  
✅ HMAC state validation con expiry  
✅ Auto token refresh  
✅ Database migration Alembic  
✅ Comprehensive error handling  
✅ Admin-only access (JWT)  
✅ ISO 8601 datetime support  
✅ 3 examples curl per test  

---

## 🎓 Prossimi Passi Possibili

- [ ] Sincronizzare eventi Google → Database
- [ ] Aggiungere partecipanti (email cliente/meccanico)
- [ ] Notifiche SMS/Email tramite Google Calendar
- [ ] Calendari multipli (per location)
- [ ] Rilevamento timezone automatico
- [ ] Condivisione calendario con clienti
- [ ] Recurring maintenance events
- [ ] Webhook per aggiornamenti real-time

---

## 🚀 Status

**✅ IMPLEMENTAZIONE COMPLETA - PRONTO PER IL TEST**

Tutti i componenti sono stati:
- ✅ Creati
- ✅ Configurati  
- ✅ Testati per import errors
- ✅ Documentati
- ✅ Pronti per l'uso

**Pronto ad avviar il backend e testare!**
