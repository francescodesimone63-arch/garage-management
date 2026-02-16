#!/bin/bash

# Script di test completo del sistema Garage Management System
# Questo script verifica l'integrità di tutti gli endpoint principali

echo "🧪 TEST DI INTEGRITÀ SISTEMA GARAGE MANAGEMENT"
echo "=================================================="
echo ""

# Colori
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_URL="http://localhost:8000/api/v1"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Funzione per fare un test
run_test() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_code=$5
    
    printf "%-50s" "🔍 $test_name..."
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -1)
    # Usa sed per rimuovere l'ultima riga (codice HTTP) senza errori "illegal line count"
    body=$(printf '%s\n' "$response" | sed '$d')
    
    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED (Expected $expected_code, got $http_code)${NC}"
        echo "   Response: $body"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi
}

# Test login
echo ""
echo -e "${YELLOW}🔐 Test Autenticazione${NC}"
run_test "Login con credenziali corrette" "POST" "/auth/login" '{"username":"admin@garage.local","password":"admin123"}' "200"

# Salva il token per i test autenticati
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin@garage.local","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Impossibile ottenere il token. I test autenticati verranno saltati.${NC}"
else
    echo -e "${GREEN}✅ Token ottenuto correttamente${NC}"
    
    # Test endpoint autenticati
    echo ""
    echo -e "${YELLOW}📋 Test WorkOrders Autenticati${NC}"
    
    # Lista work orders (usa sempre la slash finale per evitare redirect 307)
    printf "%-50s" "🔍 GET work orders list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/work-orders/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi
    
    # GET single work order (ID 1)
    printf "%-50s" "🔍 GET work order ID #1..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/work-orders/1" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    body=$(printf '%s\n' "$response" | sed '$d')
    if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        echo "   Response: $body"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test clienti
    echo ""
    echo -e "${YELLOW}👥 Test Clienti Autenticati${NC}"

    # Lista clienti
    printf "%-50s" "🔍 GET customers list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/customers/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Dettaglio cliente ID 1 (accetta 200 o 404 a seconda dei dati)
    printf "%-50s" "🔍 GET customer ID #1..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/customers/1" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    body=$(printf '%s\n' "$response" | sed '$d')
    if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        echo "   Response: $body"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test veicoli
    echo ""
    echo -e "${YELLOW}🚗 Test Veicoli Autenticati${NC}"

    # Lista veicoli
    printf "%-50s" "🔍 GET vehicles list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/vehicles/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Dettaglio veicolo ID 1 (accetta 200 o 404 a seconda dei dati)
    printf "%-50s" "🔍 GET vehicle ID #1..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/vehicles/1" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    body=$(printf '%s\n' "$response" | sed '$d')
    if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        echo "   Response: $body"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test interventi (solo lista, non crea/modifica dati)
    echo ""
    echo -e "${YELLOW}🛠️  Test Interventi Autenticati${NC}"

    # Lista interventi per scheda lavoro ID 1
    printf "%-50s" "🔍 GET interventions for work order #1..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/work-orders/1/interventions" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ] || [ "$http_code" == "404" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test ricambi (parts)
    echo ""
    echo -e "${YELLOW}🔩 Test Ricambi Autenticati${NC}"

    # Lista ricambi
    printf "%-50s" "🔍 GET parts list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/parts/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test pneumatici (tires)
    echo ""
    echo -e "${YELLOW}🛞 Test Pneumatici Autenticati${NC}"

    # Lista pneumatici
    printf "%-50s" "🔍 GET tires list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/tires/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test auto di cortesia
    echo ""
    echo -e "${YELLOW}🚙 Test Auto Cortesia Autenticati${NC}"

    # Lista auto cortesia
    printf "%-50s" "🔍 GET courtesy cars list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/courtesy-cars/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test scadenziario manutenzioni
    echo ""
    echo -e "${YELLOW}📆 Test Scadenziario Manutenzioni Autenticati${NC}"

    # Lista scadenziari manutenzione
    printf "%-50s" "🔍 GET maintenance schedules list..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/maintenance-schedules/" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi

    # Test dashboard summary
    echo ""
    echo -e "${YELLOW}📊 Test Dashboard Autenticati${NC}"

    printf "%-50s" "🔍 GET dashboard summary..."
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/dashboard/summary" \
        -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✅ OK ($http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED+1))
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED+1))
    fi
fi

# Test health check (non autenticato) - usa direttamente l'endpoint root /health
echo ""
echo -e "${YELLOW}🏥 Test Health Check${NC}"
printf "%-50s" "🔍 Health check..."
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health")
if [ "$HEALTH_CODE" == "200" ]; then
    echo -e "${GREEN}✅ OK ($HEALTH_CODE)${NC}"
    TESTS_PASSED=$((TESTS_PASSED+1))
else
    echo -e "${RED}❌ FAILED (Expected 200, got $HEALTH_CODE)${NC}"
    TESTS_FAILED=$((TESTS_FAILED+1))
fi

# Riassunto
echo ""
echo "=================================================="
echo -e "📊 RISULTATI TEST: ${GREEN}$TESTS_PASSED Passed${NC} / ${RED}$TESTS_FAILED Failed${NC}"
echo "=================================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ TUTTI I TEST SONO PASSATI!${NC}"
    exit 0
else
    echo -e "${RED}❌ ALCUNI TEST HANNO FALLITO.${NC}"
    exit 1
fi
