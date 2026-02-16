# Garage Management System - Backend

Backend FastAPI per sistema gestionale officina meccanica e carrozzeria.

## 🚀 Quick Start

### Prerequisiti

- Python 3.9+
- PostgreSQL 13+
- pip

### Installazione Rapida

```bash
# 1. Clona il repository e vai nella directory backend
cd garage-management/backend

# 2. Esegui lo script di setup (macOS/Linux)
chmod +x setup.sh
./setup.sh

# 3. Avvia il server
python main.py
```

Il server sarà disponibile su `http://localhost:8000`

### Installazione Manuale

```bash
# 1. Crea virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura database
cp .env.example .env
# Modifica .env con le tue credenziali

# 4. Crea database PostgreSQL
createdb garage_management

# 5. Popola database (opzionale)
python scripts/seed_database.py

# 6. Avvia server
python main.py
```

## 📚 Documentazione API

Una volta avviato il server, la documentazione interattiva è disponibile su:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔐 Autenticazione

Il sistema usa JWT (JSON Web Tokens) per l'autenticazione.

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@garage.com&password=admin123"
```

### Credenziali di Default (dopo seed)

- **Admin**: admin@garage.com / admin123
- **GM**: gm@garage.com / gm123
- **Officina**: officina@garage.com / officina123
- **Carrozzeria**: carrozzeria@garage.com / carrozzeria123

## 📋 Endpoint Principali

### Autenticazione
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registrazione
- `POST /api/auth/refresh` - Rinnova token
- `GET /api/auth/me` - Info utente corrente

### Utenti
- `GET /api/users/` - Lista utenti
- `POST /api/users/` - Crea utente
- `GET /api/users/{id}` - Dettagli utente
- `PUT /api/users/{id}` - Aggiorna utente
- `DELETE /api/users/{id}` - Elimina utente

### Clienti
- `GET /api/customers/` - Lista clienti (con ricerca)
- `POST /api/customers/` - Crea cliente
- `GET /api/customers/{id}` - Dettagli cliente
- `GET /api/customers/{id}/stats` - Statistiche cliente
- `PUT /api/customers/{id}` - Aggiorna cliente
- `DELETE /api/customers/{id}` - Elimina cliente

### Veicoli
- `GET /api/vehicles/` - Lista veicoli (con filtri)
- `POST /api/vehicles/` - Crea veicolo
- `GET /api/vehicles/{id}` - Dettagli veicolo
- `GET /api/vehicles/{id}/history` - Storico veicolo
- `GET /api/vehicles/{id}/maintenance-status` - Stato manutenzione
- `PUT /api/vehicles/{id}` - Aggiorna veicolo
- `DELETE /api/vehicles/{id}` - Elimina veicolo

### Ordini di Lavoro
- `GET /api/work-orders/` - Lista ordini (con filtri)
- `POST /api/work-orders/` - Crea ordine
- `GET /api/work-orders/{id}` - Dettagli ordine
- `GET /api/work-orders/stats` - Statistiche ordini
- `GET /api/work-orders/calendar` - Vista calendario
- `PUT /api/work-orders/{id}` - Aggiorna ordine
- `PATCH /api/work-orders/{id}/status` - Cambia stato
- `DELETE /api/work-orders/{id}` - Elimina ordine

## 🗄️ Database

### Struttura

Il sistema gestisce:
- **Users**: Utenti sistema (admin, gm, workshop, bodyshop)
- **Customers**: Clienti
- **Vehicles**: Veicoli clienti
- **WorkOrders**: Ordini di lavoro/schede intervento
- **Parts**: Ricambi
- **Tires**: Pneumatici
- **CourtesyCars**: Auto di cortesia
- **MaintenanceSchedules**: Scadenzario manutenzioni
- **Notifications**: Notifiche
- **CalendarEvents**: Eventi calendario
- **Documents**: Documenti
- **ActivityLogs**: Log attività

### Migrations con Alembic

```bash
# Crea una nuova migration
alembic revision --autogenerate -m "Descrizione modifiche"

# Applica migrations
alembic upgrade head

# Rollback ultima migration
alembic downgrade -1

# Visualizza storia migrations
alembic history
```

## 🛠️ Script Utility

### Seed Database
Popola il database con dati di test:
```bash
python scripts/seed_database.py
```

### Crea Admin
Crea un nuovo utente amministratore:
```bash
python scripts/create_admin.py
```

## 🔧 Configurazione

### Variabili d'Ambiente (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/garage_management

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Application
PROJECT_NAME=Garage Management System
VERSION=1.0.0
API_V1_STR=/api
```

## 🧪 Testing

```bash
# Installa dipendenze di test
pip install pytest pytest-cov pytest-asyncio httpx

# Esegui tests
pytest

# Con coverage
pytest --cov=app tests/
```

## 📦 Struttura Progetto

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── customers.py
│   │       │   ├── vehicles.py
│   │       │   └── work_orders.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── deps.py
│   ├── models/
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── vehicle.py
│   │   └── ...
│   ├── schemas/
│   │   ├── user.py
│   │   ├── customer.py
│   │   └── ...
│   └── __init__.py
├── alembic/
│   ├── versions/
│   └── env.py
├── scripts/
│   ├── seed_database.py
│   └── create_admin.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🚧 Stato Implementazione

### ✅ Completato
- Core system (config, database, security)
- Modelli database (11 entità)
- Schemi Pydantic
- Autenticazione JWT
- Endpoint: Auth, Users, Customers, Vehicles, Work Orders
- Alembic migrations setup
- Script seed database

### 🔄 In Sviluppo
- Altri endpoint CRUD (Parts, Tires, ecc.)
- Business logic avanzata
- Notifiche automatiche
- Integrazioni esterne

### 📋 TODO
- Testing completo
- Docker setup
- CI/CD pipeline
- Documentazione avanzata

## 🤝 Contributi

Per contribuire al progetto:
1. Fork il repository
2. Crea un branch per la feature
3. Commit le modifiche
4. Push al branch
5. Apri una Pull Request

## 📄 Licenza

Proprietario - Tutti i diritti riservati

## 📞 Supporto

Per supporto o domande, contatta il team di sviluppo.

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: 09/02/2026
