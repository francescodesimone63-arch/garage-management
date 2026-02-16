# 🔍 ANALISI PROBLEMA VEHICLES - 307 REDIRECT

## Data: 10/02/2026 - 16:41

---

## 🐛 SINTOMO

**Pagina Vehicles non funziona nel frontend**

---

## 📊 LOG TRACCIATO

```
16:38:50 | INFO | → GET /api/v1/vehicles     | Anonymous
16:38:50 | INFO | ← GET /api/v1/vehicles     | Status:307 | 2.97ms
16:38:50 | INFO | → GET /api/v1/vehicles/    | Anonymous
16:38:50 | INFO | ← GET /api/v1/vehicles/    | Status:200 | 6.44ms
```

**Analisi:**
1. Frontend chiama `/api/v1/vehicles` (senza slash finale)
2. Backend risponde con **307 Temporary Redirect** → `/api/v1/vehicles/`
3. Client segue il redirect automaticamente
4. Backend risponde **200 OK** con i dati

---

## 🔍 CAUSA

FastAPI di default fa redirect automatico quando:
- Router ha `prefix="/vehicles"`
- Endpoint è `@router.get("/")`
- Richiesta arriva **senza** slash finale → `/vehicles`
- FastAPI redirige a → `/vehicles/`

**Questo è comportamento NORMALE di FastAPI!**

---

## ⚠️ PROBLEMA POTENZIALE

Il **redirect 307** può causare problemi con:
1. **Axios nel frontend** - potrebbe perdere headers/body nel redirect
2. **CORS** - doppia richiesta può causare problemi CORS
3. **Performance** - doppia richiesta rallenta l'app
4. **Token Authorization** - potrebbe perdersi nel redirect

---

## 🔧 SOLUZIONI POSSIBILI

### **Soluzione 1: Disabilitare redirect in FastAPI** (CONSIGLIATO)
```python
# In main.py
app = FastAPI(
    redirect_slashes=False,  # ← Aggiungere questa opzione
    title=settings.app_name,
    ...
)
```

**Pro:** Elimina il problema alla radice  
**Contro:** Endpoint deve essere chiamato esattamente come definito

---

### **Soluzione 2: Frontend usa sempre slash finale**
```typescript
// In frontend/src/config/api.ts
export const API_ENDPOINTS = {
  VEHICLES: '/vehicles/',  // ← Aggiungere slash
  CUSTOMERS: '/customers/',
  ...
}
```

**Pro:** Soluzione semplice lato frontend  
**Contro:** Bisogna ricordarsi ovunque

---

### **Soluzione 3: Axios segue redirect automaticamente** (GIÀ ATTIVO)
Axios segue automaticamente i redirect 307, quindi dovrebbe funzionare.

**Se non funziona**, il problema è altro (CORS, token, parsing risposta).

---

## 🧪 TEST DA FARE

### 1. **Verifica risposta API diretta:**
```bash
curl -i 'http://localhost:8000/api/v1/vehicles/' \
  -H "Authorization: Bearer TOKEN"
```

Deve rispondere **200 OK** con JSON dei veicoli.

### 2. **Verifica con slash:**
```bash
curl -i 'http://localhost:8000/api/v1/vehicles' \
  -H "Authorization: Bearer TOKEN"
```

Deve rispondere **307 Redirect** poi seguire e dare **200 OK**.

### 3. **Verifica console browser:**
- Apri DevTools (F12)
- Tab Network
- Vai su http://localhost:3000/vehicles
- Verifica:
  - Request a `/api/v1/vehicles` → 307?
  - Request a `/api/v1/vehicles/` → 200?
  - Response ha dati JSON?
  - Errori console?

### 4. **Verifica CORS:**
```bash
curl -i 'http://localhost:8000/api/v1/vehicles' \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer TOKEN"
```

Deve avere header:
```
Access-Control-Allow-Origin: http://localhost:3000
```

---

## 💡 DIAGNOSI PROBABILE

Il **redirect 307 funziona** (vedi log: Status 200 dopo redirect).

**Il problema potrebbe essere:**

1. **Frontend non gestisce la risposta** - Verifica `VehiclesPage.tsx`
2. **Errore di parsing JSON** - Risposta non nel formato atteso
3. **Token scaduto/invalido** - Vedi "Anonymous" nei log (dovrebbe essere "User:1")
4. **Struttura dati diversa** - Frontend si aspetta campi diversi

---

## 🔍 VERIFICA TOKEN

**IMPORTANTE!** I log mostrano **"Anonymous"** per la richiesta vehicles:
```
16:38:50 | INFO | → GET /api/v1/vehicles | Anonymous  ← ⚠️ NON AUTENTICATO!
```

Dovrebbe mostrare `User:1` se il token fosse valido.

**QUESTO POTREBBE ESSERE IL VERO PROBLEMA!**

---

## ✅ AZIONE IMMEDIATA

### 1. **Verifica che il login funzioni:**
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@garage.local&password=admin123"
```

Salva il token dalla risposta.

### 2. **Usa il token per chiamare vehicles:**
```bash
curl 'http://localhost:8000/api/v1/vehicles/' \
  -H "Authorization: Bearer IL_TUO_TOKEN_QUI"
```

### 3. **Se funziona via curl ma non nel frontend:**
- Problema è nel frontend
- Verifica `VehiclesPage.tsx`
- Verifica axios headers
- Verifica localStorage token

---

## 📝 PROSSIMI STEP

1. [ ] Verificare token nel localStorage del browser
2. [ ] Verificare console browser per errori
3. [ ] Verificare Network tab per risposta API
4. [ ] Se risposta è OK ma non visualizza: problema è in `VehiclesPage.tsx`
5. [ ] Se risposta è errore: problema è autenticazione/backend

---

## 🎯 RISOLUZIONE RACCOMANDATA

**OPZIONE A:** Se è problema di autenticazione
→ Il frontend non sta inviando il token correttamente

**OPZIONE B:** Se è problema di redirect
→ Aggiungere `redirect_slashes=False` in `main.py`

**OPZIONE C:** Se è problema di parsing
→ Verificare che `VehiclesPage.tsx` gestisca correttamente la risposta

---

**Status**: 🔍 IN ANALISI  
**Priorità**: 🔴 ALTA  
**Prossimo step**: Verifica console browser e token
