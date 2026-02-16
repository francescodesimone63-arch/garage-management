#!/bin/bash

# Script di avvio completo per Garage Management System
# Questo script avvia sia il backend che il frontend

echo "🚀 Avvio Garage Management System..."
echo ""

# Directory del progetto
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funzione per controllare se un processo è in esecuzione
check_process() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ Porta $1 già in uso${NC}"
        return 1
    fi
    return 0
}

# Verifica porte
echo "📡 Verifica porte disponibili..."
if ! check_process 8000; then
    echo -e "${YELLOW}⚠️  Il backend potrebbe essere già in esecuzione sulla porta 8000${NC}"
    read -p "Vuoi continuare comunque? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

if ! check_process 3000; then
    echo -e "${YELLOW}⚠️  Il frontend potrebbe essere già in esecuzione sulla porta 3000${NC}"
    read -p "Vuoi continuare comunque? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Avvia il backend
echo ""
echo -e "${GREEN}🔧 Avvio Backend (FastAPI)...${NC}"
cd "$BACKEND_DIR"

# Attiva virtual environment se esiste
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Avvia il backend in background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend avviato con PID: $BACKEND_PID"
echo -e "${GREEN}✅ Backend disponibile su: http://localhost:8000${NC}"
echo -e "${GREEN}✅ API Docs disponibile su: http://localhost:8000/docs${NC}"

# Attendi che il backend sia pronto
echo "⏳ Attendi avvio backend..."
sleep 5

# Avvia il frontend
echo ""
echo -e "${GREEN}🎨 Avvio Frontend (React + Vite)...${NC}"
cd "$FRONTEND_DIR"

# Avvia il frontend in background
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend avviato con PID: $FRONTEND_PID"
echo -e "${GREEN}✅ Frontend disponibile su: http://localhost:3000${NC}"

# Salva i PID per poterli fermare in seguito
echo "$BACKEND_PID" > "$PROJECT_DIR/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_DIR/.frontend.pid"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}🎉 Sistema avviato con successo!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📱 Apri il browser su: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Credenziali di accesso di default:"
echo "  Email: admin@garage.local"
echo "  Password: admin123"
echo ""
echo "Per fermare il sistema, esegui: ./STOP.sh"
echo ""
echo "Log files:"
echo "  Backend: $BACKEND_DIR/backend.log"
echo "  Frontend: $FRONTEND_DIR/frontend.log"
echo ""

# Mantieni lo script in esecuzione
echo "Premi Ctrl+C per fermare tutti i servizi..."
wait
