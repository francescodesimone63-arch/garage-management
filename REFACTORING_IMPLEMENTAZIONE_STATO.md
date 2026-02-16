# REFACTORING ALLINEAMENTO FRONTEND-BACKEND
## Stato Implementazione: PARZIALE

Data: 11/02/2026 - Sessione 2

---

## ✅ CORREZIONI IMPLEMENTATE

### 1. WorkOrder Status Query Parameter ✅ FIXED
**File:** `frontend/src/hooks/useWorkOrders.ts`
**Stato:** ✅ COMPLETATO

```typescript
// PRIMA
params.append('status', status)

// DOPO
params.append('stato', status)
```

### 2. Backend Part Endpoint ✅ ALLINEATO (Parziale)
**File:** `backend/app/api/v1/endpoints/parts.py`
**Stato:** ✅ PARZIALMENTE CORRETTO

Corretti mappings attributi:
- ✅ `Part.name` → `Part.nome`
- ✅ `Part.description` → `Part.descrizione`
- ✅ `Part.manufacturer` → `Part.marca` (rimosso da search, brand non esiste)
- ✅ `Part.category` → `Part.categoria`
- ✅ `Part.supplier` → `Part.fornitore`
- ✅ `Part.quantity_in_stock` → `Part.quantita` (14 occorrenze)
- ✅ `Part.reorder_level` → `Part.quantita_minima` (6 occorrenze)
- ✅ `part.cost_price` → `part.prezzo_acquisto` (nel calcolo inventory value)

**Linee modifiate:** ~50 linee in 10 funzioni

**Test consigliato:**
```bash
curl -X GET "http://localhost:8000/api/v1/parts/?low_stock=true"
# Dovrebbe ritornare ricambi sotto minimo (quantita <= quantita_minima)

curl -X GET "http://localhost:8000/api/v1/parts/categories/list"
# Dovrebbe ritornare lista categorie
```

### 3. Backend Tire Endpoint ✅ PARZIALE
**File:** `backend/app/api/v1/endpoints/tires.py`
**Stato:** ✅ PARZIALMENTE CORRETTO

Corretti attributi vehicle:
- ✅ `vehicle.make` → `vehicle.marca`
- ✅ `vehicle.model` → `vehicle.modello`
- ✅ `vehicle.license_plate` → `vehicle.targa`

**Test consigliato:**
```bash
curl -X GET "http://localhost:8000/api/v1/tires/vehicle/1"
# Dovrebbe ritornare pneumatici con info veicolo allineata
```

---

## 🔴 PROBLEMI RIMANENTI CRITICI

### 1. Backend CourtesyCar Endpoint - ANCORA DISALLINEATO
**File:** `backend/app/api/v1/endpoints/courtesy_cars.py`
**Stato:** ❌ MOLTO DISALLINEATO

**Attributi che usano i nomi SBAGLIATI:**
- `CourtesyCar.status` → Dovrebbe essere `CourtesyCar.stato`
- `CourtesyCar.license_plate` → Dovrebbe essere `CourtesyCar.targa`
- `CourtesyCar.make` → Dovrebbe essere `CourtesyCar.marca` (o caricato da vehicle_id)
- `CourtesyCar.model` → Dovrebbe essere `CourtesyCar.modello` (o caricato da vehicle_id)
- `CourtesyCar.current_customer_id` → Modello non ha questo campo!
- `CourtesyCar.loan_start_date` → Modello non ha questo campo!
- `CourtesyCar.expected_return_date` → Modello non ha questo campo!
- `CourtesyCar.ON_LOAN`, `AVAILABLE` → Dovrebbe essere `DISPONIBILE`, `ASSEGNATA`, etc

**Linee problema:** Circa 20-30 linee

**Fix necessario:** Refactoring completo endpoint + allineamento con modello reale

### 2. Schema Part ⚠️ DISALLINEATO DAL MODELLO
**File:** `backend/app/schemas/part.py`
**Stato:** ❌ NON CORRISPONDE AL MODELLO

**Il problema:**
- Schema ha campi come `work_order_id`, `codice`, `descrizione`, `quantita`, `prezzo_unitario` (specifici per usarli in contesti).
- Modello ha `codice`, `nome`, `descrizione`, `categoria`, `marca`, `modello`, `quantita`, `quantita_minima`, `prezzo_acquisto`, `prezzo_vendita`, `fornitore`, `posizione_magazzino`, `tipo`, `unita_misura`
- Frontend invia `code`, `name`, `description`, `category`, `supplier`, `unit_price`, `quantity`

**Mancanza:** Lo schema è stato creato per un contesto diverso (probabilmente work_order_parts).

**Fix necessario:** Riscrivere schema Part per corrispondere al modello database + allineamento nomi frontend

### 3. Schema Tire ⚠️ PARZIALMENTE DISALLINEATO
**File:** `backend/app/schemas/tire.py`
**Stato:** ⚠️ PARZIALMENTE DISALLINEATO

**Nomi campi diversi:**
- `marca` vs `brand` (OK se inglese)
- `modello` vs `model` (OK se inglese)
- `dimensioni` vs `size` (Schema ha "dimensioni", modello ha "misura")
- `dot` vs `dot_code` (OK)
- `stagione` vs `season` (Schema pattern: "estive|invernali|quattro stagioni" - OK)
- `profondita_battistrada` vs `tread_depth` (Differente!)
- `data_montaggio` vs `installation_date` (OK)
- `data_smontaggio` vs `removal_date` (OK)

**Fix necessario:** Allineamento nomenclatura schema con modello

### 4. Schema CourtesyCar ⚠️ DISALLINEATO VIA NOMENCLATURA
**File:** `backend/app/schemas/courtesy_car.py`
**Stato:** ⚠️ DISALLINEATO

**Differenze:**
- Schema ha `targa` (corretta)
- Schema ha `stato` (corretto - Enum CourtesyCarStatus)
- Modello ha `vehicle_id` (relazione, non dati diretti)
- Schema assume dati diretti (marca, modello)

**Problema architetturale:** Il modello CourtesyCar è un wrapper di Vehicle, non entità indipendente come immagina lo schema Pydantic.

### 5. Schema MaintenanceSchedule ⚠️ NOMENCLATURA DISALLINEATA
**File:** `backend/app/schemas/maintenance_schedule.py`
**Stato:** ⚠️ PARZIALMENTE DISALLINEATO

**Differenze nome campi:**
- Schema: `tipo_manutenzione` vs Modello: `tipo` con Enum corretti
- Schema: `intervallo_km`, `intervallo_mesi` vs Modello: `intervallo_km`, `intervallo_giorni`
- Schema: `ultima_esecuzione_km`, `ultima_esecuzione_data` vs Modello: Non esiste!
- Schema: `prossima_scadenza_km`, `prossima_scadenza_data` vs Modello: `km_scadenza`, `data_scadenza`

---

## 🎯 PIANO D'AZIONE RIMANENTE

### Priority 1 - MUST FIX (Blocca funzionalità)

#### 1A. Correggere Schema Part
**Tempo:** ~1 ora
**Impact:** CRITICO - Creazione/modifica ricambi fallisce

```python
# PRIMA (ERRATO - contesto work_order)
class PartBase(BaseModel):
    work_order_id: int
    codice: str
    descrizione: str
    quantita: int
    prezzo_unitario: float  # NON ESISTE NEL MODELLO!
    sconto_percentuale: float
    fornitore: str
    numero_fattura_fornitore: str

# DOPO (CORRETTO - contesto inventory)
class PartBase(BaseModel):
    codice: str
    nome: str
    descrizione: Optional[str] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None
    modello: Optional[str] = None
    quantita: float = 0
    quantita_minima: float = 5
    prezzo_acquisto: Optional[float] = None
    prezzo_vendita: Optional[float] = None
    fornitore: Optional[str] = None
    posizione_magazzino: Optional[str] = None
    tipo: Enum(PartType) = PartType.RICAMBIO
    unita_misura: str = "pz"
    note: Optional[str] = None
```

**Azioni:**
- [ ] Riscrivere `backend/app/schemas/part.py` PartBase per corrispondere al modello
- [ ] Aggiornare PartCreate e PartUpdate
- [ ] Aggiornare frontend types in `frontend/src/types/index.ts`
- [ ] Aggiornare frontend hook `frontend/src/hooks/useParts.ts`

#### 1B. Correggere Endpoint CourtesyCar
**Tempo:** ~1.5 ore
**Impact:** CRITICO - Auto cortesia non funziona

**Azioni:**
- [ ] Mappare tutti gli attributi ai nomi corretti nel modello
- [ ] Rimappare `status` → `stato`
- [ ] Rimappare `license_plate` → `targa`
- [ ] **Decisione:** Caricare `marca`, `modello` da `vehicle_id` o tenerli diretti?
- [ ] Rimappare enumerazioni CourtesyCarStatus
- [ ] Testare CRUD endpoint

#### 1C. Correggere Schema Tire
**Tempo:** ~45 minuti
**Impact:** ALTO - Gestione pneumatici difettosa

**Azioni:**
- [ ] Allineware nomenclatura: `dimensioni` → `misura`, `profondita_battistrada` → profondità in mm
- [ ] Allineaware enumerazioni stagione
- [ ] Aggiornare schema + endpoint
- [ ] Testare creazione pneumatico

### Priority 2 - SHOULD FIX (Migliora qualità)

#### 2A. Riscrivere Schema MaintenanceSchedule
**Tempo:** ~1 ora
**Impact:** MEDIA - Manutenzioni programmate non completamente funzionali

**Azioni:**
- [ ] Allineaware nomi campi
- [ ] Standardizzare enumerazioni MaintenanceType
- [ ] Decidere tipo ricorrenza (enum vs bool)

#### 2B. Completare CourtesyCar Endpoint
**Tempo:** ~1 ora
**Impact:** MEDIA - Funzioni di prestito non implementate

**Azioni:**
- [ ] Implementare sistema prestiti (LoanHistory)
- [ ] Completare logica disponibilità nel periodo

### Priority 3 - NICE TO HAVE (Refactoring)

#### 3A. Standardizzare Nomenclatura
**Tempo:** Variabile (refactoring ampio)
**Impact:** BASSA - Coerenza interna

Scegliere: Tutto italiano o tutto inglese?
Raccomandazione: Mantenere backend italiano, aggiornare frontend a italiano

---

## 📋 RIEPILOGO STATO

| Componente | Stato | Severità |
|-----------|-------|----------|
| WorkOrder query param | ✅ FIXED | ✅ |
| Part endpoint | ✅ PARZIALE | 🔴 |
| Part schema | ❌ NON CORRETTO | 🔴 |
| Tire endpoint | ✅ PARZIALE | 🟡 |
| Tire schema | ⚠️ DISALLINEATO | 🟡 |
| CourtesyCar endpoint | ❌ MOLTO DISALLINEATO | 🔴 |
| CourtesyCar schema | ⚠️ DISALLINEATO | 🟡 |
| MaintenanceSchedule schema | ⚠️ DISALLINEATO | 🟡 |

---

## 🧪 TESTING IMMEDIATO CONSIGLIATO

```bash
# Test 1: Part lowstock
curl -X GET "http://localhost:8000/api/v1/parts/?low_stock=true" \
  -H "Authorization: Bearer TOKEN"
# Dovrebbe funzionare ✅

# Test 2: Part categories
curl -X GET "http://localhost:8000/api/v1/parts/categories/list" \
  -H "Authorization: Bearer TOKEN"
# Dovrebbe funzionare ✅

# Test 3: CourtesyCar available
curl -X GET "http://localhost:8000/api/v1/courtesy-cars/available" \
  -H "Authorization: Bearer TOKEN"
# Probabilmente fallisce ❌

# Test 4: Tire vehicle list
curl -X GET "http://localhost:8000/api/v1/tires/vehicle/1" \
  -H "Authorization: Bearer TOKEN"
# Dovrebbe funzionare con nomi corretti ✅
```

---

## 💡 Prossimo Passo

**Priorità Immediata:** Riscrivere schema Part perché è quello che causa errori silenti nella creazione ricambi.

**Suggerisco:** Continuare con il fix dello schema Part, poi CourtesyCar endpoint, poi completare i restanti schema.

