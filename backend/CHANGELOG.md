# Changelog - Garage Management System Backend

## [0.2.0] - 09/02/2026

### 🎉 Fase 1 Completata - Core API Endpoints

### Aggiunto
- **Endpoint Autenticazione** (`api/v1/endpoints/auth.py`)
  - Login con JWT
  - Registrazione utenti
  - Refresh token
  - Logout
  - Password reset (placeholder)
  - Get current user

- **Endpoint Users** (`api/v1/endpoints/users.py`)
  - CRUD completo utenti
  - Gestione profilo utente corrente
  - Role-based access control

- **Endpoint Customers** (`api/v1/endpoints/customers.py`)
  - CRUD clienti
  - Ricerca clienti (nome, email, telefono)
  - Statistiche cliente (veicoli, ordini, spesa totale)
  - Dettagli cliente con veicoli associati

- **Endpoint Vehicles** (`api/v1/endpoints/vehicles.py`)
  - CRUD veicoli
  - Filtri per cliente e ricerca
  - Storico manutenzione veicolo
  - Stato manutenzione con calcoli automatici

- **Endpoint Work Orders** (`api/v1/endpoints/work_orders.py`)
  - CRUD ordini di lavoro
  - Filtri avanzati (stato, reparto, date, veicolo)
  - Cambio stato con workflow
  - Statistiche mensili/annuali
  - Vista calendario

- **Database Migrations**
  - Configurazione completa Alembic
  - Environment setup
  - Template migrations

- **Script Utility**
  - `scripts/seed_database.py` - Popola DB con dati di test
  - `scripts/create_admin.py` - Crea utente amministratore
  - `setup.sh` - Setup automatico completo

- **Documentazione**
  - README.md completo del backend
  - IMPLEMENTATION_STATUS.md aggiornato
  - CHANGELOG.md

### Caratteristiche
- ✅ Autenticazione JWT completa
- ✅ Role-based access control (admin, gm, workshop, bodyshop)
- ✅ Validazione dati con Pydantic
- ✅ Gestione errori standardizzata
- ✅ Documentazione API automatica (Swagger/ReDoc)
- ✅ Filtri e ricerca avanzata
- ✅ Statistiche e aggregazioni
- ✅ Setup automatizzato

### API Endpoints Disponibili

#### Autenticazione
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`

#### Users (47 endpoints totali)
- `GET /api/users/`
- `POST /api/users/`
- `GET /api/users/me`
- `PUT /api/users/me`
- `GET /api/users/{id}`
- `PUT /api/users/{id}`
- `DELETE /api/users/{id}`

#### Customers
- `GET /api/customers/` (con ricerca)
- `POST /api/customers/`
- `GET /api/customers/{id}`
- `GET /api/customers/{id}/details`
- `GET /api/customers/{id}/stats`
- `PUT /api/customers/{id}`
- `DELETE /api/customers/{id}`

#### Vehicles
- `GET /api/vehicles/` (con filtri)
- `POST /api/vehicles/`
- `GET /api/vehicles/{id}`
- `GET /api/vehicles/{id}/history`
- `GET /api/vehicles/{id}/maintenance-status`
- `PUT /api/vehicles/{id}`
- `DELETE /api/vehicles/{id}`

#### Work Orders
- `GET /api/work-orders/` (con filtri)
- `POST /api/work-orders/`
- `GET /api/work-orders/{id}`
- `GET /api/work-orders/stats`
- `GET /api/work-orders/calendar`
- `PUT /api/work-orders/{id}`
- `PATCH /api/work-orders/{id}/status`
- `DELETE /api/work-orders/{id}`

### Dati di Test Inclusi
Dopo il seed, il database contiene:
- 4 utenti (admin, gm, officina, carrozzeria)
- 3 clienti con dati completi
- 4 veicoli associati ai clienti
- 3 ordini di lavoro di esempio

### Credenziali di Test
- **Admin**: admin@garage.com / admin123
- **GM**: gm@garage.com / gm123
- **Officina**: officina@garage.com / officina123
- **Carrozzeria**: carrozzeria@garage.com / carrozzeria123

## [0.1.0] - Precedente

### Aggiunto
- Struttura base progetto
- 11 modelli database (SQLAlchemy)
- 11 schemi Pydantic
- Core sistema (config, database, security)
- Sistema autenticazione JWT
- Configurazione CORS
- Middleware compression/session

---

## Prossimi Release Pianificati

### [0.3.0] - Fase 2 API (Pianificato)
- Endpoint Parts (ricambi)
- Endpoint Tires (pneumatici)
- Endpoint Courtesy Cars
- Endpoint Maintenance Schedules
- Endpoint Notifications

### [0.4.0] - Business Logic (Pianificato)
- Servizi business logic
- Calcoli automatici
- Workflow automatizzati
- Notifiche automatiche

### [0.5.0] - Integrazioni (Pianificato)
- Google Calendar API
- Email service
- SMS/WhatsApp
- Generazione PDF

### [1.0.0] - Production Ready (Obiettivo)
- Testing completo
- Docker setup
- CI/CD pipeline
- Monitoring
- Documentazione completa
