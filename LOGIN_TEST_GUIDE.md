# Test di Login - Istruzioni

## Status Corrente
✅ Backend: Online su http://localhost:8000  
✅ Frontend: Online su http://localhost:3000  
✅ API Login: Funzionante - testato con curl  
✅ Database: Impostato con tabelle create  
✅ Utente di Test: admin@garage.local / Admin123  

## Cosa è stato corretto

### 1. Errori TypeScript nel Build
- ✅ Aggiunto proprietà `_isNew` e `_modified` all'interface `Intervention`
- ✅ Rimosso prop `required` da `InputNumber` e `Select` (Ant Design non supporta questa prop)
- ✅ Rimosso hook `useDamageTypes` non utilizzato dal WorkOrdersPage

### 2. Logging Aggiunto per Debug
Aggiunto logging dettagliato nei seguenti punti:

**LoginPage.tsx (onFinish):**
```
📝 Form submitted with values: {username, password}
✅ Login completed successfully
❌ Login failed: {error}
```

**AuthContext.tsx (login):**
```
🔐 Login attempt: {username}
✅ Login response: {access_token, user}
🚀 Navigating to /dashboard
❌ Login error: {error}
```

**axios.ts (Interceptors):**
```
🔐 Login request: {data}
✅ Login response: {data}
❌ API Error: {url, status, data}
```

## Test di Login Manuale

### Passo 1: Apri il browser
- Vai a http://localhost:3000
- Dovresti vedere la pagina di login con:
  - Titolo "Garage Management"
  - Input "Email"
  - Input "Password"
  - Button "Accedi"

### Passo 2: Apri la Console del Browser
- Premi `F12` o `Cmd+Option+I` (Mac)
- Vai al tab "Console"
- Dovresti vedere il logo della console

### Passo 3: Compila il Form
- Email: `admin@garage.local`
- Password: `Admin123`
- Clicca button "Accedi"

### Passo 4: Osserva i Log
Nella console del browser, dovresti vedere gli output di logging che mostrano:

1. **Se il form viene inviato:**
   ```
   📝 Form submitted with values: {username: "admin@garage.local", password: "Admin123"}
   ```

2. **Se la richiesta viene fatta al backend:**
   ```
   🔐 Login request: {username: "admin@garage.local", password: "Admin123"}
   ```

3. **Se la risposta viene ricevuta:**
   ```
   ✅ Login response: {access_token: "eyJ...", user: {...}}
   ```

4. **Se la navigazione avviene:**
   ```
   🚀 Navigating to /dashboard
   ✅ Login completed successfully
   ```

## Risoluzione Problemi

Se vedi uno di questi messaggi:

### ❌ "Form submitted..." non appare
**Problema:** Il form non sta facendo il submit
**Soluzione:** 
- Controlla se i campi Input sono vuoti
- Compila entrambi i campi (email e password)
- Clicca il button "Accedi"

### ❌ "❌ Login failed: Errore di connessione al server"
**Problema:** Non puoi raggiungere il backend
**Soluzione:**
- Verifica che il backend sia online: `curl http://localhost:8000/api/docs`
- Controlla che VITE_API_URL in .env sia: `http://localhost:8000/api/v1`

### ❌ "Email o password non corretti"
**Problema:** Le credenziali sono sbagliate
**Soluzione:**
- Usa esattamente: `admin@garage.local` e `Admin123`
- Verifica che non ci siano spazi

### ❌ Nessun log appare nella console
**Problema:** Il logging non è visibile
**Soluzione:**
- Controlla che la console sia aperta (`F12`)
- Controlla il tab "Console" (non "Network")
- Ricarica la pagina (`Cmd+R`)
- Prova di nuovo

## Test Alternativo (curl)

Se vuoi testare il login via API direttamente:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@garage.local","password":"Admin123"}'
```

Se vedi un JWT token nella risposta, il backend funziona correttamente.

## Prossimi Passi

Una volta confermato che il login funziona:

1. **Test Interventions Feature**
   - Crea una nuova scheda lavoro
   - Aggiungi interventi con descrizione, durata, tipo
   - Verifica che gli interventi vengono salvati

2. **Test Approval Blocking**
   - Prova ad approvare una scheda senza interventi
   - Dovrebbe mostrare un warning

3. **Test End-to-End**
   - Logout
   - Login di nuovo
   - Verifica che i dati persistono

## Comandi Utili

```bash
# Controllare se i server sono online
curl http://localhost:8000/api/docs  # Backend
curl http://localhost:3000            # Frontend

# Visualizzare i log del backend
tail -f /tmp/uvicorn.log

# Visualizzare i log del frontend
tail -f /tmp/vite.log
```

---

**Nota:** Tutti i log che ho aggiunto sono disponibili nella console del browser (F12). Controlla la console quando clicchi il button "Accedi" per vedere dove il flusso si interrompe.
