#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin@garage.local&password=admin123' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:50}..."
echo ""

# Create test vehicle
echo "Creating test vehicle..."
curl -s -X POST 'http://localhost:8000/api/v1/vehicles/' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": 1,
    "targa": "TEST123",
    "marca": "TestMarca",
    "modello": "TestModello",
    "anno": 2020,
    "numero_telaio": "12345678901234567",
    "alimentazione": "benzina",
    "km_attuali": 10000
  }' | python3 -m json.tool

echo ""
echo "Fetching vehicles list..."
curl -s "http://localhost:8000/api/v1/vehicles/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
