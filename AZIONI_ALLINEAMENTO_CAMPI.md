# AZIONI IMMEDIATE NECESSARIE
## Verifica Allineamento Frontend-Backend
Data: 11/02/2026

---

## ✅ CORREZIONI APPLICATE

### 1. WorkOrder Status Query Parameter ✅ FIXED
**File modificato:** `frontend/src/hooks/useWorkOrders.ts` (Linea 38)

**Problema:** Frontend inviava `?status=bozza` ma backend aspettava `?stato=bozza`

**Soluzione:** Aggiornato query parameter da `status` a `stato`

```typescript
// PRIMA
if (status) {
  params.append('status', status)
}

// DOPO
if (status) {
  params.append('stato', status)  // ALLINEATO AL BACKEND
}
```

**Status:** ✅ **COMPLETATO**
**Testing:** Verificare che il filtro per stato funzioni correttamente

---

## 🟠 CORREZIONI IN PIANIFICAZIONE

### Priority 1 - Blockers (Deve essere fatto subito)

#### 1. Part (Ricambi) - Refactoring Schema Completo
**Severità:** 🔴 **CRITICO**
**Effort:** ~2 ore

**Discrepanze trovate:**
- Frontend invia: `code`, `name`, `description`, `category`, `supplier`, `unit_price`, `quantity`, `min_stock_level`, `location`
- Backend schema aspetta: `work_order_id`, `codice`, `descrizione`, `quantita`, `prezzo_unitario`, `sconto_percentuale`, `fornitore`, `numero_fattura_fornitore`
- Backend model ha: `codice`, `nome`, `descrizione`, `categoria`, `marca`, `modello`, `quantita`, `quantita_minima`, `prezzo_acquisto`, `prezzo_vendita`, `fornitore`, `posizione_magazzino`

**Azioni necessarie:**
```
1. [ ] Verificare endpoint `/parts/` nel backend (backend/app/api/v1/endpoints/parts.py)
2. [ ] Allinearre schema Pydantic con il modello database  
3. [ ] Correggere nomi campi per corrispondenza frontend-backend
4. [ ] Aggiornare frontend types se necessario
5. [ ] Testare CRUD completo per parts
```

**File da modificare:**
- `backend/app/schemas/part.py` (FULL REWRITE)
- `backend/app/api/v1/endpoints/parts.py` (VERIFICA)
- `frontend/src/hooks/useParts.ts` (POSSIBILE AGGIORNAMENTO)

---

#### 2. Tire (Pneumatici) - Rideign Architetturale
**Severità:** 🔴 **CRITICO**
**Effort:** ~4 ore

**Discrepanze trovate:**
- Frontend pensa a "set di pneumatici" con quantity
- Backend ha singoli Tire per cada posizione
- Nomi campi diversi in quasi tutti campi
- Enumerazioni diverse per stagione e tipo

**Azioni necessarie:**
```
1. [ ] Decidere: singoli Tire o Set di Tire?
2. [ ] Standardizzare enumerazioni (stagione: estiva/invernale/quattro stagioni)
3. [ ] Allineware nomenclatura campi (size -> misura, tread_depth -> profondita_battistrada)
4. [ ] Riscrivere schema Pydantic Tire
5. [ ] Aggiornare frontend types se necessario
6. [ ] Testare CRUD completo
```

**File da modificare:**
- `backend/app/models/tire.py` (REVIEW & REDESIGN)
- `backend/app/schemas/tire.py` (FULL REWRITE)
- `backend/app/api/v1/endpoints/tires.py` (VERIFICA)
- `frontend/src/types/index.ts` (POSSIBILE AGGIORNAMENTO)
- `frontend/src/hooks/useTires.ts` (POSSIBILE AGGIORNAMENTO)

---

### Priority 2 - Major Issues (Deve essere fatto presto)

#### 3. CourtesyCar (Auto Cortesia) - Wrapper API o Redesign
**Severità:** 🔴 **CRITICO**
**Effort:** ~3 ore

**Discrepanze trovate:**
- Frontend immagina: dati semplici diretti (brand, model, year, license_plate)
- Backend immagina: wrapper a Vehicle + sistema contrattuale (leasing/affitto/proprietà)

**Azioni necessarie:**
```
1. [ ] Decidere: aggiungere wrapper API o modificare frontend?
2. [ ] Se wrapper: creare endpoint che ritorna dati flattened
3. [ ] Se modifica frontend: aggiornare logica per caricare da Vehicle
4. [ ] Allineawre enumerazioni status
5. [ ] Testare assegnazione auto cortesia a work orders
```

**File da modificare:**
- `backend/app/models/courtesy_car.py` (REVIEW)
- `backend/app/schemas/courtesy_car.py` (POSSIBILE WRAPPER)
- `backend/app/api/v1/endpoints/courtesy_cars.py` (POSSIBILE WRAPPER)
- `frontend/src/types/index.ts` (POSSIBILE AGGIORNAMENTO)
- `frontend/src/hooks/useCourtesyCars.ts` (POSSIBILE AGGIORNAMENTO)

---

#### 4. MaintenanceSchedule (Manutenzioni) - Allineamento Nomenclatura
**Severità:** 🔴 **CRITICO**  
**Effort:** ~1.5 ore

**Discrepanze trovate:**
- Nomi campi diversi: `scheduled_date` vs `prossima_scadenza_data`
- Enumerazioni diverse: `oil_change` vs `ordinaria/straordinaria`
- Tipo ricorrenza: `recurrence_type` (enum) vs `ricorrente` (bool)

**Azioni necessarie:**
```
1. [ ] Allineawre nomi campi tra frontend e backend
2. [ ] Standardizzare enumerazioni MaintenanceType
3. [ ] Decidere tipo ricorrenza (enum vs bool)
4. [ ] Aggiornare schema e frontend types
5. [ ] Testare CRUD completo
```

**File da modificare:**
- `backend/app/schemas/maintenance_schedule.py` (NOMENCLATURA)
- `frontend/src/types/index.ts` (ENUMERAZIONI)
- `frontend/src/hooks/useMaintenanceSchedules.ts` (POSSIBILE AGGIORNAMENTO)

---

### Priority 3 - Code Quality (Deve essere fatto)

#### 5. Standardizzare Nomenclatura Italiana vs Inglese
**Severità:** 🟡 **MODERATO**
**Effort:** Variabile (refactoring ampio)

**Opzione A: Tutto Italiano**
```
- Backend model: ✅ Già italiano
- Backend schema: ✅ Già italiano  
- Frontend types: ❌ Cambiare da inglese a italiano
- Frontend pages/components: ❌ Aggiornare nomi
```

**Opzione B: Tutto Inglese**
```
- Backend model: ❌ Cambiare da italiano a inglese
- Backend schema: ❌ Cambiare da italiano a inglese
- Frontend: ✅ Già inglese
```

**Raccomandazione:** Mantenere Backend italiano (già implementato) e aggiornare Frontend a italiano per coerenza.

---

#### 6. Standardizzare Enumerazioni
**Severità:** 🟡 **MODERATO**
**Effort:** ~1 ora

**Enumerazioni da standardizzare:**

| Enum | Frontend | Backend |
|------|----------|---------|
| WorkOrderStatus | ✅ 'bozza' | ✅ 'bozza' | Allineato |
| TireType | 'summer', 'winter' | 'estivo', 'invernale' | Diverso |
| MaintenanceType | 'oil_change', 'brake_service' | 'ordinaria', 'straordinaria' | Diverso |
| CourtesyCarStatus | 'available', 'in_use' | 'disponibile', 'assegnata' | Diverso |

**Azioni:**
```
1. [ ] Creare enumerazioni standard
2. [ ] Aggiornare backend per usare enumerazioni standard
3. [ ] Aggiornare frontend per usare enumerazioni standard
4. [ ] Aggiungere mappatura per retrocompatibilità se necessario
```

---

## 📋 ORDINE DI PRIORITÀ CONSIGLIATO

1. **WorkOrder Status** ✅ DONE
2. **Part Schema** (Blocca creazione ricambi)
3. **Tire Redesign** (Blocca gestione pneumatici)
4. **CourtesyCar Wrapper** (Blocca assegnazione auto cortesia)
5. **MaintenanceSchedule** (Blocca manutenzioni programmate)
6. **Enumerazioni Standard** (Miglioramento generale)
7. **Nomenclatura Coerente** (Refactoring ampio)

---

## 🔍 TESTING CONSIGLIATO

Dopo ogni fix, eseguire test specifico:

### Test WorkOrder Status ✅
```bash
# Test filtro stato
curl -X GET "http://localhost:8000/api/v1/work-orders/?stato=bozza"

# Test con stato non valido
curl -X GET "http://localhost:8000/api/v1/work-orders/?stato=invalido"
# Deve ritornare 400 con messaggio chiaro
```

### Test Part CRUD
```bash
# Create
curl -X POST http://localhost:8000/api/v1/parts/ -H "Content-Type: application/json" -d '{...}'

# Read
curl -X GET http://localhost:8000/api/v1/parts/

# Update
curl -X PUT http://localhost:8000/api/v1/parts/1 -H "Content-Type: application/json" -d '{...}'

# Delete  
curl -X DELETE http://localhost:8000/api/v1/parts/1
```

---

## 📊 MAPPA DELLE ENTITÀ

```
Per capire dipendenze:

Customer (ALLINEATO ✅)
  ├── Vehicle (ALLINEATO ✅)
  │   ├── WorkOrder (PARZIALE ⚠️)
  │   │   └── Part (DISALLINEATO ❌)
  │   └── Tire (DISALLINEATO ❌)
  └── CourtesyCar (DISALLINEATO ❌)
      └── (Wrapped)Vehicle
          └── MaintenanceSchedule (DISALLINEATO ❌)

CalendarEvent (NON ANALIZZATO?)
  └── WorkOrder (PARZIALE ⚠️)

Notification (NON ANALIZZATO?)
```

---

## 💡 CONCLUSION

La verifica ha rivelato incoerenze strutturali significative tra frontend e backend che richiedono attenzione immediata. Le entità "core" (Customer, Vehicle) sono ben allineate, ma le entità "secondarie" (Part, Tire, CourtesyCar, MaintenanceSchedule) hanno discrepanze critiche.

**Stato complessivo:** ⚠️ **Applicazione funziona parzialmente, ma rischia data loss o comportamenti inaspettati**

**Prossimo passo:** Iniziare con il fix di WorkOrder Status (già fatto) e poi procedere con Part schema refactoring.

