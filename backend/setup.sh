#!/bin/bash

# Script di setup completo per Garage Management System Backend

echo "============================================================"
echo "  GARAGE MANAGEMENT SYSTEM - SETUP BACKEND"
echo "============================================================"
echo ""

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica Python
echo "Verifica Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 non trovato. Installalo prima di continuare.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 trovato${NC}"
echo ""

# Verifica PostgreSQL
echo "Verifica PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL non trovato. Assicurati di averlo installato.${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL trovato${NC}"
fi
echo ""

# Crea virtual environment
echo "Creazione virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment creato${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment già esistente${NC}"
fi
echo ""

# Attiva virtual environment
echo "Attivazione virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment attivato${NC}"
echo ""

# Installa dipendenze
echo "Installazione dipendenze..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dipendenze installate${NC}"
echo ""

# Crea file .env se non esiste
if [ ! -f ".env" ]; then
    echo "Creazione file .env..."
    cp .env.example .env
    echo -e "${GREEN}✓ File .env creato${NC}"
    echo -e "${YELLOW}⚠ IMPORTANTE: Modifica il file .env con le tue configurazioni!${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ File .env già esistente${NC}"
    echo ""
fi

# Richiedi informazioni database
echo "============================================================"
echo "  CONFIGURAZIONE DATABASE"
echo "============================================================"
echo ""
read -p "Nome database [garage_management]: " DB_NAME
DB_NAME=${DB_NAME:-garage_management}

read -p "Username PostgreSQL [postgres]: " DB_USER
DB_USER=${DB_USER:-postgres}

read -sp "Password PostgreSQL: " DB_PASSWORD
echo ""

read -p "Host PostgreSQL [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Porta PostgreSQL [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

# Aggiorna .env con configurazione database
echo ""
echo "Aggiornamento configurazione database in .env..."
sed -i.bak "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}|" .env
echo -e "${GREEN}✓ Configurazione database aggiornata${NC}"
echo ""

# Chiedi se creare il database
read -p "Vuoi creare il database '${DB_NAME}'? (s/n) [s]: " CREATE_DB
CREATE_DB=${CREATE_DB:-s}

if [ "$CREATE_DB" = "s" ] || [ "$CREATE_DB" = "S" ]; then
    echo "Creazione database..."
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database creato${NC}"
    else
        echo -e "${YELLOW}⚠ Database potrebbe già esistere o errore di connessione${NC}"
    fi
    echo ""
fi

# Chiedi se popolare il database
read -p "Vuoi popolare il database con dati di test? (s/n) [s]: " SEED_DB
SEED_DB=${SEED_DB:-s}

if [ "$SEED_DB" = "s" ] || [ "$SEED_DB" = "S" ]; then
    echo "Popolamento database..."
    python scripts/seed_database.py
    echo ""
fi

# Riepilogo
echo "============================================================"
echo "  SETUP COMPLETATO!"
echo "============================================================"
echo ""
echo "Comandi utili:"
echo "  - Avvia server:       python main.py"
echo "  - Crea admin:         python scripts/create_admin.py"
echo "  - Seed database:      python scripts/seed_database.py"
echo "  - Crea migration:     alembic revision --autogenerate -m 'message'"
echo "  - Applica migration:  alembic upgrade head"
echo ""
echo "API Documentation:"
echo "  - Swagger UI:  http://localhost:8000/api/docs"
echo "  - ReDoc:       http://localhost:8000/api/redoc"
echo ""
echo "============================================================"
