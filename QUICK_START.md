# Quick Start Guide - Garage Management System

## 🚀 Avvio Rapido

### Setup Iniziale (Solo la prima volta)

```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management
./SETUP.sh
```

Lo script di setup:
1. ✅ Installa dipendenze Python (backend)
2. ✅ Installa dipendenze Node.js (frontend)
3. ✅ Crea il database
4. ✅ Crea l'utente admin
5. ✅ (Opzionale) Popola con dati di esempio

### Avvio Sistema

```bash
./START.sh
```

Il sistema avvierà automaticamente:
- 🔧 **Backend** (FastAPI) su http://localhost:8000
- 🎨 **Frontend** (React) su http://localhost:3000
- 📚 **API Docs** su http://localhost:8000/docs

### Arresto Sistema

```bash
./STOP.sh
```

## 📱 Accesso all'Applicazione

### URL
```
http://localhost:3000
```

### Credenziali di Default

**Admin:**
- Email: `admin@garage.local`
- Password: `admin123`

**Direttore Generale:**
- Email: `gm@garage.local`
- Password: `gm123`

**Capo Officina:**
- Email: `officina@garage.local`
- Password: `officina123`

**Capo Carrozzeria:**
- Email: `carrozzeria@garage.local`
- Password: `carrozzeria123`

**Reception:**
- Email: `reception@garage.local`
- Password: `reception123`

## 🔍 Verifica Sistema

### Backend
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend
Apri il browser su: http://localhost:3000

### API Documentation
Apri il browser su: http://localhost:8000/docs

## 📝 Operazioni Comuni

### Creare un nuovo utente admin
```bash
cd backend
source venv/bin/activate
python scripts/create_admin.py
```

### Popolare il database con dati di esempio
```bash
cd backend
source venv/bin/activate
python scripts/seed_database.py
```

### Visualizzare i log
```bash
# Backend
tail -f backend/backend.log

# Frontend
tail -f frontend/frontend.log
```

### Reset Database
```bash
cd backend
source venv/bin/activate
rm -f garage.db
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
python scripts/create_admin.py
```

## ⚠️ Troubleshooting

### Porta già in uso
```bash
# Verifica processi in esecuzione
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend

# Termina i processi
./STOP.sh
```

### Dipendenze mancanti
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Database corrotto
```bash
cd backend
rm -f garage.db
source venv/bin/activate
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
python scripts/create_admin.py
```

### Errori di autenticazione
1. Verifica che il backend sia avviato
2. Controlla le credenziali
3. Cancella localStorage del browser (F12 → Application → Local Storage)
4. Riprova il login

## 📚 Documentazione Completa

- [README.md](README.md) - Panoramica generale
- [SINTESI_ESECUTIVA.md](SINTESI_ESECUTIVA.md) - Sintesi esecutiva del progetto
- [SPECIFICHE_TECNICHE.md](SPECIFICHE_TECNICHE.md) - Specifiche tecniche dettagliate
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentazione API
- [DATABASE_SCHEMA.sql](DATABASE_SCHEMA.sql) - Schema database
- [WORKFLOW_OPERATIVI.md](WORKFLOW_OPERATIVI.md) - Workflow operativi
- [backend/README.md](backend/README.md) - Documentazione backend
- [FRONTEND_README.md](FRONTEND_README.md) - Documentazione frontend

## 🆘 Supporto

Per problemi o domande:
1. Consulta la documentazione
2. Verifica i log
3. Controlla che tutte le dipendenze siano installate
4. Verifica che le porte 8000 e 3000 siano disponibili

## 🎯 Prossimi Passi

1. ✅ Familiarizza con l'interfaccia
2. ✅ Crea alcuni clienti di test
3. ✅ Aggiungi veicoli
4. ✅ Crea ordini di lavoro
5. ✅ Esplora tutte le funzionalità
6. ✅ Personalizza le configurazioni
7. ✅ Integra con i tuoi dati reali

---

**Buon lavoro! 🚗🔧**
