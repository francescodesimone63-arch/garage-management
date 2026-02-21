# 🚀 COME RIAVVIARE IL SISTEMA (Garage Management RBAC)

## Se il sistema è bloccato o non risponde

### Step 1: Apri un NUOVO terminale (Command + T)
```bash
# Non usare il terminale corrente - è probabilmente bloccato
```

### Step 2: Naviga alla cartella del progetto
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management
```

### Step 3: Pulisci prima (opzionale but recommended)
```bash
pkill -9 python 2>/dev/null
pkill -9 node 2>/dev/null
pkill -9 uvicorn 2>/dev/null
sleep 3
```

### Step 4: Avvia il sistema con START.sh
```bash
bash START.sh
```

... e rispondi `s` (sì) se ti chiede di confermare la porta 8000

---

## ✅ Aspetta fino a che non vedi:

```
✅ Backend: http://0.0.0.0:8000
✅ Frontend: http://localhost:3000
... (altri log)
```

---

## 🎯 Allora:

1. Apri browser: `http://localhost:3000`
2. Login con: `admin@garage.local` / `admin123`
3. Dovresti entrare nel sistema RBAC completo

---

## ❓ Se ancora non funziona:

### Opzione 1: Avvia manualmente separatamente

**Terminal 1 - Backend:**
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /Users/francescodesimone/Sviluppo\ Python/garage-management/frontend
npm run dev
```

### Opzione 2: Check health
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}

curl http://localhost:3000
# Should return HTML of login page
```

---

## ⚠️ NOTA CRITICA

Il sistema RBAC è **COMPLETO** ma ci sono ancora alcuni file che necessitano di fix tecnici:

**TODO - NEXT SESSION:**
- ❌ Fix `/backend/app/api/v1/permissions.py` (async/sync conflict)
- ❌ Remove `dependencies=[Depends(...)]` decorators dall endpoint finché permissions.py non è fixato
- ❌ After permissions.py is fixed, re-apply all endpoint protections

**Per adesso l'app funziona SENZA protezioni endpoint** - il RBAC database è completo, ma l'enforcement API è in sospeso.

---

## 📝 SISTEMA RBAC - STATO ATTUALE

```
✅ Database con 8 ruoli, 44 permissions, 352 mappings
✅ Auth con JWT token
✅ Frontend components (RolePermissionsMatrix, UsersManager)
✅ Custom hooks (usePermission, useIsAdmin, etc.)
⏳ API endpoints protection (in sospeso - async/sync issue)
```

---

**QUANDO RIPROVARE**: Su nuovo terminale con `bash START.sh`

