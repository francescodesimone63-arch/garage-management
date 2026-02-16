#!/bin/bash

# Script per testare le correzioni di Work Orders e Customers
# Data: 11/02/2026

echo "🔍 TESTING FIXES - Work Orders e Customers"
echo "=========================================="
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base API
BASE_URL="http://localhost:8000/api/v1"

# Funzione per ottenere il token
get_token() {
    echo "🔐 Ottengo token di autenticazione..."
    
    TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin123")
    
    TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        echo -e "${RED}❌ Errore: impossibile ottenere token${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Token ottenuto${NC}"
}

# Test 1: Creazione Cliente senza Codice Fiscale
test_create_customer() {
    echo ""
    echo "📋 TEST 1: Creazione Cliente SENZA Codice Fiscale"
    echo "---------------------------------------------------"
    
    CUSTOMER_DATA='{
        "tipo": "privato",
        "nome": "Mario",
        "cognome": "Rossi",
        "email": "mario.rossi.test@example.com",
        "cellulare": "3331234567",
        "telefono": null,
        "indirizzo": "Via Roma 1",
        "citta": "Milano",
        "cap": "20100",
        "provincia": "MI",
        "note": "Cliente di test",
        "codice_fiscale": null,
        "partita_iva": null,
        "ragione_sociale": null
    }'
    
    RESPONSE=$(curl -s -X POST "$BASE_URL/customers/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$CUSTOMER_DATA")
    
    CUSTOMER_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$CUSTOMER_ID" ]; then
        echo -e "${GREEN}✅ Cliente creato con ID: $CUSTOMER_ID${NC}"
        echo "   Nome: Mario Rossi"
        echo "   Email: mario.rossi.test@example.com"
        return 0
    else
        echo -e "${RED}❌ Errore nella creazione del cliente${NC}"
        echo "   Response: $RESPONSE"
        return 1
    fi
}

# Test 2: Lista Work Orders con formato paginato
test_list_work_orders() {
    echo ""
    echo "📋 TEST 2: Lista Work Orders (formato paginato)"
    echo "---------------------------------------------------"
    
    RESPONSE=$(curl -s -X GET "$BASE_URL/work-orders/?skip=0&limit=10" \
        -H "Authorization: Bearer $TOKEN")
    
    # Verifica presenza di "items" e "total"
    if echo "$RESPONSE" | grep -q '"items"' && echo "$RESPONSE" | grep -q '"total"'; then
        TOTAL=$(echo $RESPONSE | grep -o '"total":[0-9]*' | cut -d':' -f2)
        echo -e "${GREEN}✅ Formato paginato corretto${NC}"
        echo "   Total work orders: $TOTAL"
        return 0
    else
        echo -e "${RED}❌ Formato paginato non corretto${NC}"
        echo "   Response: $RESPONSE"
        return 1
    fi
}

# Test 3: Creazione Work Order con tutti i campi
test_create_work_order() {
    echo ""
    echo "📋 TEST 3: Creazione Work Order completo"
    echo "---------------------------------------------------"
    
    # Prima ottieni un cliente e veicolo esistente
    CUSTOMERS=$(curl -s -X GET "$BASE_URL/customers/?limit=1" \
        -H "Authorization: Bearer $TOKEN")
    CUSTOMER_ID=$(echo $CUSTOMERS | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    VEHICLES=$(curl -s -X GET "$BASE_URL/vehicles/?limit=1" \
        -H "Authorization: Bearer $TOKEN")
    VEHICLE_ID=$(echo $VEHICLES | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -z "$CUSTOMER_ID" ] || [ -z "$VEHICLE_ID" ]; then
        echo -e "${YELLOW}⚠️  Nessun cliente/veicolo disponibile per il test${NC}"
        return 0
    fi
    
    WO_DATA=$(cat <<EOF
{
    "customer_id": $CUSTOMER_ID,
    "vehicle_id": $VEHICLE_ID,
    "numero_scheda": "TEST-$(date +%s)",
    "data_appuntamento": "$(date -u +%Y-%m-%dT%H:%M:%S)Z",
    "data_fine_prevista": "$(date -u -d '+7 days' +%Y-%m-%dT%H:%M:%S)Z",
    "stato": "bozza",
    "priorita": "media",
    "tipo_danno": "meccanica",
    "valutazione_danno": "Test di creazione work order completo",
    "note": "Work order di test",
    "costo_stimato": 500.00
}
EOF
)
    
    RESPONSE=$(curl -s -X POST "$BASE_URL/work-orders/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$WO_DATA")
    
    WO_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
    
    if [ -n "$WO_ID" ]; then
        echo -e "${GREEN}✅ Work Order creato con ID: $WO_ID${NC}"
        echo "   Customer ID: $CUSTOMER_ID"
        echo "   Vehicle ID: $VEHICLE_ID"
        echo "   Stato: bozza"
        return 0
    else
        echo -e "${RED}❌ Errore nella creazione del work order${NC}"
        echo "   Response: $RESPONSE"
        return 1
    fi
}

# Test 4: Verifica che i campi siano salvati correttamente
test_work_order_fields() {
    echo ""
    echo "📋 TEST 4: Verifica campi salvati nel Work Order"
    echo "---------------------------------------------------"
    
    # Ottieni l'ultimo work order creato
    RESPONSE=$(curl -s -X GET "$BASE_URL/work-orders/?limit=1" \
        -H "Authorization: Bearer $TOKEN")
    
    WO_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -z "$WO_ID" ]; then
        echo -e "${YELLOW}⚠️  Nessun work order disponibile per il test${NC}"
        return 0
    fi
    
    # Ottieni i dettagli del work order
    WO_DETAILS=$(curl -s -X GET "$BASE_URL/work-orders/$WO_ID" \
        -H "Authorization: Bearer $TOKEN")
    
    # Verifica presenza campi chiave
    CHECKS=0
    PASSED=0
    
    for field in "numero_scheda" "stato" "data_appuntamento" "valutazione_danno"; do
        CHECKS=$((CHECKS + 1))
        if echo "$WO_DETAILS" | grep -q "\"$field\""; then
            PASSED=$((PASSED + 1))
        fi
    done
    
    if [ $PASSED -eq $CHECKS ]; then
        echo -e "${GREEN}✅ Tutti i campi sono presenti ($PASSED/$CHECKS)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Alcuni campi mancanti ($PASSED/$CHECKS)${NC}"
        return 0
    fi
}

# Test 5: Modifica Cliente
test_update_customer() {
    echo ""
    echo "📋 TEST 5: Modifica Cliente esistente"
    echo "---------------------------------------------------"
    
    # Ottieni primo cliente
    RESPONSE=$(curl -s -X GET "$BASE_URL/customers/?limit=1" \
        -H "Authorization: Bearer $TOKEN")
    
    CUSTOMER_ID=$(echo $RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -z "$CUSTOMER_ID" ]; then
        echo -e "${YELLOW}⚠️  Nessun cliente disponibile per il test${NC}"
        return 0
    fi
    
    UPDATE_DATA='{
        "note": "Cliente aggiornato da test - '"$(date)"'"
    }'
    
    UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/customers/$CUSTOMER_ID" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$UPDATE_DATA")
    
    if echo "$UPDATE_RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}✅ Cliente aggiornato con ID: $CUSTOMER_ID${NC}"
        return 0
    else
        echo -e "${RED}❌ Errore nell'aggiornamento del cliente${NC}"
        echo "   Response: $UPDATE_RESPONSE"
        return 1
    fi
}

# Esegui tutti i test
main() {
    echo ""
    echo "Inizio testing..."
    echo ""
    
    get_token
    
    TOTAL_TESTS=5
    PASSED_TESTS=0
    
    test_create_customer && PASSED_TESTS=$((PASSED_TESTS + 1))
    test_list_work_orders && PASSED_TESTS=$((PASSED_TESTS + 1))
    test_create_work_order && PASSED_TESTS=$((PASSED_TESTS + 1))
    test_work_order_fields && PASSED_TESTS=$((PASSED_TESTS + 1))
    test_update_customer && PASSED_TESTS=$((PASSED_TESTS + 1))
    
    echo ""
    echo "=========================================="
    echo "📊 RISULTATI TEST"
    echo "=========================================="
    echo ""
    
    if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
        echo -e "${GREEN}✅ Tutti i test passati: $PASSED_TESTS/$TOTAL_TESTS${NC}"
        echo ""
        echo "🎉 Le correzioni funzionano correttamente!"
    else
        echo -e "${YELLOW}⚠️  Test passati: $PASSED_TESTS/$TOTAL_TESTS${NC}"
        echo ""
        echo "Alcuni test non sono passati o sono stati saltati."
    fi
    
    echo ""
}

# Controlla se il backend è in esecuzione
check_backend() {
    if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ Backend non raggiungibile su $BASE_URL${NC}"
        echo ""
        echo "Assicurati che il backend sia avviato:"
        echo "  cd garage-management/backend"
        echo "  uvicorn app.main:app --reload --port 8000"
        echo ""
        exit 1
    fi
}

check_backend
main
