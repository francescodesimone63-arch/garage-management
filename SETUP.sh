#!/bin/bash

# Script di setup iniziale per Garage Management System

echo "🔧 Setup Garage Management System..."
echo ""

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ========================================
# 1. SETUP BACKEND
# ========================================
echo -e "${GREEN}📦 Setup Backend...${NC}"
cd "$BACKEND_DIR"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non trovato. Installalo prima di continuare.${NC}"
    exit 1
fi

echo "✓ Python $(python3 --version)"

# Crea virtual environment se non esiste
if [ ! -d "venv" ]; then
    echo "Creazione virtual environment..."
    python3 -m venv venv
fi

# Attiva virtual environment
source venv/bin/activate

# Installa dipendenze
echo "Installazione dipendenze Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Verifica file .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  File .env non trovato. Copia da .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  IMPORTANTE: Modifica il file .env con le tue configurazioni!${NC}"
fi

# Inizializza database
echo "Inizializzazione database..."
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"

# Esegui migrazioni Alembic
echo "Esecuzione migrazioni database..."
alembic upgrade head 2>/dev/null || echo "Migrazioni non disponibili o già eseguite"

# Crea utente admin
echo "Creazione utente admin..."
python scripts/create_admin.py

# Seed database (opzionale)
read -p "Vuoi popolare il database con dati di esempio? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    python scripts/seed_database.py
fi

echo -e "${GREEN}✅ Backend setup completato${NC}"
echo ""

# ========================================
# 2. SETUP FRONTEND
# ========================================
echo -e "${GREEN}🎨 Setup Frontend...${NC}"
cd "$FRONTEND_DIR"

# Verifica Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js non trovato. Installalo prima di continuare.${NC}"
    exit 1
fi

echo "✓ Node $(node --version)"
echo "✓ npm $(npm --version)"

# Installa dipendenze (se non già fatto)
if [ ! -d "node_modules" ]; then
    echo "Installazione dipendenze npm..."
    npm install
fi

# Verifica file .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  File .env non trovato. Copia da .env.example...${NC}"
    cp .env.example .env
fi

echo -e "${GREEN}✅ Frontend setup completato${NC}"
echo ""

# ========================================
# 3. RIEPILOGO
# ========================================
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Setup completato con successo!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📋 Prossimi passi:"
echo ""
echo "1. Verifica le configurazioni in:"
echo "   - backend/.env"
echo "   - frontend/.env"
echo ""
echo "2. Avvia il sistema:"
echo "   ./START.sh"
echo ""
echo "3. Accedi all'applicazione:"
echo "   http://localhost:3000"
echo ""
echo "4. Credenziali di default:"
echo "   Email: admin@garage.local"
echo "   Password: admin123"
echo ""
echo "📚 Documentazione disponibile in:"
echo "   - README.md"
echo "   - backend/README.md"
echo "   - API_DOCUMENTATION.md"
echo ""
