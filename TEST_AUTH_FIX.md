# 🔍 PROBLEMA AUTENTICAZIONE - ANALISI COMPLETA

## 🐛 PROBLEMA REALE

**L'endpoint `/vehicles` restituisce 401 Not authenticated**

```
16:46:26 | INFO  | → GET /api/v1/vehicles/ | Anonymous  ← ⚠️
16:46:26 | ERROR | ← GET /api/v1/vehicles/ | Status:401 | 1.55ms
```

**CAUSA**: Il token JWT NON viene inviato nelle richieste!

---

## 🔍 DIAGNOSI

### ✅ Backend funziona:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@garage.local&password=admin123"

# Risponde con token ✅
```

### ✅ Axios configurato correttamente:
- Interceptor aggiunge `Authorization: Bearer ${token}`
- Gestione errori 401 → redirect a login

### ❌ Token non presente o invalido:
- Le richieste sono tutte "Anonymous"
- Frontend non invia header Authorization

---

## 🎯 POSSIBILI CAUSE:

### 1. **Token non salvato nel localStorage**
- Login non salva il token correttamente
- Chiave localStorage errata

### 2. **Token scaduto**
- Token JWT scaduto (default 8 ore)
- Nessun refresh automatico

### 3. **CORS blocca header Authorization**
- Browser blocca header nei redirect
- Preflight OPTIONS non gestito

### 4. **Formato token errato**
- Token non in formato "Bearer XXX"
- Spazi o caratteri extra

---

## ✅ SOLUZIONE

### **STEP 1: Verifica token nel browser**

Apri DevTools (F12) → Console:
```javascript
localStorage.getItem('garage_access_token')
```

**Se NULL**: Il login non salva il token  
**Se esiste**: Verificare se è valido

---

### **STEP 2: Test manuale login**

1. Vai su http://localhost:3000/login
2. Login con: admin@garage.local / admin123
3. Apri DevTools → Application → LocalStorage
4. Verifica chiave `garage_access_token` presente
5. Copia il token

---

### **STEP 3: Test token manuale**

```bash
# Usa il token copiato dal browser
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl http://localhost:8000/api/v1/vehicles/ \
  -H "Authorization: Bearer $TOKEN"
```

**Se risponde con dati** → Token valido, problema nel frontend  
**Se 401** → Token invalido o scaduto

---

### **STEP 4: Fix AuthContext**

Il problema potrebbe essere nell'AuthContext che non salva il token correttamente.

Verificare in `AuthContext.tsx`:
```typescript
// DOPO IL LOGIN
localStorage.setItem(TOKEN_KEY, access_token)  // ✅ DEVE esserci
setUser(userData)
```

---

## 🔧 FIX IMMEDIATO

### **Opzione A: Rifare login**
1. Logout
2. Clear localStorage
3. Login di nuovo
4. Token dovrebbe essere salvato

### **Opzione B: Token manuale (temporaneo)**

Apri Console browser (F12):
```javascript
// Fai login e salva il token
fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=admin@garage.local&password=admin123'
})
.then(r => r.json())
.then(data => {
  localStorage.setItem('garage_access_token', data.access_token)
  console.log('Token salvato!', data.access_token)
  location.reload()
})
```

---

## 📊 VERIFICA FUNZIONAMENTO

Dopo il fix, i log dovrebbero mostrare:
```
→ GET /api/v1/vehicles/ | User:1  ← ✅ Autenticato!
← GET /api/v1/vehicles/ | Status:200 | 15.24ms
```

Invece di:
```
→ GET /api/v1/vehicles/ | Anonymous  ← ❌ Non autenticato
← GET /api/v1/vehicles/ | Status:401 | 1.55ms
```

---

## 🎯 AZIONI IMMEDIATE

1. [ ] Apri http://localhost:3000/login
2. [ ] Fai login con admin@garage.local / admin123
3. [ ] Apri DevTools (F12) → Application → LocalStorage
4. [ ] Verifica presenza chiave `garage_access_token`
5. [ ] Se presente → Ricarica pagina vehicles
6. [ ] Se assente → Usa fix manuale sopra

---

**Status**: 🔴 PROBLEMA AUTENTICAZIONE  
**Priorità**: 🔴 CRITICA  
**Fix**: Verificare login e localStorage token
