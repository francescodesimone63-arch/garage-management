# VERIFICA ALLINEAMENTO CAMPI FRONTEND - BACKEND
## Progetto: garage-management
Data: 11/02/2026

---

## 📊 RIEPILOGO ESECUTIVO

**Stato Generale:** ⚠️ **CRITICO - Molte discrepanze trovate**

| Entità | Frontend | Backend | Match | Severità |
|--------|----------|---------|-------|----------|
| Customer | ✅ OK | ✅ OK | 100% | ✅ OK |
| Vehicle | ✅ OK | ✅ OK | 100% | ✅ OK |
| WorkOrder | ⚠️ PARZIALE | ⚠️ PARZIALE | ~80% | 🟡 MODERATO |
| Part | ❌ NO | ❌ NO | 10% | 🔴 CRITICO |
| Tire | ❌ NO | ❌ NO | 20% | 🔴 CRITICO |
| CourtesyCar | ❌ NO | ❌ NO | 15% | 🔴 CRITICO |
| MaintenanceSchedule | ⚠️ PARZIALE | ⚠️ PARZIALE | 40% | 🔴 CRITICO |
| CalendarEvent | ? | ⚠️ Database | ? | 🟡 MODERATO |

---

## ✅ ENTITÀ ALLINEATE

### 1. Customer (Clienti)
**Status:** ✅ **PERFETTAMENTE ALLINEATA**

**Frontend Types:**
```typescript
interface Customer {
  id: number
  tipo: string // 'privato' | 'azienda'
  nome?: string
  cognome?: string
  ragione_sociale?: string
  codice_fiscale: string  // Opzionale nel backend!
  partita_iva?: string
  indirizzo?: string
  citta?: string
  cap?: string
  provincia?: string
  telefono?: string
  cellulare?: string
  email?: string
  note?: string
}
```

**Backend Model + Schema:** ✅ IDENTICO

**Verificato in:**
- `backend/app/models/customer.py`
- `backend/app/schemas/customer.py`
- `frontend/src/types/index.ts`

**Nota:** Nel typescript dichiarato come `required` ma backend lo rende opzionale. OK così.

---

### 2. Vehicle (Veicoli)
**Status:** ✅ **PERFETTAMENTE ALLINEATA**

**Frontend Types:**
```typescript
interface Vehicle {
  id: number
  customer_id: number
  targa: string
  telaio?: string
  marca: string
  modello: string
  anno?: number
  colore?: string
  km_attuali?: number
  note?: string
}
```

**Backend Model:** ✅ IDENTICO

```python
class Vehicle(Base):
  targa: str
  telaio: str
  marca: str
  modello: str
  anno: int
  colore: str
  km_attuali: int
  note: str
```

---

## 🟡 ENTITÀ PARZIALMENTE ALLINEATE

### 3. WorkOrder (Schede Lavoro)
**Status:** ⚠️ **PARZIALMENTE ALLINEATA - NUOVA DISCREPANZA!**

**Discrepanza Critica Appena Introdotta:**

Nel frontend `useWorkOrders.ts` ancora usa:
```typescript
params.append('status', status)
```

Ma il backend endpoint (dopo la mia correzione) adesso usa:
```python
@router.get("/")
def read_work_orders(
    ...
    stato: Optional[str] = Query(None, ...)  # RINOMINATOda "status"
    ...
)
```

**Conseguenza:** Il filtro per stato NON FUNZIONA più! Il frontend manda `?status=bozza` ma il backend aspetta `?stato=bozza`.

**Discrepanza nell'Endpoint:**

Frontend manda:
```
GET /api/v1/work-orders/?status=bozza
```

Backend aspetta:
```
GET /api/v1/work-orders/?stato=bozza
```

**Campi Allineati:**
- `numero_scheda` ✅
- `data_appuntamento` ✅
- `data_fine_prevista` ✅
- `data_completamento` ✅
- `tipo_danno` ✅
- `priorita` ✅
- `valutazione_danno` ✅
- `note` ✅
- `estado` ⚠️ (frontend enum, backend enum) - Nomi enum corretti
- `creato_da` ✅
- `approvato_da` ✅
- `auto_cortesia_id` ✅
- `costo_stimato` ✅
- `costo_finale` ✅

**Campi Mancanti nel Frontend:**
- `vehicle` (relationship - OK, caricato dinamicamente)
- `customer` (relationship - OK, caricato dinamicamente)

**Fix Necessario:** Aggiornare frontend per usare `stato` al posto di `status`:

```typescript
// Frontend: useWorkOrders.ts (linea ~38)
if (status) {
  params.append('stato', status)  // CAMBIARE da 'status' a 'stato'
}
```

---

## 🔴 ENTITÀ NON ALLINEATE

### 4. Part (Ricambi)
**Status:** ❌ **COMPLETAMENTE DISALLINEATA**

**GRAVE PROBLEMA:** I nomi dei campi sono completamente diversi tra frontend, modello backend e schema backend!

#### Frontend Types:
```typescript
interface Part {
  id: number
  code: string              // ← Frontend
  name: string              // ← Frontend
  description?: string      // ← Frontend
  category?: string         // ← Frontend
  supplier?: string         // ← Frontend
  quantity_in_stock: number // ← Frontend
  minimum_quantity: number  // ← Frontend
  unit_price: number        // ← Frontend
  location?: string         // ← Frontend
  notes?: string
}

interface PartCreate {
  code: string
  name: string
  description?: string
  category: string
  supplier?: string
  unit_price: number
  quantity: number
  min_stock_level?: number
  location?: string
  notes?: string
}
```

#### Backend Model:
```python
class Part(Base):
  codice: str                    # ← Backend Model
  nome: str                      # ← Backend Model
  descrizione: str               # ← Backend Model
  categoria: str                 # ← Backend Model
  marca: str                     # ← Backend Model (EXTRA!)
  modello: str                   # ← Backend Model (EXTRA!)
  quantita: DECIMAL              # ← Backend Model
  quantita_minima: DECIMAL       # ← Backend Model
  prezzo_acquisto: DECIMAL       # ← Backend Model
  prezzo_vendita: DECIMAL        # ← Backend Model (EXTRA!)
  fornitore: str                 # ← Backend Model
  posizione_magazzino: str       # ← Backend Model
  tipo: Enum(PartType)           # ← Backend Model (EXTRA!)
  unita_misura: str              # ← Backend Model (EXTRA!)
```

#### Backend Schema (COMPLETAMENTE DIVERSO!):
```python
class PartBase(BaseModel):
  work_order_id: int             # ← Questo NON dovrebbe essere qui!
  codice: str
  descrizione: str
  quantita: int
  prezzo_unitario: float         # ← Diverso da backend model!
  sconto_percentuale: float
  fornitore: str
  numero_fattura_fornitore: str
```

**ANALISI CRITICA:**
```
Frontend       Backend Model    Backend Schema
─────────────────────────────────────────────
code       →   codice       →   codice ✅ (ma non nel PartCreate frontend!)
name       →   nome         →   ❌ MANCANTE!
description→   descrizione  →   descrizione ✅
category   →   categoria    →   ❌ MANCANTE!
supplier   →   fornitore    →   fornitore ✅
unit_price →   prezzo_XX    →   prezzo_unitario ⚠️
quantity   →   quantita     →   quantita ✅ (ma non in frontend!)
min_qty    →   quantita_min →   ❌ MANCANTE!
location   →   pos_magazzino→   ❌ MANCANTE!
```

**Problema Tecnico:**
1. Il frontend invia `code`, `name`, `category` → Backend schema non ha questi campi!
2. Backend schema ha `work_order_id` che non dovrebbe avere (Part è indipendente)
3. Il modello database ha diversi campi dal schema Pydantic

**Fix Necessario:** ❌ **REFACTORING COMPLETO SCHEMA PART**

---

### 5. Tire (Pneumatici)
**Status:** ❌ **COMPLETAMENTE DISALLINEATA**

#### Frontend Types:
```typescript
interface Tire {
  id: number
  vehicle_id: number
  brand: string              // ← Frontend
  model: string              // ← Frontend
  size: string               // ← Frontend
  type: TireType
  position: TirePosition
  dot_code?: string
  tread_depth?: number
  purchase_date?: string
  installation_date?: string
  installation_km?: number
  notes?: string
  is_stored: boolean
  is_active: boolean
}

interface TireCreate {
  vehicle_id: number
  brand: string
  model: string
  size: string
  dot_code?: string
  quantity: number
  position?: string
  installation_date?: string
  removal_date?: string
  storage_location?: string
  price?: number
  notes?: string
}
```

#### Backend Model:
```python
class Tire(Base):
  vehicle_id: int
  tipo_stagione: Enum           # ← Backend
  marca: str                    # ← Match con "brand"? NO!
  modello: str                  # ← Match con "model"? NO!
  misura: str                   # ← Match con "size" ✓
  data_deposito: DateTime       # ← Non inFrontend!
  data_ultimo_cambio: DateTime  # ← Non in Frontend!
  data_prossimo_cambio: DateTime# ← Non in Frontend!
  stato: Enum(TireStatus)       # ← Non in Frontend!
  posizione_deposito: str       # ← Non in Frontend!
  note: str
  position: Enum               # ← Duplicato col posizione_deposito?
  condition: Enum              # ← Non in Frontend!
  tread_depth: int             # ← Match!
  manufacture_date: DateTime   # ← Non in Frontend!
  last_rotation_date: DateTime # ← Non in Frontend!
  last_rotation_km: int        # ← Non in Frontend!
```

#### Backend Schema:
```python
class TireBase(BaseModel):
  vehicle_id: int
  marca: str                    # ← Nomenclatura italiana
  modello: str
  dimensioni: str               # ← "dimensioni" non "size"!
  dot: str                      # ← "dot" non "dot_code"
  stagione: str                 # ← Pattern: "estive|invernali|quattro stagioni"
  stato: TireStatus
  km_percorsi: int
  profondita_battistrada: float # ← "profondita" non "tread_depth"
  posizione_attuale: str
  data_acquisto: date
  data_montaggio: date
  data_smontaggio: date
  prezzo_acquisto: float
  note: str
```

**Mappatura Confusa:**
```
Frontend          Backend Model     Backend Schema
──────────────────────────────────────────────────
brand         →   marca        →   marca ✗(non "brand"!)
model         →   modello      →   modello ✗(non "model"!)
size          →   misura       →   dimensioni ✗(nome diverso!)
dot_code      →   ❌ NIENTE   →   dot ✗(campo diverso!)
position      →   position OR  →   ❌ MANCANTE!
              →   posizione_deposito
tread_depth   →   tread_depth  →   profondita_battistrada ✗
install_date  →   ❌ NIENTE   →   data_montaggio ✓
removal_date  →   ❌ NIENTE   →   data_smontaggio ✓
is_stored     →   ❌ NIENTE   →   stato: TireStatus
is_active     →   ❌ NIENTE   →   ❌ MANCANTE!
quantity      →   ❌ NIENTE   →   ❌ MANCANTE! (Tire è singolo!)
```

**Problema Architetturale:**
- Il frontend crea interi "Set di Pneumatici" con `quantity`
- Il backend crea singoli Tire per posizione
- Paradigma completamente diverso!

**Fix Necessario:** ❌ **REFACTORING ARCHITETTURALE COMPLETO**

---

### 6. CourtesyCar (Auto Cortesia)
**Status:** ❌ **COMPLETAMENTE DISALLINEATA**

#### Frontend Types:
```typescript
interface CourtesyCar {
  id: number
  license_plate: string           // ← Frontend
  brand: string
  model: string
  year?: number
  status: CourtesyCarStatus       // 'available' | 'in_use' | 'maintenance'
  current_customer_id?: number
  current_work_order_id?: number
  loan_start_date?: string
  expected_return_date?: string
  current_km?: number
  notes?: string
}
```

#### Backend Model:
```python
class CourtesyCar(Base):
  vehicle_id: int                # ← FK a Vehicle, non info diretta!
  contratto_tipo: Enum           # ← 'leasing' | 'affitto' | 'proprieta'
  fornitore_contratto: str       # ← Non in Frontend!
  data_inizio_contratto: Date    # ← Non in Frontend!
  data_scadenza_contratto: Date  # ← Non in Frontend!
  canone_mensile: DECIMAL        # ← Non in Frontend!
  km_inclusi_anno: int           # ← Non in Frontend!
  stato: Enum                    # ←'disponibile'|'assegnata'|'manutenzione'
  note: str
```

**Backend Schema:**
```python
class CourtesyCarBase(BaseModel):
  targa: str                     # ← Nomenclatura italiana!
  marca: str
  modello: str
  anno: int
  stato: CourtesyCarStatus
  km_attuali: int
  data_ultima_revisione: date
  data_prossima_revisione: date
  assicurazione_numero: str      # ← Non in Frontend!
  assicurazione_scadenza: date   # ← Non in Frontend!
  note: str
```

**CONFRONTO CRITICO:**

Frontend immagina CourtesyCar come:
- Entità indipendente con dati diretti (brand, model, year)
- Sistema di assignazione semplice (current_customer, current_work_order)
- Tracciamento prestito semplice (loan_dates, km)

Backend immagina CourtesyCar come:
- Wrapper intorno a Vehicle (vehicle_id non dati diretti)
- Sistema di contratto complesso (leasing/affitto/proprietà)
- Sistema di revisioni (ultima/prossima revisione)
- Sistema di assicurazione

**Sono due concezioni completamente diverse!**

**Fix Necessario:** ❌ **RIDEIGN ARCHITETTURALE O WRAPPER API**

---

### 7. MaintenanceSchedule (Manutenzioni Programmate)
**Status:** ⚠️ **PARZIALMENTE ALLINEATA - NOMENCLATURA DIVERSA**

#### Frontend Types:
```typescript
interface MaintenanceSchedule {
  id: number
  vehicle_id: number
  maintenance_type: MaintenanceType    // 'oil_change' | 'brake_service' | etc
  scheduled_date: string
  description?: string
  km_threshold?: number
  recurrence_type?: RecurrenceType
  recurrence_interval?: number
  last_performed_date?: string
  next_due_date?: string
  is_active: boolean
  notes?: string
}
```

#### Backend Model:
```python
class MaintenanceSchedule(Base):
  vehicle_id: int
  tipo: Enum(MaintenanceType)         # ← 'ordinaria' | 'straordinaria'
  descrizione: str
  km_scadenza: int
  data_scadenza: date
  km_preavviso: int
  giorni_preavviso: int
  stato: Enum                         # ← 'attivo' | 'completato' | 'annullato'
  ricorrente: bool
  intervallo_km: int
  intervallo_giorni: int
  ultima_notifica: datetime
```

#### Backend Schema:
```python
class MaintenanceScheduleBase(BaseModel):
  vehicle_id: int
  tipo_manutenzione: str              # ← Nomenclatura diversa!
  descrizione: str
  intervallo_km: int
  intervallo_mesi: int                # ← Non in Frontend!
  ultima_esecuzione_km: int
  ultima_esecuzione_data: date
  prossima_scadenza_km: int
  prossima_scadenza_data: date
  costo_previsto: float
  note: str
```

**Mappatura:**
```
Frontend              Backend Model    Backend Schema
──────────────────────────────────────────────────
maintenance_type  →  tipo         →  tipo_manutenzione (nome diverso!)
scheduled_date    →  data_scadenza→  prossima_scadenza_data (semantica diversa!)
km_threshold      →  km_scadenza  →  prossima_scadenza_km ✓
description       →  descrizione  →  descrizione ✓
recurrence_type   →  ❌           →  ricorrente (bool vs enum!)
recurrence_int    →  intervallo_km→  intervallo_km/mesi (duplicato!)
last_performed    →  ❌           →  ultima_esecuzione_data ✓
next_due_date     →  data_scadenza→  prossima_scadenza_data ⚠️
is_active         →  stato        →  ❌ (enum vs bool!)
```

**Problemi:**
1. Frontend enum `MaintenanceType` ha valori come `'oil_change'` ma backend ha `'ordinaria'`
2. Frontend `recurrence_type` è enum, backend `ricorrente` è bool
3. Nomi dei campi spesso diversi

**Fix Necessario:** ⚠️ **ALLINEAMENTO ENUMERAZIONI E NOMENCLATURA**

---

### 8. CalendarEvent (Eventi Calendario)
**Status:** ? **NON COMPLETAMENTE ANALIZZATO**

Backend Model ha:
```python
class CalendarEvent(Base):
  work_order_id: int
  google_event_id: str
  titolo: str
  descrizione: str
  data_inizio: datetime
  data_fine: datetime
  partecipanti: str  # JSON
  sincronizzato: bool
```

Frontend non ha hook specifico per CalendarEvent, sembra gestito tramite WorkOrder.

---

## 🔍 PROBLEMI ARCHITETTURALI IDENTIFICATI

### Problema #1: Nomenclatura Mista (Italiano/Inglese)
- Backend model: italiano (`numero_scheda`, `tipo_danno`, `marca`, `modello`)
- Backend schema: italiano (`numero_scheda`, `tipo_manutenzione`, `targa`)
- Frontend: inglese (`brand`, `model`, `license_plate`, `dot_code`)

**Conseguenza:** Mapping manuale necessario
**Severità:** 🟡 MODERATO

### Problema #2: Enumerazioni Diverse
Frontend:
- `WorkOrderStatus`: `'bozza'` (anche italiano)
- `TireType`: `'summer'`, `'winter'`, `'all_season'` (inglese)
- `MaintenanceType`: `'oil_change'`, `'brake_service'` (inglese)

Backend Model:
- `TireStatus`: `'estivo'`, `'invernale'` (italiano)
- `MaintenanceType`: `'ordinaria'`, `'straordinaria'` (italiano)
- `CourtesyCarStatus`: `'disponibile'`, `'assegnata'` (italiano)

**Conseguenza:** Conversione enum necessaria in molti punti
**Severità:** 🔴 CRITICO

### Problema #3: Entità Diverse tra Frontend e Backend
- **Tire:** Frontend pensa a "set di pneumatici", Backend a singoli pneumatici
- **CourtesyCar:** Frontend pensa a dati semplici, Backend a sistema contrattuale complesso
- **Part:** Frontend e Backend schema hanno modelli dati completamente diversi

**Severità:** 🔴 CRITICO

### Problema #4: Parametri Query Diversi
- Frontend manda `?status=bozza`
- Backend aspetta `?stato=bozza` (dopo la mia correzione)

**Severità:** 🔴 CRITICO (causa failure immediata)

---

## 📋 TABELLA RIEPILOGATIVA DISCREPANZE

| # | Campo | Frontend | Backend | Allineato | Severità |
|---|-------|----------|---------|-----------|----------|
| **CUSTOMER** |||||
| 1 | tipo | type | tipo | ✅ | | |
| 2 | nome | nome | nome | ✅ | |
| **VEHICLE** |||||
| 1 | marca | marca | marca | ✅ | |
| 2 | modello | modello | modello | ✅ | |
| **WORKORDER** |||||
| 1 | numero_scheda | numero_scheda | numero_scheda | ✅ | |
| 2 | status (QUERY) | status | stato | ❌ | 🔴 CRITICO |
| 3 | stato (FIELD) | stato | stato | ✅ | |
| **PART** |||||
| 1 | code | codice | codice | ⚠️ | 🔴 CRITICO |
| 2 | name | nome | descrizione | ❌ | 🔴 CRITICO |
| 3 | category | categoria | ❌ MANCANTE | ❌ | 🔴 CRITICO |
| 4 | unit_price | prezzo_acquisto | prezzo_unitario | ❌ | 🔴 CRITICO |
| 5 | quantity | quantita | quantita | ✅ | |
| 6 | min_stock_level | quantita_minima | ❌ MANCANTE | ❌ | 🔴 CRITICO |
| 7 | location | posizione_magazzino | ❌ MANCANTE | ❌ | 🔴 CRITICO |
| **TIRE** |||||
| 1 | brand | marca | marca | ⚠️ | 🔴 CRITICO |
| 2 | model | modello | modello | ⚠️ | 🔴 CRITICO |
| 3 | size | misura | dimensioni | ❌ | 🔴 CRITICO |
| 4 | dot_code | ❌ NIENTE | dot | ❌ | 🔴 CRITICO |
| 5 | position | position | posizione_attuale | ⚠️ | 🔴 CRITICO |
| 6 | tread_depth | tread_depth | profondita_battistrada | ❌ | 🔴 CRITICO |
| **COURTESYCAR** |||||
| 1 | license_plate | targa (indirect) | targa | ⚠️ | 🔴 CRITICO |
| 2 | status | stato | stato | ⚠️ (enum) | 🔴 CRITICO |
| **MAINTENANCESCHEDULE** |||||
| 1 | maintenance_type | tipo_manutenzione | tipo_manutenzione | ⚠️ (enum) | 🔴 CRITICO |
| 2 | scheduled_date | data_scadenza | prossima_scadenza_data | ⚠️ | 🟡 MODERATO |
| 3 | recurrence_type | ricorrente | ricorrente | ❌ (type) | 🔴 CRITICO |

---

## 🚨 AZIONI NECESSARIE

### Priority 1 - BLOCKERS (Causano failure immediato)

- [ ] **WorkOrder Status Query Parameter**
  - File: `frontend/src/hooks/useWorkOrders.ts`
  - Linea: ~38
  - Azione: Cambiare `params.append('status', status)` → `params.append('stato', status)`
  - Impact: ALTA - Il filtro non funziona
  - Tempo: 2 minuti

- [ ] **Part Schema Completo Refactoring**
  - File: `backend/app/schemas/part.py`
  - Problema: Schema completo completamente diverso dal modello
  - Azione: Riallineare schema con modello e tipi frontend
  - Impact: ALTA - Creazione/modifica parti fallisce silenziosamente
  - Tempo: 2 ore

- [ ] **Tire Conceptual Redesign**
  - File: Multipli (frontend types, backend model, schema)
  - Problema: Paradigma intrinsecamente diverso
  - Azione: Decidere se singoli pneumatici o set, riallineare
  - Impact: ALTA - Gestione pneumatici non funziona
  - Tempo: 4 ore

### Priority 2 - Major Issues

- [ ] **CourtesyCar Wrapper API**
  - Problema: Modello dati completamente diverso
  - Azione: Creareesamente wrapper API o rideign modello
  - Impact: ALTA - Auto cortesia non funziona correttamente
  - Tempo: 3 ore

- [ ] **Enumerazioni Allineate**
  - Problema: Valori enum diversi tra frontend e backend
  - Azione: Unificare set di valori enum
  - Impact: MEDIA - Conversioni manuali necessarie
  - Tempo: 2 ore

- [ ] **MaintenanceSchedule Nomenclatura**
  - File: Backend schema e frontend types
  - Problema: Nomi campi e tipi diversi
  - Azione: Allineamento nomenclatura e tipi enum
  - Impact: MEDIA - Creazione/lettura ricerche non allineata
  - Tempo: 1.5 ore

### Priority 3 - Minor Issues

- [ ] **Nomenclatura Italiana/Inglese Coerente**
  - Azione: Scegliere standard (o italiano o inglese) e applicare ovunque
  - Impact: BASSA - Confusione durante sviluppo
  - Tempo: Variabile (refactoring ampio)

---

## 📝 CONCLUSIONI

- **Entità ben allineate:** Customer, Vehicle (2 su 8)
- **Entità parzialmente allineate:** WorkOrder, MaintenanceSchedule (2 su 8)
- **Entità NON allineate:** Part, Tire, CourtesyCar (3 su 8)
- **Entità non analizzate:** CalendarEvent, User, Notification (1 su 8)

**Stato complessivo:** ⚠️ **PROBLEMA SERIO - Il progetto ha incoerenze strutturali importanti che potrebbero causare data loss o comportamenti inaspettati**

Le priorità principali sono:
1. Correggere il query parameter status/stato per Work Orders (IMMEDIATO)
2. Riallineare Part, Tire, CourtesyCar (URGENTE)
3. Standardizzare nomenclatura e enumerazioni  (IMPORTANTE)

