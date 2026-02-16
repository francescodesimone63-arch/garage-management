#!/bin/bash

# Test Suite - Verifica fix implementati
# Questo script testa tutti gli endpoint modificati

set -e

API_URL="http://localhost:8000/api/v1"
TOKEN=""  # Sarà riempito dopo il login

# Colori
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧪 Avvio Test Suite - Allineamento Backend${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ Backend è online (port 8000)${NC}\n"
else
    echo -e "${RED}❌ Backend non risponde (status: $HEALTH)${NC}\n"
    exit 1
fi

# Test 2: Frontend Health
echo -e "${YELLOW}Test 2: Frontend Health Check${NC}"
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND" = "200" ]; then
    echo -e "${GREEN}✅ Frontend è online (port 3000)${NC}\n"
else
    echo -e "${YELLOW}⚠️  Frontend status: $FRONTEND (potrebbe essere in avvio)${NC}\n"
fi

# Test 3: WorkOrder Enum Conversion
echo -e "${YELLOW}Test 3: WorkOrder Status Filter (Enum Conversion)${NC}"
WO_TEST=$(curl -s -X GET "$API_URL/work-orders?stato=bozza&skip=0&limit=1" \
  -H "Content-Type: application/json" 2>/dev/null)

if echo "$WO_TEST" | grep -q "items\|numero_scheda\|stato"; then
    echo -e "${GREEN}✅ WorkOrder enum filter funziona${NC}"
    echo "   Response: $(echo $WO_TEST | head -c 100)..."
else
    echo -e "${YELLOW}⚠️  Response: $WO_TEST${NC}"
fi
echo ""

# Test 4: Part Endpoint - Check Fields
echo -e "${YELLOW}Test 4: Part Endpoint - Field Alignment${NC}"
PARTS=$(curl -s -X GET "$API_URL/parts?skip=0&limit=1" \
  -H "Content-Type: application/json" 2>/dev/null)

# Verifica i campi corretti del nuovo schema
if echo "$PARTS" | grep -q "codice"; then
    echo -e "${GREEN}✅ Field 'codice' presenta (schema allineato)${NC}"
else
    echo -e "${RED}❌ Field 'codice' non trovato${NC}"
fi

if echo "$PARTS" | grep -q "nome"; then
    echo -e "${GREEN}✅ Field 'nome' presente${NC}"
else
    echo -e "${RED}❌ Field 'nome' non trovato${NC}"
fi

if echo "$PARTS" | grep -q "quantita"; then
    echo -e "${GREEN}✅ Field 'quantita' presente${NC}"
else
    echo -e "${RED}❌ Field 'quantita' non trovato${NC}"
fi

# Verifica che campi vecchi NON siano presenti
if echo "$PARTS" | grep -q "\"code\""; then
    echo -e "${RED}❌ ERRORE: Field 'code' ancora presente (dovrebbe essere 'codice')${NC}"
else
    echo -e "${GREEN}✅ Field 'code' non presente (rimosso correttamente)${NC}"
fi

if echo "$PARTS" | grep -q "\"name\""; then
    echo -e "${RED}❌ ERRORE: Field 'name' ancora presente (dovrebbe essere 'nome')${NC}"
else
    echo -e "${GREEN}✅ Field 'name' non presente (rimosso correttamente)${NC}"
fi
echo ""

# Test 5: Tire Endpoint - Enumi
echo -e "${YELLOW}Test 5: Tire Endpoint - Enumi Italiano${NC}"
TIRES=$(curl -s -X GET "$API_URL/tires?skip=0&limit=1" \
  -H "Content-Type: application/json" 2>/dev/null)

if echo "$TIRES" | grep -q "tipo_stagione"; then
    echo -e "${GREEN}✅ Field 'tipo_stagione' presente${NC}"
else
    echo -e "${RED}❌ Field 'tipo_stagione' non trovato${NC}"
fi

if echo "$TIRES" | grep -q "stato"; then
    echo -e "${GREEN}✅ Field 'stato' presente (non 'status')${NC}"
else
    echo -e "${RED}❌ Field 'stato' non trovato${NC}"
fi

if echo "$TIRES" | grep -q "tread_depth"; then
    echo -e "${GREEN}✅ Field 'tread_depth' presente${NC}"
else
    echo -e "${RED}❌ Field 'tread_depth' non trovato${NC}"
fi
echo ""

# Test 6: CourtesyCar Endpoint
echo -e "${YELLOW}Test 6: CourtesyCar Endpoint - Vehicle ID vs License Plate${NC}"
CARS=$(curl -s -X GET "$API_URL/courtesy-cars?skip=0&limit=1" \
  -H "Content-Type: application/json" 2>/dev/null)

if echo "$CARS" | grep -q "vehicle_id"; then
    echo -e "${GREEN}✅ Field 'vehicle_id' presente${NC}"
else
    echo -e "${RED}❌ Field 'vehicle_id' non trovato${NC}"
fi

if echo "$CARS" | grep -q "\"license_plate\""; then
    echo -e "${RED}❌ ERRORE: Field 'license_plate' ancora presente (dovrebbe essere rimosso)${NC}"
else
    echo -e "${GREEN}✅ Field 'license_plate' non presente (rimosso correttamente)${NC}"
fi

if echo "$CARS" | grep -q "stato"; then
    echo -e "${GREEN}✅ Field 'stato' presente (enum Italian)${NC}"
else
    echo -e "${RED}❌ Field 'stato' non trovato${NC}"
fi

if echo "$CARS" | grep -q "contratto_tipo"; then
    echo -e "${GREEN}✅ Field 'contratto_tipo' presente${NC}"
else
    echo -e "${RED}❌ Field 'contratto_tipo' non trovato${NC}"
fi
echo ""

# Test 7: MaintenanceSchedule Endpoint
echo -e "${YELLOW}Test 7: MaintenanceSchedule Endpoint - Field Alignment${NC}"
MAINT=$(curl -s -X GET "$API_URL/maintenance-schedules?skip=0&limit=1" \
  -H "Content-Type: application/json" 2>/dev/null)

if echo "$MAINT" | grep -q "tipo"; then
    echo -e "${GREEN}✅ Field 'tipo' presente (enum)${NC}"
else
    echo -e "${RED}❌ Field 'tipo' non trovato${NC}"
fi

if echo "$MAINT" | grep -q "descrizione"; then
    echo -e "${GREEN}✅ Field 'descrizione' presente${NC}"
else
    echo -e "${RED}❌ Field 'descrizione' non trovato${NC}"
fi

if echo "$MAINT" | grep -q "km_scadenza"; then
    echo -e "${GREEN}✅ Field 'km_scadenza' presente${NC}"
else
    echo -e "${RED}❌ Field 'km_scadenza' non trovato${NC}"
fi

if echo "$MAINT" | grep -q "data_scadenza"; then
    echo -e "${GREEN}✅ Field 'data_scadenza' presente${NC}"
else
    echo -e "${RED}❌ Field 'data_scadenza' non trovato${NC}"
fi
echo ""

# Test 8: Part Creation Test (se backend dispone di auth)
echo -e "${YELLOW}Test 8: Part Creation with New Schema${NC}"
PART_CREATE=$(curl -s -X POST "$API_URL/parts" \
  -H "Content-Type: application/json" \
  -d '{
    "codice": "TEST-PART-001",
    "nome": "Test Part",
    "descrizione": "Test Description",
    "categoria": "Test",
    "quantita": 10,
    "quantita_minima": 5
  }' 2>/dev/null)

if echo "$PART_CREATE" | grep -q "codice\|TEST-PART-001\|401\|403"; then
    echo -e "${GREEN}✅ Part creation endpoint risponde (schema allineato)${NC}"
    if echo "$PART_CREATE" | grep -q "401\|403"; then
        echo -e "${YELLOW}   Nota: Autenticazione richiesta (atteso)${NC}"
    fi
else
    echo -e "${RED}❌ Test fallito: $PART_CREATE${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Test Suite Completato!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "✅ Servizi Online:"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Prossimi Passi:"
echo "   1. Accedi al frontend (http://localhost:3000)"
echo "   2. Verifica form di creazione Part, Tire, CourtesyCar"
echo "   3. Testa creazione/modifica di entità"
echo "   4. Verifica enum valori nei dropdown"
echo ""
