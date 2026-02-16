# VERIFICA ERRORI FUNZIONE SCHEDALAVORI
## File: `backend/app/api/v1/endpoints/work_orders.py`

Data: 11/02/2026
Stato: ANALISI COMPLETATA

---

## 🔴 ERRORI CRITICI IDENTIFICATI

### ERRORE #1: Conversione Enum Status Non Gestita ⚠️ CRITICO
**Posizione:** Riga 59
**Funzione:** `read_work_orders()`

```python
# CODICE ATTUALE (ERRATO)
if status:
    query = query.filter(WorkOrder.stato == status)
```

**Problema:**
- Il parametro `status` arriva come **stringa** dal query parameter
- `WorkOrder.stato` è un **Enum SQLAlchemy** di tipo `WorkOrderStatus`
- SQLAlchemy non sa convertire automaticamente una stringa a enum
- Causa: `TypeError` o risultati vuoti a runtime

**Valori enum validi:**
- `"bozza"`
- `"approvata"`
- `"in_lavorazione"`
- `"completata"`
- `"annullata"`

**Soluzione richiesta:**
```python
# CORRETTO
if status:
    try:
        status_enum = WorkOrderStatus[status.upper()]
        # oppure
        status_enum = WorkOrderStatus(status.lower())
        query = query.filter(WorkOrder.stato == status_enum)
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stato non valido: {status}. Valori ammessi: bozza, approvata, in_lavorazione, completata, annullata"
        )
```

---

### ERRORE #2: Ambiguità Named Parameter - `status`
**Posizione:** Riga 33
**Funzione:** `read_work_orders()`

```python
status: Optional[str] = Query(None, description="Filtra per stato"),
```

**Problema:**
- La variabile si chiama `status` che ha significato speciale in FastAPI/HTTP
- Causa confusione con il parametro `status` di FastAPI stesso
- Potrebbe causare sorprese nella signature della funzione

**Consigliato:**
```python
stato: Optional[str] = Query(None, description="Filtra per stato"),
```

Poi nella logica:
```python
if stato:
    stato_enum = WorkOrderStatus(stato.lower())
    query = query.filter(WorkOrder.stato == stato_enum)
```

---

### ERRORE #3: Mancanza Type Hint per Response Model ⚠️ MODERATO
**Posizione:** Riga 28
**Funzione:** `read_work_orders()`

```python
@router.get("/")
def read_work_orders(...) -> Any:  # ❌ ERRATO: ritorna dict non Any
```

**Problema:**
- La funzione ritorna un dict personalizzato (non WorkOrderResponse)
- Il type hint `-> Any` è ambiguo e non aiuta il client
- FastAPI non valida lo schema della response

**Corretto:**
```python
from pydantic import BaseModel

class WorkOrderListResponse(BaseModel):
    items: List[WorkOrderResponse]
    total: int
    page: int
    size: int

@router.get("/", response_model=WorkOrderListResponse)
def read_work_orders(...) -> WorkOrderListResponse:
```

---

### ERRORE #4: Possibile Problema di Join Multipli ⚠️ MINORE
**Posizione:** Riga 47-55
**Funzione:** `read_work_orders()`

```python
if search:
    search_filter = f"%{search}%"
    query = query.join(Customer).join(Vehicle).filter(
        or_(...)
    )
```

**Potenziale Problema:**
- Se `search` è `None`, i join non vengono eseguiti
- Ma successivamente se si fanno ulteriori filtri su Customer/Vehicle, saranno mancanti
- Non è un errore diretto, ma potrebbe causare problemi di incoerenza

**Consiglio:**
```python
# Esegui sempre i join se potrebbero essere utili
if search or (qualche altra condizione su Customer/Vehicle):
    query = query.join(Customer).join(Vehicle)
```

---

### ERRORE #5: Campo di Database Confuso nella Query ⚠️ MINORE
**Posizione:** Riga 157
**Funzione:** `read_work_orders_stats()`

```python
total_revenue = db.query(func.sum(WorkOrder.costo_finale)).filter(
    WorkOrder.stato.in_([WorkOrderStatus.COMPLETATA]),
    ...
)
```

**Considerazione:**
- Il modello ha `costo_finale` (corretto)
- Ma in altre parti del progetto vedo riferimenti a `final_total`
- Verificare coerenza dei nomi

---

## 📋 RIEPILOGO ERRORI

| # | Tipo | Severità | Linea | Descrizione |
|---|------|----------|-------|-------------|
| 1 | Logic Error | 🔴 CRITICO | 59 | Enum conversion missing per status filter |
| 2 | Naming | 🟡 MODERATO | 33 | Parametro `status` ambiguo, usare `stato` |
| 3 | Type Hint | 🟡 MODERATO | 28 | Response schema non definito, usare `list[dict]` o custom model |
| 4 | Logic | 🟢 MINORE | 47-55 | Join condizionali potrebbero causare bug futuri |
| 5 | Consistency | 🟢 MINORE | 157 | Nome campo `costo_finale` vs `final_total` |

---

## 🔧 CORREZIONI NECESSARIE

### Fix Prioritario #1 (CRITICO)
**File:** `backend/app/api/v1/endpoints/work_orders.py`
**Linee:** 59
**Azione:** Aggiungere conversione enum per status

```python
# Filtro stato - CORRETTO
if stato:  # rinominato da status a stato
    try:
        stato_enum = WorkOrderStatus(stato.lower())
        query = query.filter(WorkOrder.stato == stato_enum)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stato '{stato}' non valido. Valori: bozza, approvata, in_lavorazione, completata, annullata"
        )
```

### Fix Prioritario #2 (MODERATO)
**File:** `backend/app/api/v1/endpoints/work_orders.py`
**Linee:** 28-85
**Azione:** Definire response model corretto

```python
from pydantic import BaseModel

class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
    page: int
    size: int

@router.get("/", response_model=WorkOrderListResponse)
def read_work_orders(...) -> WorkOrderListResponse:
    ...
```

---

## ✅ VERIFICA COMPLETATE

- [x] Lettura file work_orders.py
- [x] Analisi modello WorkOrder database
- [x] Verifica schema Pydantic
- [x] Controllo enum conversion
- [x] Review documentazione FIX

---

## 📌 CONCLUSIONI

La funzione `schedalavori` (read_work_orders) ha **almeno 1 errore critico**:
1. **Mancanza conversione enum per filtro status** - causa failure in produzione

E **2-3 problemi moderati** che andrebbero risolti:
- Type hint ambiguo per response
- Naming confusione su parametro status
- Possibili problemi di join condizionali in futuro

**Stato funzionale:** ⚠️ **DIFETTOSO** - la funzione fallisce quando si usa il filtro status
