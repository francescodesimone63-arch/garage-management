🧠 MEMORIA CRITICA DEL PROGETTO - GARAGE MANAGEMENT SYSTEM
===========================================================

Data Creazione: 20 febbraio 2026
Ultima Revisione: 20 febbraio 2026

📁 STRUTTURA DEL PROGETTO
========================

Workspace: /Users/francescodesimone/Sviluppo Python/garage-management

```
garage-management/
│
├── 📂 doc/                           ← TUTTA LA DOCUMENTAZIONE
│   ├── SCHEMA_ER_GARAGE_DB.md       ← Schema DB (26 tabelle)
│   ├── MODIFICHE_EFFETTUATE.md      ← Log delle modifiche fatte
│   ├── REGOLE_CRITICHE_AI.md        ← REGOLE INVIOLABILI per AI
│   │
│   └── 📂 database/                  ← Specifico per DB
│       ├── SCHEMA_ER.html           ← ⭐ DIAGRAMMA INTERATTIVO
│       ├── SCHEMA_ER.mmd            ← Mermaid puro (editabile)
│       ├── database_schema.json     ← Schema completo JSON
│       └── COME_USARE_SCHEMA_ER.md ← Guida uso diagramma
│
├── 📂 backend/                       ← FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py                 ← ⭐ MODIFICATO: CORSPreflightMiddleware
│   │   ├── models/                 ← 17 file modelli DB
│   │   ├── api/                    ← Endpoints API
│   │   └── middleware/
│   │       └── cors_preflight.py   ← ⭐ CREATO: Gestisce OPTIONS
│   │
│   ├── garage.db                   ← ⭐⭐⭐ DATABASE PRINCIPALE (UNICO!)
│   ├── create_admin_user.py        ← Crea user admin
│   ├── seed_test_data.py           ← Carica dati di test
│   ├── init_database.py            ← Inizializza schema DB
│   └── venv/                        ← Python virtualenv
│
├── 📂 frontend/                      ← React 18 + Vite + TypeScript
│   ├── src/
│   │   ├── utils/
│   │   │   └── errorTracker.ts     ← ⭐ Sistema debug globale
│   │   ├── components/
│   │   │   └── DebugDashboard.tsx  ← ⭐ Visualizza errori (Ctrl+Shift+D)
│   │   └── hooks/
│   │       └── useErrorTracking.ts ← Hook per tracking
│   ├── package.json
│   └── node_modules/
│
├── START.sh                          ← Script avvio backend + frontend
├── STOP.sh                           ← Script fermata backend + frontend
│
└── ... (altri file di progetto)
```

---

🔴 REGOLE CRITICHE - MEMORIA INVIOLABILE
========================================

### 1. DATABASE
✓ **Il database è SEMPRE:** `/backend/garage.db`
✗ **NON usare:** db.sqlite3, altri file .db, backup
✓ **UNICO database di lavoro**

### 2. MODIFICHE AL DATABASE - AUTORIZZAZIONE OBBLIGATORIA
PRIMA di fare QUALSIASI operazione con i dati, devo CHIEDERE:

❌ **VIETATO senza permesso:**
- Cancellazione record (DELETE)
- Modifica dati (UPDATE)
- Reset/reinizializzazione (DELETE all)
- Creazione nuovo database
- Rimozione file garage.db

✓ **CONSENTITO senza chiedere:**
- SELECT / Letture
- Verifiche integrità
- Backup (copia, NON elimino originale)
- Esame log e errori

### 3. QUANDO CHIEDO AUTORIZZAZIONE
Frasi tipo:
- "Posso cancellare il database e ricrearlo?"
- "Devo eliminare i dati correnti per risolvere questo?"
- "Autorizzami a..." (per operazioni distruttive)

### 4. FLUSSO DECISIONALE CRITICO
1. Vedo errore database → CHIEDO PRIMA
2. Script seed fallisce → CHIEDO PRIMA
3. Schema incompatibile → CHIEDO PRIMA
4. Devo modificare dati → CHIEDO PRIMA
5. Devo cancellare/reset → CHIEDO PRIMA

---

🗄️ DATABASE SCHEMA (26 TABELLE)
===============================

### CORE ENTITIES
- **users**: Autenticazione (admin@garage.local / admin123)
- **customers**: 5 clienti di test caricati
- **vehicles**: 10 veicoli di test caricati
- **work_orders**: 15 ordini di lavoro di test caricati

### DATI ATTUALI
| Tabella | Count |
|---------|-------|
| users | 1 (admin) |
| customers | 5 |
| vehicles | 10 |
| work_orders | 15 |
| ... (altri) | ... |

### ENTITÀ PRINCIPALE
**WORK_ORDERS** è il centro di tutto - collega:
- customers (chi chiede)
- vehicles (su cosa lavoriamo)
- interventions (cosa facciamo)
- parts (cosa usiamo)
- documents (prevenivi, fatture)
- calendar_events (pianificazione)

---

🔧 MODIFICHE EFFETTUATE
=======================

### 1. FILE: `/backend/app/main.py`
- AGGIUNTO: `from app.middleware.cors_preflight import CORSPreflightMiddleware`
- AGGIUNTO: `app.add_middleware(CORSPreflightMiddleware)`
- MOTIVO: Risolvere errore CORS 405 Method Not Allowed

### 2. FILE: `/backend/app/middleware/cors_preflight.py`
- CREATO: Middleware che intercetta OPTIONS requests
- FUNZIONE: Ritorna 200 OK con header CORS prima del routing
- MOTIVO: Abilitare browser a fare preflight requests

### 3. FILE: `/backend/seed_test_data.py`
- MODIFICATO: Rimosso campo 'note' da WorkOrder (non esiste)
- MOTIVO: Campo non presente nel modello

### 4. DATABASE: `/backend/garage.db`
- CANCELLATO: database vecchio (con autorizzazione dell'utente)
- RICREATO: schema completo da SQLAlchemy models (27 tabelle)
- CARICATI: Dati di test (5 clienti, 10 veicoli, 15 ordini)
- CREATO: User admin (admin@garage.local / admin123)

### 5. FRONTEND: Sistema di Debug
- errorTracker.ts: Singleton globale per catturare errori
- DebugDashboard.tsx: UI per visualizzare errori (Ctrl+Shift+D)
- useErrorTracking: Hook per componenti React

---

🚀 STATO ATTUALE (20 febbraio 2026)
===================================

✅ Backend: Uvicorn su porta 8000
✅ Frontend: Vite su porta 3000
✅ Database: garage.db con schema completo
✅ Dati: 5 clienti, 10 veicoli, 15 ordini di lavoro
✅ Autenticazione: Admin user funzionante
✅ CORS: Preflight 200 OK (risolto!)
✅ Debug: Sistema operativo (Ctrl+Shift+D)
✅ Documentazione: Completa e organizzata

### ⭐ PAGINA ADMIN CENTRALE
**File:** `/frontend/src/pages/settings/SettingsPage.tsx`
**IMPORTANTE:** Questa pagina contiene TUTTE le funzioni di gestione dell'applicazione:
- Gestione Utenti (Create/Edit/Delete)
- Sistema Tabelle Lookup (Damage Types, Customer Types, Work Order Status, Priority Types, Intervention Status Types)
- ✅ NUOVO: Rami Sinistro (Insurance Branch Types)
- Aggiungi SEMPRE qui nuove funzioni admin

---

📊 DOCUMENTAZIONE DISPONIBILE
=============================

| File | Percorso | Contenuto |
|------|----------|----------|
| Schema DB completo | doc/SCHEMA_ER_GARAGE_DB.md | 26 tabelle, relazioni, entità |
| Log modifiche | doc/MODIFICHE_EFFETTUATE.md | Tutte le cambiate fatte |
| Regole critiche | doc/REGOLE_CRITICHE_AI.md | Regole inviolabili |
| Diagramma ER | doc/database/SCHEMA_ER.html | ⭐ Grafico interattivo (APRI) |
| Mermaid puro | doc/database/SCHEMA_ER.mmd | Editabile, per mermaid.live |
| Schema JSON | doc/database/database_schema.json | Per software/tools |
| Guida diagramma | doc/database/COME_USARE_SCHEMA_ER.md | Come usare il file ER |

---

🎯 PROSSIMI PASSI (ROADMAP)
===========================

### Priority 1 ⭐⭐⭐

#### FASE 1 — RBAC Database (✅ COMPLETATO)
- [x] Aggiungere ruoli `GMA` e `FEM` all'enum `UserRole`
- [x] Creare modello `Permission` (permessi catalogo)
- [x] Creare modello `RolePermission` (matrice dinamica ruoli-permessi)
- [x] Creare modello `Workshop` (officine multi-garage)
- [x] Aggiungere `workshop_id` (FK) al modello `User`
- [x] Database inizializzato con schema completo (29 tabelle)
- [x] Seed permessi iniziali (44 permessi raggruppati per categoria)
- [x] Ruolo-permessi mappati (352 mappamenti creati)

#### FASE 2 — API Permessi
- [ ] Endpoint `GET /api/v1/permissions` (lista permessi)
- [ ] Endpoint `GET /api/v1/permissions/matrix` (matrice ruoli-permessi)
- [ ] Endpoint `PUT /api/v1/permissions/matrix` (aggiorna matrice)
- [ ] Aggiornare `GET /api/v1/auth/me` con `permissions[]`
- [ ] Creare dependency `require_permission(codice)`
- [ ] Applicare protezioni a tutti gli endpoint

#### FASE 4 — Frontend Protezione
- [ ] Aggiornare tipo `User` con `permissions[]` e `workshop_id`
- [ ] Creare hook `usePermission()`
- [ ] Creare componente `<Can permission="">`
- [ ] Creare `RoleBasedRoute`
- [ ] Applicare protezioni a App.tsx routes

#### FASE 5 — Admin Gestione Permessi (UI)
- [ ] Pagina con griglia interattiva ruoli × permessi
- [ ] Checkbox per ogni permesso-ruolo
- [ ] Salvataggio matrici

### Priority 2 ⭐⭐
- [ ] FASE 3 — Workshop multi-officina CRUD
- [ ] FASE 6 — Admin gestione officine (UI)
- [ ] FASE 7 — Sicurezza predisposta (refresh token, token blacklist, rate limiting)

### PRIMA: Priority UI ⭐⭐⭐
- [ ] UI CRUD Customers
- [ ] UI CRUD Vehicles
- [ ] UI CRUD Work Orders

---

🔐 SISTEMA RBAC DINAMICO
========================

**Architettura**: Role-Based Access Control con permessi configurabili da ADMIN

**Ruoli (8 totali)**:
- `ADMIN` - Gestione sistema
- `GM` - General Manager  
- `GMA` - GM Assistant
- `FEM` - Front End Manager
- `CMM` - Capo Meccanica
- `CBM` - Capo Carrozzeria
- `WORKSHOP` - Operatore Meccanica
- `BODYSHOP` - Operatore Carrozzeria

**Tabelle Database**:
- `permissions` - Catalogo azioni/funzionalità (54+ permessi)
- `role_permissions` - Matrice dinamica ruolo-permesso (configurabile)
- `workshops` - Officine del garage (multi-officina)
- `users.workshop_id` - FK verso workshop

**Categorie Permessi**: Sistema, Clienti, Veicoli, Schede Lavoro, Interventi, Magazzino, Pneumatici, Auto Cortesia, Calendario, Manutenzioni, Dashboard, Documenti/Report

**Flusso Login**: Response include `permissions[]` array con permessi concessi

---

🔐 CREDENZIALI DI TEST
======================

### Admin User
- Email: `admin@garage.local`
- Password: `admin123`
- Role: ADMIN

### Database
- Type: SQLite (aiosqlite async)
- File: `/backend/garage.db`
- Tables: 26
- Test Data: Loaded

---

📞 CONTATTI IMPORTANTI
======================

Quando cercare questa memoria:
1. Prima di fare operazioni sul database
2. Prima di modificare file di configurazione
3. Prima di cambiare middleware/CORS
4. Per capire come funziona il sistema
5. Per verificare la struttura DB
6. Per ricordare le modifiche effettuate

---

⚠️ PROMEMORIA FINALE
====================

Io (GitHub Copilot) DEVO ricordare:

1. ✅ Database è `/backend/garage.db` - SOLO QUESTO
2. ✅ CHIEDO SEMPRE prima di modificare dati
3. ✅ Questa documentazione NON dimentico
4. ✅ Regole critiche sono inviolabili
5. ✅ Autorizzazione dell'utente è sacra

Questo file è il mio "cervello" del progetto.
Se dimentico qualcosa, cerco QUI.

---

Memorizzato il: 20 febbraio 2026
Versione: 1.0 - Memoria Critica
Autorità: Francesco De Simone (Utente)
