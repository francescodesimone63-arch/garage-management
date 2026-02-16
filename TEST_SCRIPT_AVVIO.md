# ✅ Test e Verifica Script START.sh / STOP.sh

**Data:** 11 Febbraio 2026  
**Status:** ✅ SCRIPT CORRETTI E TESTATI

---

## 📋 Correzioni Applicate

### START.sh
1. ✅ **Porta corretta**: Cambiata da 5173 → **3000** (frontend)
2. ✅ **Backend path**: Cambiato da `uvicorn main:app` → `uvicorn app.main:app`
3. ✅ **URL output**: Aggiornato da http://localhost:5173 → **http://localhost:3000**
4. ✅ **Verifica porte**: Check sulla porta 3000 (frontend) invece di 5173

### STOP.sh
1. ✅ **Porta killata**: Cambiata da 5173 → **3000** (frontend)

---

## 🚀 Come Usare

### Avviare il Sistema
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management
./START.sh
```

**Output atteso:**
```
🚀 Avvio Garage Management System...

📡 Verifica porte disponibili...

🔧 Avvio Backend (FastAPI)...
Backend avviato con PID: XXXXX
✅ Backend disponibile su: http://localhost:8000
✅ API Docs disponibile su: http://localhost:8000/docs
⏳ Attendi avvio backend...

🎨 Avvio Frontend (React + Vite)...
Frontend avviato con PID: XXXXX
✅ Frontend disponibile su: http://localhost:3000

================================
🎉 Sistema avviato con successo!
================================

📱 Apri il browser su: http://localhost:3000
📚 API Documentation: http://localhost:8000/docs

Credenziali di accesso di default:
  Email: admin@garage.local
  Password: admin123

Per fermare il sistema, esegui: ./STOP.sh
```

**Note:**
- Lo script verrà eseguito in background
- I servizi continueranno a girare dopo che lo script termina
- Puoi usare il browser mentre lo script è in esecuzione

---

### Fermare il Sistema
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management
./STOP.sh
```

**Output atteso:**
```
🛑 Arresto Garage Management System...
🔴 Arresto Backend (PID: XXXXX)...
🔴 Arresto Frontend (PID: XXXXX)...
🧹 Pulizia porte...
✅ Sistema arrestato
```

---

## 🧪 Test Eseguiti

### ✅ Test 1: STOP.sh
```bash
$ ./STOP.sh
🛑 Arresto Garage Management System...
Backend non in esecuzione
Frontend non in esecuzione
🧹 Pulizia porte...
✅ Sistema arrestato
```
**Risultato:** ✅ PASS

### ✅ Test 2: START.sh
```bash
$ ./START.sh
🚀 Avvio Garage Management System...
📡 Verifica porte disponibili...
🔧 Avvio Backend (FastAPI)...
Backend avviato con PID: 52746
✅ Backend disponibile su: http://localhost:8000
✅ API Docs disponibile su: http://localhost:8000/docs
⏳ Attendi avvio backend...
🎨 Avvio Frontend (React + Vite)...
Frontend avviato con PID: 52776
✅ Frontend disponibile su: http://localhost:3000

================================
🎉 Sistema avviato con successo!
================================
```
**Risultato:** ✅ PASS

---

## 📊 Servizi Avviati

| Servizio | Porta | Status | URL |
|----------|-------|--------|-----|
| Backend | 8000 | ✅ Online | http://localhost:8000 |
| Backend Docs | 8000/docs | ✅ Online | http://localhost:8000/docs |
| Frontend | 3000 | ✅ Online | http://localhost:3000 |

---

## 📝 File di Log

**Durante l'esecuzione dei servizi:**
- Backend log: `backend/backend.log`
- Frontend log: `frontend/frontend.log`

**Puoi monitorare i servizi:**
```bash
# Backend
tail -f backend/backend.log

# Frontend
tail -f frontend/frontend.log
```

---

## 🆘 Troubleshooting

### Se una porta è già in uso:
Lo script chiede conferma per continuare. Scegli `s` per continuare o `n` per uscire.

### Se il backend non parte:
1. Verifica che il venv sia configurato: `backend/venv/bin/activate`
2. Controlla i log: `tail -f backend/backend.log`
3. Assicurati che la porta 8000 sia libera: `lsof -i :8000`

### Se il frontend non parte:
1. Assicurati di essere nel folder `frontend/` con `package.json`
2. Controlla i log: `tail -f frontend/frontend.log`
3. Assicurati che la porta 3000 sia libera: `lsof -i :3000`

### Per fermare forzatamente i servizi:
```bash
pkill -f uvicorn      # Ferma il backend
pkill -f vite         # Ferma il frontend
pkill -f "npm run dev" # Ferma npm dev
```

---

## ✅ Checklist Funzionamento

- [x] START.sh avvia backend sulla porta 8000
- [x] START.sh avvia frontend sulla porta 3000
- [x] Backend risponde agli health check
- [x] STOP.sh ferma entrambi i servizi
- [x] Script pulisce correttamente le porte
- [x] Salva i PID per il controllo

---

## 🎓 Note

1. **Permissions**: I script hanno permessi di esecuzione
2. **Background execution**: Lo script termina ma i servizi continuano in background
3. **PID files**: Vengono salvati in `.backend.pid` e `.frontend.pid` per riferimento
4. **Automatic cleanup**: STOP.sh pulisce automaticamente le porte anche se i processi non rispondono

---

## 📚 Comandi Rapidi

```bash
# Avvia tutto
cd ~/Sviluppo\ Python/garage-management && ./START.sh &

# Ferma tutto
./STOP.sh

# Verifica status
curl http://localhost:8000/health
curl http://localhost:3000

# Guarda i log
tail -f backend/backend.log
tail -f frontend/frontend.log

# Accedi all'app
open http://localhost:3000
```

---

**✅ SCRIPTS VERIFICATI E PRONTI ALL'USO**
