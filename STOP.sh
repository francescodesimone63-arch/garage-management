#!/bin/bash

# Script per fermare il Garage Management System

echo "🛑 Arresto Garage Management System..."

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Ferma il backend
if [ -f "$PROJECT_DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_DIR/.backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${RED}🔴 Arresto Backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID
        rm "$PROJECT_DIR/.backend.pid"
    else
        echo "Backend non in esecuzione"
        rm "$PROJECT_DIR/.backend.pid"
    fi
fi

# Ferma il frontend
if [ -f "$PROJECT_DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_DIR/.frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${RED}🔴 Arresto Frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        rm "$PROJECT_DIR/.frontend.pid"
    else
        echo "Frontend non in esecuzione"
        rm "$PROJECT_DIR/.frontend.pid"
    fi
fi

# Pulizia aggiuntiva: termina tutti i processi sulle porte 8000 e 3000
echo "🧹 Pulizia porte..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo -e "${GREEN}✅ Sistema arrestato${NC}"
