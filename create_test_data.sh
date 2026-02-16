#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get token
echo -e "${BLUE}1. Getting authentication token...${NC}"
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@garage.local&password=admin123' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo -e "${RED}Error: Could not get token${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Token obtained${NC}"
echo ""

# Create customer
echo -e "${BLUE}2. Creating test customer...${NC}"
CUSTOMER=$(curl -s -X POST 'http://localhost:8000/api/v1/customers/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "nome": "Mario",
    "cognome": "Rossi",
    "tipo": "privato",
    "codice_fiscale": "RSSMRA80A01F205X",
    "email": "mario.rossi@test.com",
    "telefono": "3331234567",
    "indirizzo": "Via Roma 1",
    "citta": "Milano",
    "cap": "20100"
  }')

CUSTOMER_ID=$(echo $CUSTOMER | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$CUSTOMER_ID" ]; then
  echo -e "${RED}Error creating customer:${NC}"
  echo $CUSTOMER | python3 -m json.tool
  exit 1
fi

echo -e "${GREEN}✓ Customer created with ID: $CUSTOMER_ID${NC}"
echo ""

# Create vehicle
echo -e "${BLUE}3. Creating test vehicle...${NC}"
VEHICLE=$(curl -s -X POST 'http://localhost:8000/api/v1/vehicles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"customer_id\": $CUSTOMER_ID,
    \"targa\": \"AB123CD\",
    \"marca\": \"Fiat\",
    \"modello\": \"Punto\",
    \"anno\": 2020,
    \"numero_telaio\": \"12345678901234567\",
    \"alimentazione\": \"benzina\",
    \"cilindrata\": 1200,
    \"km_attuali\": 50000,
    \"note\": \"Veicolo di test\"
  }")

VEHICLE_ID=$(echo $VEHICLE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$VEHICLE_ID" ]; then
  echo -e "${RED}Error creating vehicle:${NC}"
  echo $VEHICLE | python3 -m json.tool
  exit 1
fi

echo -e "${GREEN}✓ Vehicle created with ID: $VEHICLE_ID${NC}"
echo ""

# Fetch vehicles list
echo -e "${BLUE}4. Fetching vehicles list...${NC}"
curl -s "http://localhost:8000/api/v1/vehicles/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Test data created successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Now open:${NC} http://localhost:3000/vehicles"
echo -e "${BLUE}You should see:${NC} 1 vehicle in the table"
