# Testing Suite - Allineamento Backend-Frontend

**Data:** 11 Febbraio 2026  
**Scope:** Verifica completa dei fix implementati

---

## 🎯 Prerequisiti

```bash
# 1. Avviare il backend
cd /Users/francescodesimone/Sviluppo\ Python/garage-management/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 2. Avviare il frontend (in nuovo terminale)
cd /Users/francescodesimone/Sviluppo\ Python/garage-management/frontend
npm run dev  # localhost:3000

# 3. Ottenere token di autenticazione
# Fare login via UI o usare curl per login
```

---

## 📝 Test WorkOrder Endpoint

### Test 1.1: WorkOrder Filter con Status Enum Conversion
**Endpoint:** `GET /api/v1/work-orders?stato=bozza`  
**Expected:** Status filter funziona con corretto enum conversion

```bash
# Test con stato valido
curl -X GET "http://localhost:8000/api/v1/work-orders?stato=bozza" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Expected Response: 200 OK con lista di work orders in stato BOZZA

# Test con stato invalido
curl -X GET "http://localhost:8000/api/v1/work-orders?stato=invalid_status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 400 Bad Request con messaggio "Invalid status: invalid_status"
```

### Test 1.2: WorkOrder Response Fields
**Verifica:** I campi ritornati dal backend matchano i tipi TypeScript

```bash
curl -X GET "http://localhost:8000/api/v1/work-orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Campi attesi:**
```json
{
  "id": 1,
  "numero_scheda": "WO-2026-001",
  "stato": "bozza",
  "data_creazione": "2026-02-11T10:00:00",
  "vehicle_id": 1,
  "customer_id": 1,
  "tipo_danno": "...",
  "priorita": "media",
  "valutazione_danno": "...",
  "date_appuntamento": "2026-02-15T14:00:00",
  "auto_cortesia_id": null,
  "costo_stimato": 500.00
}
```

---

## 📦 Test Part Endpoint

### Test 2.1: Create Part con Campi Corretti
**Endpoint:** `POST /api/v1/parts`  
**Expected:** Part creato con i campi corretti del model

```bash
curl -X POST "http://localhost:8000/api/v1/parts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codice": "PART-EXAMPLE-001",
    "nome": "Filtro Olio Motore",
    "descrizione": "Filtro olio originale per motore benzina",
    "categoria": "Filtri",
    "marca": "Bosch",
    "modello": "0451103010",
    "quantita": 15,
    "quantita_minima": 5,
    "prezzo_acquisto": 25.50,
    "prezzo_vendita": 45.00,
    "fornitore": "Bosch Direct",
    "posizione_magazzino": "A-3-2",
    "tipo": "ricambio",
    "unita_misura": "pz",
    "note": "Compatibile con modelli 2019-2024"
  }'

# Expected Response: 201 Created con ID parte
# Verify: Nessun errore su campi inesistenti come "work_order_id", "prezzo_unitario"
```

### Test 2.2: Update Part
**Endpoint:** `PUT /api/v1/parts/{id}`

```bash
curl -X PUT "http://localhost:8000/api/v1/parts/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantita": 10,
    "quantita_minima": 3,
    "prezzo_vendita": 50.00
  }'

# Expected Response: 200 OK con parte aggiornati
```

### Test 2.3: List Parts con Filtri
**Endpoint:** `GET /api/v1/parts?skip=0&limit=10&search=filtro`

```bash
curl -X GET "http://localhost:8000/api/v1/parts?skip=0&limit=10&search=filtro" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK con lista parts filtrati
# Body deve avere: codice, nome, descrizione, quantita, quantita_minima, prezzo_acquisto, etc.
```

### Test 2.4: Get Low Stock Parts
**Endpoint:** `GET /api/v1/parts/low-stock`

```bash
curl -X GET "http://localhost:8000/api/v1/parts/low-stock" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK - Parts dove quantita <= quantita_minima
```

---

## 🛞 Test Tire Endpoint

### Test 3.1: Create Tire con Enumi Corretti
**Endpoint:** `POST /api/v1/tires`

```bash
curl -X POST "http://localhost:8000/api/v1/tires" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "tipo_stagione": "estivo",
    "marca": "Michelin",
    "modello": "Pilot Sport 4",
    "misura": "225/45 R17",
    "data_deposito": "2026-02-01T10:00:00Z",
    "data_ultimo_cambio": "2026-02-11T14:30:00Z",
    "data_prossimo_cambio": "2026-06-11T14:30:00Z",
    "stato": "depositati",
    "position": "rear_left",
    "condition": "good",
    "tread_depth": 8,
    "manufacture_date": "2025-06-15T00:00:00Z",
    "last_rotation_date": "2026-02-01T10:00:00Z",
    "last_rotation_km": 50000,
    "posizione_deposito": "Scaffale 5-A",
    "note": "Pneumatici estivi 2025"
  }'

# Expected Response: 201 Created
# Verify: Enumi tipo_stagione='estivo', stato='depositati', condition='good' sono corretti
```

### Test 3.2: Update Tire
**Endpoint:** `PUT /api/v1/tires/{id}`

```bash
curl -X PUT "http://localhost:8000/api/v1/tires/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tread_depth": 7,
    "condition": "fair",
    "data_prossimo_cambio": "2026-05-15T14:30:00Z"
  }'

# Expected Response: 200 OK
```

### Test 3.3: Get Tires for Vehicle
**Endpoint:** `GET /api/v1/tires?vehicle_id=1`

```bash
curl -X GET "http://localhost:8000/api/v1/tires?vehicle_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK con list tires per vehicle
# Verify: Fields tipo_stagione, marca, modello, misura, stato, etc.
```

---

## 🚗 Test CourtesyCar Endpoint

### Test 4.1: Create CourtesyCar
**Endpoint:** `POST /api/v1/courtesy-cars`

```bash
curl -X POST "http://localhost:8000/api/v1/courtesy-cars" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 2,
    "contratto_tipo": "leasing",
    "fornitore_contratto": "Hertz",
    "data_inizio_contratto": "2026-01-01",
    "data_scadenza_contratto": "2027-01-01",
    "canone_mensile": 450.00,
    "km_inclusi_anno": 12000,
    "stato": "disponibile",
    "note": "Auto cortesia principale per grandi lavori"
  }'

# Expected Response: 201 Created
# Verify: Usa vehicle_id, non license_plate
# Verify: Enum stato='disponibile' (not 'available')
```

### Test 4.2: Get Available CourtesyCars
**Endpoint:** `GET /api/v1/courtesy-cars/available`

```bash
curl -X GET "http://localhost:8000/api/v1/courtesy-cars/available" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK
# Verify: Solo auto con stato='disponibile'
# Verify: Info vehicle accessible tramite vehicle relationship
```

### Test 4.3: Loan CourtesyCar (Create CarAssignment)
**Endpoint:** `POST /api/v1/courtesy-cars/{id}/loan`

```bash
curl -X POST "http://localhost:8000/api/v1/courtesy-cars/1/loan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "work_order_id": 1,
    "loan_start_date": "2026-02-11T10:00:00Z",
    "expected_return_date": "2026-02-15T18:00:00Z",
    "km_at_loan": 50000,
    "notes": "Auto assegnata per sostituzione vetri"
  }'

# Expected Response: 200 OK
# Verify: Crea record CarAssignment
# Verify: CourtesyCar.stato = 'assegnata'
```

### Test 4.4: Return CourtesyCar (Complete CarAssignment)
**Endpoint:** `POST /api/v1/courtesy-cars/{id}/return`

```bash
curl -X POST "http://localhost:8000/api/v1/courtesy-cars/1/return" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "return_date": "2026-02-15T17:00:00Z",
    "km_at_return": 50180,
    "condition_notes": "Carrozzeria OK, no danni",
    "needs_maintenance": false
  }'

# Expected Response: 200 OK
# Verify: Completa CarAssignment (data_fine_effettiva, km_fine, stato='completata')
# Verify: CourtesyCar.stato = 'disponibile'
```

### Test 4.5: Get CourtesyCar Stats
**Endpoint:** `GET /api/v1/courtesy-cars/stats/summary`

```bash
curl -X GET "http://localhost:8000/api/v1/courtesy-cars/stats/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK
# Verify: Stats con stati corretti (disponibile, assegnata, manutenzione, fuori_servizio)
# Example response:
{
  "total_cars": 3,
  "available": 2,
  "assigned": 1,
  "in_maintenance": 0,
  "out_of_service": 0,
  "utilization_rate": 33.33,
  "by_status": {
    "disponibile": 2,
    "assegnata": 1
  }
}
```

---

## 🔧 Test MaintenanceSchedule Endpoint

### Test 5.1: Create MaintenanceSchedule
**Endpoint:** `POST /api/v1/maintenance-schedules`

```bash
curl -X POST "http://localhost:8000/api/v1/maintenance-schedules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "tipo": "ordinaria",
    "descrizione": "Cambio olio e filtro",
    "km_scadenza": 55000,
    "data_scadenza": "2026-06-11",
    "km_preavviso": 1000,
    "giorni_preavviso": 30,
    "stato": "attivo",
    "ricorrente": true,
    "intervallo_km": 10000,
    "intervallo_giorni": 365,
    "note": "Ogni 10000 km o 1 anno, usare olio Castrol Edge"
  }'

# Expected Response: 201 Created
# Verify: Enum tipo='ordinaria' (not 'oil_change' string), stato='attivo'
```

### Test 5.2: Update MaintenanceSchedule
**Endpoint:** `PUT /api/v1/maintenance-schedules/{id}`

```bash
curl -X PUT "http://localhost:8000/api/v1/maintenance-schedules/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "km_scadenza": 60000,
    "data_scadenza": "2026-07-15",
    "km_preavviso": 1500
  }'

# Expected Response: 200 OK
```

### Test 5.3: Get Due Maintenance
**Endpoint:** `GET /api/v1/maintenance-schedules?stato=attivo&vehicle_id=1`

```bash
curl -X GET "http://localhost:8000/api/v1/maintenance-schedules?stato=attivo&vehicle_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected Response: 200 OK
# Return schedules in stato='attivo'
```

---

## 🎨 Frontend Integration Tests

### Test 6.1: Types Compilation
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management/frontend
npm run build

# Expected: No TypeScript errors
# Verify: No "Property 'code' not found on Part" errors
# Verify: No "Property 'brand' not found on Tire" errors
# Verify: No "Property 'license_plate' not found on CourtesyCar" errors
```

### Test 6.2: Hook Imports
Verifica che i hooks importano correttamente i tipi aggiornati:

```bash
# In frontend/src/hooks/useParts.ts
grep -n "interface PartCreate" useParts.ts
# Expected: codice, nome, categoria, quantita, quantita_minima, prezzo_acquisto, prezzo_vendita

grep -n "interface TireCreate" useTires.ts
# Expected: tipo_stagione, marca, modello, misura, data_ultimo_cambio, stato

grep -n "interface CourtesyCarCreate" useCourtesyCars.ts
# Expected: vehicle_id, contratto_tipo, fornitore_contratto, canone_mensile, stato

grep -n "interface MaintenanceScheduleCreate" useMaintenanceSchedules.ts
# Expected: tipo, descrizione, km_scadenza, data_scadenza, intervallo_km, intervallo_giorni
```

### Test 6.3: Enum Filtering in UI
Verifica che i select/dropdown dei form display gli enum valori corretti:

```bash
# Verify in browser DevTools:
# Parts form -> tipo: ["ricambio", "fornitura"]
# Tires form -> tipo_stagione: ["estivo", "invernale"]
#            -> condition: ["new", "good", "fair", "poor", "worn_out"]
#            -> stato: ["depositati", "montati"]
# CourtesyCar form -> stato: ["disponibile", "assegnata", "manutenzione", "fuori_servizio"]
# MaintenanceSchedule form -> tipo: ["ordinaria", "straordinaria"]
#                          -> stato: ["attivo", "completato", "annullato"]
```

---

## ✅ Verification Checklist

### Backend
- [ ] WorkOrder enum conversion funziona senza errori
- [ ] Part schema accetta tutti i campi corretti
- [ ] Part API esclude campi inesistenti
- [ ] Tire schema con enumi italiano
- [ ] Tire API accetta tipo_stagione, marca, modello, misura
- [ ] CourtesyCar usa vehicle_id, non license_plate
- [ ] CourtesyCar loan/return usa CarAssignment
- [ ] CourtesyCar stats mostra stati corretti
- [ ] MaintenanceSchedule usa tipo enum, non string
- [ ] MaintenanceSchedule scadenza usa km_scadenza + data_scadenza
- [ ] MaintenanceSchedule preavviso funziona correttamente

### Frontend
- [ ] TypeScript compila senza errori
- [ ] Part interface ha: codice, nome, categoria, quantita, quantita_minima, prezzo_acquisto, prezzo_vendita
- [ ] Tire interface ha: tipo_stagione, marca, modello, misura, data_ultimo_cambio, stato
- [ ] CourtesyCar interface ha: vehicle_id, contratto_tipo, canone_mensile, stato (no license_plate, brand, model, year)
- [ ] MaintenanceSchedule interface ha: tipo, descrizione, km_scadenza, data_scadenza, intervallo_km
- [ ] useParts hook usa PartCreate con campi corretti
- [ ] useTires hook usa TireCreate con tipo_stagione enum
- [ ] useCourtesyCars hook usa vehicle_id
- [ ] useMaintenanceSchedules hook usa tipo enum

### Integration
- [ ] Frontend form carica e salva su backend senza validation errors
- [ ] API response viene correttamente mappata ai tipi TypeScript
- [ ] Enum values nel frontend matchano backend
- [ ] Database contiene dati corretti associati alle nuove/aggiornate strutture

---

## 🐛 Debug Tips

Se test falliscono:

1. **Backend errors**
   ```bash
   # Check FastAPI error responses
   curl -i -X POST http://localhost:8000/api/v1/parts \
     -H "Content-Type: application/json" \
     -d '{"codice": "TEST", "nome": "Test"}'
   # Look at error_detail message
   ```

2. **Field mapping errors**
   ```bash
   # Database query to check actual column names
   sqlite3 garage-db.sqlite3 "PRAGMA table_info(parts);"
   # Verify: nome, codice, categoria, quantita, quantita_minima exist
   ```

3. **Frontend enum issues**
   ```bash
   # Browser console
   console.log(TireSeason)  // Should show: { ESTIVO: 'estivo', INVERNALE: 'invernale' }
   console.log(CourtesyCarStatus)  // Should show correct Italian values
   ```

4. **Query parameter issues**
   ```bash
   # Check exact parameter names expected
   curl -X GET "http://localhost:8000/api/v1/courtesy-cars?stato_filter=disponibile" \
     -H "Authorization: Bearer TOKEN"
   # Should return cars con stato=disponibile
   ```

---

**Generated:** 11 Febbraio 2026  
**Status:** Ready for comprehensive testing
