# 🏗️ SPECIFICHE TECNICHE - SISTEMA GESTIONALE GARAGE

## 📋 INDICE

1. [Architettura Generale](#architettura-generale)
2. [Stack Tecnologico](#stack-tecnologico)
3. [Struttura Database](#struttura-database)
4. [API Backend](#api-backend)
5. [Frontend](#frontend)
6. [Integrazioni Esterne](#integrazioni-esterne)
7. [Sicurezza](#sicurezza)
8. [Performance](#performance)
9. [Deploy](#deploy)

---

## 🏛️ ARCHITETTURA GENERALE

### **Pattern Architetturale**
- **Tipo:** Client-Server con architettura a 3 livelli
- **Stile:** RESTful API
- **Comunicazione:** HTTP/HTTPS + JSON

### **Diagramma Architettura**

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  React.js SPA (Single Page Application)         │  │
│  │  - Tailwind CSS (styling)                       │  │
│  │  - React Router (navigation)                    │  │
│  │  - Axios (HTTP client)                          │  │
│  │  - React Query (state management)               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTPS/JSON
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.11+)                         │  │
│  │  - Pydantic (validation)                        │  │
│  │  - JWT (authentication)                         │  │
│  │  - APScheduler (background tasks)               │  │
│  │  - CORS middleware                              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ SQL
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLite (dev) / PostgreSQL (prod)               │  │
│  │  - SQLAlchemy 2.0 ORM                           │  │
│  │  - Alembic (migrations)                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ API
┌─────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                      │
│  - Google Calendar API                                  │
│  - Google Drive API                                     │
│  - SendGrid (email)                                     │
│  - Twilio (SMS)                                         │
│  - WhatsApp Business API                                │
│  - OpenAI/Perplexity (AI search)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ STACK TECNOLOGICO

### **Backend**

#### **Framework e Librerie Core**
```python
# requirements.txt (Backend)
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

#### **Database e ORM**
```python
# Database drivers
psycopg2-binary==2.9.9  # PostgreSQL (produzione)
aiosqlite==0.19.0       # SQLite async (sviluppo)

# Migrations
alembic==1.13.1
```

#### **Autenticazione e Sicurezza**
```python
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
python-dotenv==1.0.0              # Environment variables
```

#### **Task Scheduling**
```python
apscheduler==3.10.4  # Background tasks e cron jobs
```

#### **Integrazioni Esterne**
```python
# Google APIs
google-auth==2.26.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.115.0

# Email
sendgrid==6.11.0

# SMS
twilio==8.11.1

# AI
openai==1.10.0
httpx==0.26.0  # Per Perplexity API
```

#### **Utilities**
```python
python-dateutil==2.8.2
pytz==2023.3
```

---

### **Frontend**

#### **Framework e Librerie**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "axios": "^1.6.5",
    "@tanstack/react-query": "^5.17.9",
    "react-hook-form": "^7.49.3",
    "date-fns": "^3.2.0",
    "@headlessui/react": "^1.7.18",
    "@heroicons/react": "^2.1.1"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "vite": "^5.0.11",
    "@vitejs/plugin-react": "^4.2.1"
  }
}
```

#### **Build Tool**
- **Vite** - Build tool moderno e veloce
- **PostCSS** - Processing CSS
- **Autoprefixer** - Compatibilità browser

---

## 🗄️ STRUTTURA DATABASE

### **Schema Completo (14 Tabelle)**

#### **1. users - Utenti Sistema**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ruolo VARCHAR(20) NOT NULL CHECK(ruolo IN ('GM', 'CMM', 'CBM', 'ADMIN')),
    nome VARCHAR(100),
    cognome VARCHAR(100),
    attivo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_ruolo ON users(ruolo);
```

#### **2. customers - Clienti**
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    ragione_sociale VARCHAR(200),
    codice_fiscale VARCHAR(16),
    partita_iva VARCHAR(11),
    telefono VARCHAR(20),
    email VARCHAR(100),
    indirizzo TEXT,
    citta VARCHAR(100),
    cap VARCHAR(10),
    provincia VARCHAR(2),
    preferenze_notifica TEXT, -- JSON: {"email": true, "sms": false, "whatsapp": true}
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_telefono ON customers(telefono);
```

#### **3. vehicles - Veicoli**
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    targa VARCHAR(10) UNIQUE NOT NULL,
    telaio VARCHAR(17),
    marca VARCHAR(50),
    modello VARCHAR(50),
    anno INTEGER,
    colore VARCHAR(30),
    km_attuali INTEGER,
    customer_id INTEGER,
    tipo VARCHAR(20) CHECK(tipo IN ('cliente', 'cortesia')) DEFAULT 'cliente',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE INDEX idx_vehicles_targa ON vehicles(targa);
CREATE INDEX idx_vehicles_customer ON vehicles(customer_id);
CREATE INDEX idx_vehicles_tipo ON vehicles(tipo);
```

#### **4. work_orders - Schede Lavoro**
```sql
CREATE TABLE work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_scheda VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_appuntamento TIMESTAMP,
    data_fine_prevista TIMESTAMP,
    data_completamento TIMESTAMP,
    stato VARCHAR(20) CHECK(stato IN ('bozza', 'approvata', 'in_lavorazione', 'completata', 'annullata')) DEFAULT 'bozza',
    tipo_danno VARCHAR(50),
    priorita VARCHAR(20) CHECK(priorita IN ('bassa', 'media', 'alta', 'urgente')) DEFAULT 'media',
    valutazione_danno TEXT,
    note TEXT,
    creato_da INTEGER,
    approvato_da INTEGER,
    auto_cortesia_id INTEGER,
    costo_stimato DECIMAL(10,2),
    costo_finale DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (creato_da) REFERENCES users(id),
    FOREIGN KEY (approvato_da) REFERENCES users(id),
    FOREIGN KEY (auto_cortesia_id) REFERENCES courtesy_cars(id)
);

CREATE INDEX idx_work_orders_numero ON work_orders(numero_scheda);
CREATE INDEX idx_work_orders_customer ON work_orders(customer_id);
CREATE INDEX idx_work_orders_vehicle ON work_orders(vehicle_id);
CREATE INDEX idx_work_orders_stato ON work_orders(stato);
CREATE INDEX idx_work_orders_data_app ON work_orders(data_appuntamento);
```

#### **5. work_order_activities - Attività Schede**
```sql
CREATE TABLE work_order_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    descrizione TEXT NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('meccanica', 'carrozzeria')) NOT NULL,
    assegnato_a VARCHAR(10) CHECK(assegnato_a IN ('CMM', 'CBM')),
    stato VARCHAR(20) CHECK(stato IN ('da_fare', 'in_corso', 'completata')) DEFAULT 'da_fare',
    ore_stimate DECIMAL(5,2),
    ore_effettive DECIMAL(5,2),
    costo_manodopera DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_activities_work_order ON work_order_activities(work_order_id);
CREATE INDEX idx_activities_tipo ON work_order_activities(tipo);
CREATE INDEX idx_activities_stato ON work_order_activities(stato);
```

#### **6. parts - Parti di Ricambio**
```sql
CREATE TABLE parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descrizione TEXT,
    categoria VARCHAR(100),
    marca VARCHAR(100),
    modello VARCHAR(100),
    quantita DECIMAL(10,2) DEFAULT 0,
    quantita_minima DECIMAL(10,2) DEFAULT 5,
    prezzo_acquisto DECIMAL(10,2),
    prezzo_vendita DECIMAL(10,2),
    fornitore VARCHAR(200),
    posizione_magazzino VARCHAR(100),
    tipo VARCHAR(20) CHECK(tipo IN ('ricambio', 'fornitura')) DEFAULT 'ricambio',
    unita_misura VARCHAR(10) DEFAULT 'pz',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parts_codice ON parts(codice);
CREATE INDEX idx_parts_categoria ON parts(categoria);
CREATE INDEX idx_parts_quantita ON parts(quantita);
```

#### **7. work_order_parts - Parti per Schede**
```sql
CREATE TABLE work_order_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    quantita_richiesta DECIMAL(10,2) NOT NULL,
    quantita_utilizzata DECIMAL(10,2) DEFAULT 0,
    stato VARCHAR(20) CHECK(stato IN ('da_ordinare', 'in_arrivo', 'disponibile', 'utilizzata', 'non_utilizzata')) DEFAULT 'da_ordinare',
    data_ordine TIMESTAMP,
    data_arrivo TIMESTAMP,
    data_utilizzo TIMESTAMP,
    fornitore_ordine VARCHAR(200),
    prezzo_acquisto DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

CREATE INDEX idx_wo_parts_work_order ON work_order_parts(work_order_id);
CREATE INDEX idx_wo_parts_part ON work_order_parts(part_id);
CREATE INDEX idx_wo_parts_stato ON work_order_parts(stato);
```

#### **8. stock_movements - Movimenti Magazzino**
```sql
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id INTEGER NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('carico', 'scarico', 'rettifica')) NOT NULL,
    quantita DECIMAL(10,2) NOT NULL,
    quantita_precedente DECIMAL(10,2),
    quantita_nuova DECIMAL(10,2),
    work_order_id INTEGER,
    data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    utente_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (utente_id) REFERENCES users(id)
);

CREATE INDEX idx_movements_part ON stock_movements(part_id);
CREATE INDEX idx_movements_data ON stock_movements(data_movimento);
```

#### **9. tires - Pneumatici**
```sql
CREATE TABLE tires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    tipo_stagione VARCHAR(20) CHECK(tipo_stagione IN ('estivo', 'invernale')) NOT NULL,
    marca VARCHAR(50),
    modello VARCHAR(50),
    misura VARCHAR(30),
    data_deposito TIMESTAMP,
    data_ultimo_cambio TIMESTAMP,
    data_prossimo_cambio TIMESTAMP,
    stato VARCHAR(20) CHECK(stato IN ('depositati', 'montati')) DEFAULT 'depositati',
    posizione_deposito VARCHAR(50),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_tires_vehicle ON tires(vehicle_id);
CREATE INDEX idx_tires_prossimo_cambio ON tires(data_prossimo_cambio);
```

#### **10. courtesy_cars - Auto Cortesia**
```sql
CREATE TABLE courtesy_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER UNIQUE NOT NULL,
    contratto_tipo VARCHAR(20) CHECK(contratto_tipo IN ('leasing', 'affitto', 'proprieta')) NOT NULL,
    fornitore_contratto VARCHAR(200),
    data_inizio_contratto DATE,
    data_scadenza_contratto DATE,
    canone_mensile DECIMAL(10,2),
    km_inclusi_anno INTEGER,
    stato VARCHAR(20) CHECK(stato IN ('disponibile', 'assegnata', 'manutenzione', 'fuori_servizio')) DEFAULT 'disponibile',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_courtesy_stato ON courtesy_cars(stato);
```

#### **11. car_assignments - Assegnazioni Auto**
```sql
CREATE TABLE car_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    courtesy_car_id INTEGER NOT NULL,
    work_order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    data_inizio TIMESTAMP NOT NULL,
    data_fine_prevista TIMESTAMP NOT NULL,
    data_fine_effettiva TIMESTAMP,
    km_inizio INTEGER,
    km_fine INTEGER,
    stato VARCHAR(20) CHECK(stato IN ('prenotata', 'in_corso', 'completata', 'annullata')) DEFAULT 'prenotata',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courtesy_car_id) REFERENCES courtesy_cars(id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_assignments_courtesy_car ON car_assignments(courtesy_car_id);
CREATE INDEX idx_assignments_work_order ON car_assignments(work_order_id);
CREATE INDEX idx_assignments_date ON car_assignments(data_inizio, data_fine_prevista);
```

#### **12. maintenance_schedules - Scadenziari**
```sql
CREATE TABLE maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('ordinaria', 'straordinaria')) NOT NULL,
    descrizione TEXT NOT NULL,
    km_scadenza INTEGER,
    data_scadenza DATE,
    km_preavviso INTEGER DEFAULT 1000,
    giorni_preavviso INTEGER DEFAULT 30,
    stato VARCHAR(20) CHECK(stato IN ('attivo', 'completato', 'annullato')) DEFAULT 'attivo',
    ricorrente BOOLEAN DEFAULT FALSE,
    intervallo_km INTEGER,
    intervallo_giorni INTEGER,
    ultima_notifica TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_schedules_vehicle ON maintenance_schedules(vehicle_id);
CREATE INDEX idx_schedules_scadenza ON maintenance_schedules(data_scadenza);
CREATE INDEX idx_schedules_stato ON maintenance_schedules(stato);
```

#### **13. notifications - Notifiche**
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo VARCHAR(20) CHECK(tipo IN ('email', 'sms', 'whatsapp')) NOT NULL,
    destinatario VARCHAR(200) NOT NULL,
    oggetto VARCHAR(200),
    messaggio TEXT NOT NULL,
    stato VARCHAR(20) CHECK(stato IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    data_invio TIMESTAMP,
    errore TEXT,
    riferimento_tipo VARCHAR(50),
    riferimento_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_stato ON notifications(stato);
CREATE INDEX idx_notifications_tipo ON notifications(tipo);
CREATE INDEX idx_notifications_data ON notifications(data_invio);
```

#### **14. calendar_events - Eventi Google Calendar**
```sql
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER UNIQUE NOT NULL,
    google_event_id VARCHAR(255) UNIQUE,
    titolo VARCHAR(200) NOT NULL,
    descrizione TEXT,
    data_inizio TIMESTAMP NOT NULL,
    data_fine TIMESTAMP NOT NULL,
    partecipanti TEXT, -- JSON array
    sincronizzato BOOLEAN DEFAULT FALSE,
    ultima_sincronizzazione TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_calendar_work_order ON calendar_events(work_order_id);
CREATE INDEX idx_calendar_google_id ON calendar_events(google_event_id);
```

---

## 🔌 API BACKEND

### **Struttura Endpoint**

```
/api/v1/
├── auth/
│   ├── POST   /login
│   ├── POST   /logout
│   ├── GET    /me
│   └── POST   /refresh
├── users/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── customers/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   └── DELETE /{id}
├── vehicles/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   └── GET    /customer/{customer_id}
├── work-orders/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   ├── POST   /{id}/approve
│   ├── POST   /{id}/suggest-appointment
│   ├── GET    /calendar
│   └── GET    /dashboard
├── parts/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   ├── POST   /check-availability
│   ├── POST   /reserve
│   └── POST   /search-suppliers
├── stock-movements/
│   ├── GET    /
│   ├── POST   /
│   └── GET    /part/{part_id}
├── tires/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── GET    /alerts
│   └── POST   /send-alerts
├── courtesy-cars/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── GET    /available
│   └── POST   /assign
├── maintenance-schedules/
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /{id}
│   ├── PUT    /{id}
│   ├── DELETE /{id}
│   └── GET    /alerts
├── notifications/
│   ├── POST   /send
│   └── GET    /history
├── calendar/
│   ├── POST   /sync
│   └── GET    /events
└── reports/
    ├── GET    /dashboard
    ├── GET    /work-orders
    ├── GET    /inventory
    └── GET    /export
```

### **Autenticazione JWT**

```python
# Schema Token
{
    "sub": "user_id",
    "username": "mario.rossi",
    "ruolo": "GM",
    "exp": 1234567890
}

# Headers richieste autenticate
Authorization: Bearer <token>
```

### **Response Format Standard**

```json
{
    "success": true,
    "data": { ... },
    "message": "Operazione completata",
    "timestamp": "2026-02-09T14:30:00Z"
}
```

### **Error Format**

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Dati non validi",
        "details": [...]
    },
    "timestamp": "2026-02-09T14:30:00Z"
}
```

---

## 🎨 FRONTEND

### **Struttura Componenti**

```
src/
├── components/
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Modal.jsx
│   │   ├── Table.jsx
│   │   └── Spinner.jsx
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Footer.jsx
│   │   └── Layout.jsx
│   └── features/
│       ├── WorkOrders/
│       ├── Customers/
│       ├── Vehicles/
│       ├── Parts/
│       └── Calendar/
├── pages/
│   ├── Dashboard.jsx
│   ├── Login.jsx
│   ├── WorkOrders/
│   ├── Customers/
│   ├── Vehicles/
│   ├── Parts/
│   ├── Tires/
│   ├── CourtesyCars/
│   └── Reports/
├── services/
│   ├── api.js
│   ├── auth.js
│   └── storage.js
├── hooks/
│   ├── useAuth.js
│   ├── useWorkOrders.js
│   └── useParts.js
├── utils/
│   ├── formatters.js
│   ├── validators.js
│   └── constants.js
├── App.jsx
└── main.jsx
```

### **Routing**

```javascript
// Protected routes per ruolo
const routes = {
  GM: ['/dashboard', '/work-orders', '/customers', '/vehicles', '/parts', '/reports'],
  CMM: ['/dashboard', '/work-orders', '/parts'],
  CBM: ['/dashboard', '/work-orders', '/parts']
}
```

---

## 🔐 SICUREZZA

### **Autenticazione**
- JWT con refresh token
- Password hashing (bcrypt)
- Session timeout: 8 ore
- Refresh token: 30 giorni

### **Autorizzazione**
- Role-Based Access Control (RBAC)
- Middleware per verifica permessi
- Validazione input (Pydantic)

### **Protezione**
- CORS configurato
- Rate limiting
- SQL injection prevention (ORM)
- XSS protection
- HTTPS obbligatorio (produzione)

---

## ⚡ PERFORMANCE

### **Backend**
- Async/await per I/O non bloccante
- Connection pooling database
- Caching query frequenti
- Pagination risultati

### **Frontend**
- Code splitting
- Lazy loading componenti
- React Query per caching
- Debouncing ricerche

---

## 🚀 DEPLOY

### **Sviluppo Locale**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### **Produzione (Render/Railway)**
- Deploy automatico da Git
- Environment variables
- Database PostgreSQL gestito
- SSL automatico
- Backup giornalieri

---

**Documento creato:** 09/02/2026  
**Versione:** 1.0
