# 🎯 QUICK START - Sistema di Debug

## ✅ Cosa è stato installato

```
✅ Logger avanzato nel backend
✅ Debug Middleware per tracciare richieste/risposte
✅ Error Tracker nel frontend (React)
✅ Debug Dashboard (Ctrl+Shift+D)
✅ Script di validazione
✅ Documentazione completa
```

---

## 🚀 Come usare il sistema

### 1️⃣ Apri Debug Dashboard
```
Premi: Ctrl+Shift+D nel browser
```

### 2️⃣ Esegui l'azione che causa errore
```
Es: Crea un nuovo veicolo, aggiornaun cliente, etc.
```

### 3️⃣ Visualizza l'errore nella Dashboard
```
- Vedi il tipo di errore (API, Validazione, Network, ecc)
- Vedi la severità (Bassa, Media, Alta, Critica)
- Vedi il messaggio di errore
- Scarica il JSON per i dettagli completi
```

### 4️⃣ Controlla i logs del backend (se lo richiedi)
```bash
tail -f backend/logs/debug.log
```

---

## 📊 Cosa traccia il sistema

### **Frontend - Error Tracker**

| Errore | Origine | Come vederlo |
|--------|---------|-------------|
| 500 Server Error | API Response | Dashboard → API type → High/Critical severity |
| 422 Validation | API Response | Dashboard → API type → Status 422 |
| 401 Unauthorized | API Response | Dashboard → API type → Status 401 |
| CORS Blocked | Network | Dashboard → Network type → Critical |
| Runtime JS Error | Browser | Dashboard → Runtime type |
| Form Validation | Local | Dashboard → Validation type |

### **Backend - Debug Logger**

| Log | File | Visualizzazione |
|-----|------|-----------------|
| Richieste API | `logs/debug.log` | `tail -f backend/logs/debug.log` |
| Errori Database | `logs/debug.log` | `grep "DATABASE ERROR"` |
| Errori Validazione | `logs/debug.log` | `grep "VALIDATION ERROR"` |
| Errori generali | `logs/debug.log` | `grep "ERROR"` |

---

## 🔧 Comandi Utili

```bash
# Pulisci cache browser
Ctrl+Shift+R (oppure Cmd+Shift+R su Mac)

# Esegui validazione sistema
bash validate.sh

# Visualizza ultimi errori
tail -50 backend/logs/debug.log

# Segui errori in tempo reale
tail -f backend/logs/debug.log | grep "ERROR"

# Conta errori per tipo
grep -c "API ERROR" backend/logs/debug.log
grep -c "DATABASE ERROR" backend/logs/debug.log
grep -c "VALIDATION ERROR" backend/logs/debug.log

# Scarica logs JSON dalla Dashboard
Ctrl+Shift+D → Log List → "Scarica Logs"
```

---

## 🐛 Troubleshooting Workflow

### Quando trovi un errore, segui questo ordine:

**Step 1: Browser Console**
```
F12 → Console tab
Vedi i logs colorati dell'Error Tracker
```

**Step 2: Debug Dashboard**
```
Ctrl+Shift+D
Filtra per tipo/severità
Vedi il messaggio completo
```

**Step 3: Backend Logs (se necessario)**
```bash
tail -50 backend/logs/debug.log
Leggi lo stack trace completo
```

**Step 4: Identifica il problema**
```
Dai logs → Traccia il file e il numero di riga
Correggi il problema
```

**Step 5: Riavvia e testa**
```bash
bash STOP.sh && sleep 2 && bash START.sh
Pulisci cache browser: Ctrl+Shift+R
Testa di nuovo
```

---

## 📝 Esempi di Debugging

### Esempio 1: Vehicle creation fallisce con 422

**Dashboard Output:**
```
🔴 CRITICAL - API Error: POST /api/v1/vehicles/
Status: 422
Error: {
  "detail": [{
    "field": "targa",
    "msg": "Field required"
  }]
}
```

**Soluzione:**
1. Frontend: Aggiungi il campo `targa` al form
2. O Backend: Rendi il campo opzionale in `schemas/vehicle.py`

---

### Esempio 2: CORS Error dopo aver riavviato

**Browser Console:**
```
⚠️ MEDIUM - Network Error at /api/v1/customers/
Error: CORS policy: No 'Access-Control-Allow-Origin' header
```

**Soluzione:**
1. Non è un errore backend (CORS middleware è configurato)
2. **È cache browser!**
3. Pulisci: `Ctrl+Shift+Delete` → Cancella tutto → Hard Refresh `Ctrl+Shift+R`

---

### Esempio 3: 500 Internal Server Error

**Dashboard:**
```
🔴 CRITICAL - API Error: POST /api/v1/work-orders/
Status: 500
```

**Backend Logs:**
```bash
tail -f backend/logs/debug.log

# Output:
🔴 DATABASE ERROR | {
  "operation": "insert",
  "table": "work_orders",
  "exception": "Foreign key constraint failed",
  "traceback": "..."
}
```

**Soluzione:**
1. Leggi il messaggio di errore database
2. Nel code, traccia fino al file e la riga del problema
3. Correggi il constraint violato
4. Riavvia backend
5. Riprova

---

## 🎓 Best Practices

### ✅ DO

```typescript
// ✅ BENE: Traccia errori con contesto
const { trackAPIError } = useErrorTracking()
trackAPIError(endpoint, method, status, error, {
  userId: user.id,
  action: 'create_vehicle'
})

// ✅ BENE: Logga tutto nel backend
logger.error("Errore creazione veicolo", exception=e, vehicle_id=data.id)

// ✅ BENE: Pulisci cache quando cambi codice
bash START.sh && Ctrl+Shift+R
```

### ❌ DONT

```typescript
// ❌ MALE: Errore silenzioso
try {
  await api.post('/vehicles', data)
} catch (e) {
  // Silenzio totale!
}

// ❌ MALE: Log non informativo
console.log("error")

// ❌ MALE: Server non rispondde e non sai perché
// Senza logs = debugging cieco
```

---

## 📞 Domande Frequenti

**D: Dove trovo i logs?**
```
A: backend/logs/ → debug.log, vehicles.log, customers.log, etc.
```

**D: Come scarico tutti gli errori?**
```
A: Ctrl+Shift+D → Dashboard → "Scarica Logs" → JSON file
```

**D: Come leggo il JSON dell'errore?**
```
A: Ctrl+Shift+D → Clicca errore → Tab "Dettagli Log" → Vedi JSON completo
```

**D: Backend non loggga nulla**
```
A: Verifica main.py → ErrorHandlerMiddleware e DebugMiddleware aggiunti
B: Controlla che app/middleware/debug_middleware.py esista
C: Riavvia backend
```

**D: Debug Dashboard non appare?**
```
A: Premi Ctrl+Shift+D
B: O clicca pulsante 🐛 in basso a destra
C: Se non vedi il pulsante, pulisci cache (Ctrl+Shift+R)
```

---

## 🎯 Prossimi Step

1. **Apri il browser** su http://localhost:3000
2. **Premi Ctrl+Shift+D** per aprire Debug Dashboard
3. **Testa una funzionalità** (ad es. crea un cliente)
4. **Vedi l'errore nella Dashboard** se ce n'è uno
5. **Scarica i logs** se necessario per analisi profonda

---

**Sistema creato il:** 2026-02-20  
**Versione:** 1.0  
**Stato:** ✅ Utilizzabile e Testato

