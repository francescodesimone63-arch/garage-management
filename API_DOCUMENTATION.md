# 📚 API DOCUMENTATION - GARAGE MANAGEMENT SYSTEM

## 📋 INDICE

1. [Introduzione](#introduzione)
2. [Autenticazione](#autenticazione)
3. [Convenzioni API](#convenzioni-api)
4. [Endpoints](#endpoints)
   - [Auth](#auth-endpoints)
   - [Users](#users-endpoints)
   - [Customers](#customers-endpoints)
   - [Vehicles](#vehicles-endpoints)
   - [Work Orders](#work-orders-endpoints)
   - [Parts](#parts-endpoints)
   - [Stock Movements](#stock-movements-endpoints)
   - [Tires](#tires-endpoints)
   - [Courtesy Cars](#courtesy-cars-endpoints)
   - [Maintenance Schedules](#maintenance-schedules-endpoints)
   - [Notifications](#notifications-endpoints)
   - [Calendar](#calendar-endpoints)
   - [Reports](#reports-endpoints)
5. [Codici di Errore](#codici-di-errore)
6. [Rate Limiting](#rate-limiting)

---

## 🚀 INTRODUZIONE

### Base URL
```
Sviluppo: http://localhost:8000/api/v1
Produzione: https://api.garage-management.com/api/v1
```

### Headers Richiesti
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>  # Per endpoint autenticati
```

---

## 🔐 AUTENTICAZIONE

Il sistema utilizza JWT (JSON Web Tokens) per l'autenticazione.

### Token Structure
```json
{
  "sub": "user_id",
  "username": "mario.rossi",
  "ruolo": "GM",
  "exp": 1234567890
}
```

### Token Lifecycle
- **Access Token**: 8 ore
- **Refresh Token**: 30 giorni

---

## 📐 CONVENZIONI API

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operazione completata",
  "timestamp": "2026-02-09T14:30:00Z"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dati non validi",
    "details": [
      {
        "field": "email",
        "message": "Email non valida"
      }
    ]
  },
  "timestamp": "2026-02-09T14:30:00Z"
}
```

### Pagination
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

### Filtering
```
GET /api/v1/resource?filter[field]=value&filter[field2]=value2
```

### Sorting
```
GET /api/v1/resource?sort=field,-field2  # + ASC, - DESC
```

---

## 📍 ENDPOINTS

### AUTH ENDPOINTS

#### 🔹 POST /auth/login
**Descrizione**: Login utente

**Request Body:**
```json
{
  "username": "mario.rossi",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "id": 1,
      "username": "mario.rossi",
      "email": "mario@garage.it",
      "ruolo": "GM",
      "nome": "Mario",
      "cognome": "Rossi"
    }
  }
}
```

---

#### 🔹 POST /auth/refresh
**Descrizione**: Rinnova access token

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 28800
  }
}
```

---

#### 🔹 POST /auth/logout
**Descrizione**: Logout utente

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logout effettuato con successo"
}
```

---

#### 🔹 GET /auth/me
**Descrizione**: Profilo utente corrente

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "mario.rossi",
    "email": "mario@garage.it",
    "ruolo": "GM",
    "nome": "Mario",
    "cognome": "Rossi",
    "attivo": true,
    "created_at": "2026-01-01T10:00:00Z"
  }
}
```

---

### USERS ENDPOINTS

#### 🔹 GET /users
**Descrizione**: Lista utenti (solo ADMIN)

**Query Parameters:**
- `ruolo`: Filtra per ruolo (GM, CMM, CBM)
- `attivo`: Filtra per stato (true/false)
- `page`: Numero pagina (default: 1)
- `per_page`: Risultati per pagina (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "mario.rossi",
        "email": "mario@garage.it",
        "ruolo": "GM",
        "nome": "Mario",
        "cognome": "Rossi",
        "attivo": true
      }
    ],
    "total": 4,
    "page": 1,
    "per_page": 20,
    "pages": 1
  }
}
```

---

#### 🔹 POST /users
**Descrizione**: Crea nuovo utente (solo ADMIN)

**Request Body:**
```json
{
  "username": "nuovo.utente",
  "email": "nuovo@garage.it",
  "password": "password123",
  "ruolo": "CMM",
  "nome": "Nuovo",
  "cognome": "Utente"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "username": "nuovo.utente",
    "email": "nuovo@garage.it",
    "ruolo": "CMM",
    "nome": "Nuovo",
    "cognome": "Utente",
    "attivo": true,
    "created_at": "2026-02-09T14:30:00Z"
  }
}
```

---

### CUSTOMERS ENDPOINTS

#### 🔹 GET /customers
**Descrizione**: Lista clienti

**Query Parameters:**
- `search`: Ricerca per nome, cognome, email, telefono
- `tipo`: privato/azienda
- `page`: Numero pagina
- `per_page`: Risultati per pagina

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "nome": "Giovanni",
        "cognome": "Bianchi",
        "ragione_sociale": null,
        "codice_fiscale": "BNCGNN80A01H501Z",
        "telefono": "+39 333 1234567",
        "email": "giovanni.bianchi@email.it",
        "citta": "Roma",
        "veicoli_count": 2
      }
    ],
    "total": 150,
    "page": 1,
    "per_page": 20,
    "pages": 8
  }
}
```

---

#### 🔹 POST /customers
**Descrizione**: Crea nuovo cliente

**Request Body:**
```json
{
  "nome": "Giovanni",
  "cognome": "Bianchi",
  "codice_fiscale": "BNCGNN80A01H501Z",
  "telefono": "+39 333 1234567",
  "email": "giovanni.bianchi@email.it",
  "indirizzo": "Via Roma 123",
  "citta": "Roma",
  "cap": "00100",
  "provincia": "RM",
  "preferenze_notifica": {
    "email": true,
    "sms": false,
    "whatsapp": true
  }
}
```

---

### VEHICLES ENDPOINTS

#### 🔹 GET /vehicles
**Descrizione**: Lista veicoli

**Query Parameters:**
- `tipo`: cliente/cortesia
- `customer_id`: ID cliente proprietario
- `search`: Ricerca per targa, marca, modello

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "targa": "AB123CD",
        "marca": "Fiat",
        "modello": "500",
        "anno": 2020,
        "colore": "Rosso",
        "km_attuali": 25000,
        "tipo": "cliente",
        "customer": {
          "id": 1,
          "nome": "Giovanni Bianchi"
        }
      }
    ]
  }
}
```

---

### WORK ORDERS ENDPOINTS

#### 🔹 GET /work-orders
**Descrizione**: Lista schede lavoro

**Query Parameters:**
- `stato`: bozza/approvata/in_lavorazione/completata/annullata
- `priorita`: bassa/media/alta/urgente
- `customer_id`: ID cliente
- `vehicle_id`: ID veicolo
- `data_da`: Data appuntamento da (YYYY-MM-DD)
- `data_a`: Data appuntamento a (YYYY-MM-DD)
- `assegnato_a`: CMM/CBM (filtra per attività assegnate)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "numero_scheda": "WO-2026-0001",
        "stato": "approvata",
        "data_appuntamento": "2026-02-15T09:00:00Z",
        "data_fine_prevista": "2026-02-15T17:00:00Z",
        "tipo_danno": "carrozzeria_leggera",
        "priorita": "media",
        "customer": {
          "id": 1,
          "nome": "Giovanni Bianchi",
          "telefono": "+39 333 1234567"
        },
        "vehicle": {
          "id": 1,
          "targa": "AB123CD",
          "marca": "Fiat",
          "modello": "500"
        },
        "attivita_count": 3,
        "parti_count": 5,
        "costo_stimato": 450.00
      }
    ]
  }
}
```

---

#### 🔹 POST /work-orders
**Descrizione**: Crea nuova scheda lavoro

**Request Body:**
```json
{
  "customer_id": 1,
  "vehicle_id": 1,
  "tipo_danno": "carrozzeria_leggera",
  "priorita": "media",
  "valutazione_danno": "Ammaccatura portiera anteriore destra...",
  "note": "Cliente richiede auto cortesia",
  "attivita": [
    {
      "descrizione": "Raddrizzatura portiera",
      "tipo": "carrozzeria",
      "ore_stimate": 2.5
    },
    {
      "descrizione": "Verniciatura portiera",
      "tipo": "carrozzeria",
      "ore_stimate": 1.5
    }
  ],
  "parti": [
    {
      "part_id": 15,
      "quantita_richiesta": 1
    }
  ]
}
```

---

#### 🔹 POST /work-orders/{id}/approve
**Descrizione**: Approva scheda lavoro (solo GM)

**Request Body:**
```json
{
  "data_appuntamento": "2026-02-15T09:00:00Z",
  "data_fine_prevista": "2026-02-15T17:00:00Z",
  "auto_cortesia_id": 3,
  "note_approvazione": "Approvato, procedere con i lavori"
}
```

---

#### 🔹 POST /work-orders/{id}/suggest-appointment
**Descrizione**: Suggerisce appuntamento ottimale

**Request Body:**
```json
{
  "durata_ore": 8,
  "tipo_lavoro": "carrozzeria",
  "urgenza": "normale"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "suggerimenti": [
      {
        "data_inizio": "2026-02-15T09:00:00Z",
        "data_fine": "2026-02-15T17:00:00Z",
        "disponibilita": "ottima",
        "auto_cortesia_disponibili": [3, 5]
      },
      {
        "data_inizio": "2026-02-16T09:00:00Z",
        "data_fine": "2026-02-16T17:00:00Z",
        "disponibilita": "buona",
        "auto_cortesia_disponibili": [2, 3, 5]
      }
    ]
  }
}
```

---

### PARTS ENDPOINTS

#### 🔹 GET /parts
**Descrizione**: Lista parti di ricambio

**Query Parameters:**
- `search`: Ricerca per codice, nome, descrizione
- `categoria`: Filtra per categoria
- `sotto_scorta`: true per parti sotto scorta minima
- `tipo`: ricambio/fornitura

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "codice": "OIL-5W30",
        "nome": "Olio motore 5W30",
        "categoria": "Lubrificanti",
        "quantita": 50,
        "quantita_minima": 10,
        "unita_misura": "litri",
        "prezzo_acquisto": 15.00,
        "prezzo_vendita": 25.00,
        "fornitore": "Fornitore Auto Srl",
        "posizione_magazzino": "A-01-03",
        "sotto_scorta": false
      }
    ]
  }
}
```

---

#### 🔹 POST /parts/check-availability
**Descrizione**: Verifica disponibilità parti per scheda lavoro

**Request Body:**
```json
{
  "parti": [
    {
      "part_id": 1,
      "quantita": 5
    },
    {
      "part_id": 3,
      "quantita": 2
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "disponibili": [
      {
        "part_id": 1,
        "disponibile": true,
        "quantita_disponibile": 50
      }
    ],
    "non_disponibili": [
      {
        "part_id": 3,
        "disponibile": false,
        "quantita_disponibile": 1,
        "quantita_mancante": 1
      }
    ]
  }
}
```

---

#### 🔹 POST /parts/search-suppliers
**Descrizione**: Ricerca fornitori tramite AI

**Request Body:**
```json
{
  "parte": "Pastiglie freno anteriori Fiat 500 2020",
  "urgente": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "fornitori": [
      {
        "nome": "AutoRicambi.it",
        "prezzo": 35.00,
        "disponibilita": "Immediata",
        "link": "https://autoricambi.it/...",
        "valutazione": 4.5
      },
      {
        "nome": "RicambiOnline24",
        "prezzo": 32.50,
        "disponibilita": "2-3 giorni",
        "link": "https://ricambionline24.it/...",
        "valutazione": 4.2
      }
    ]
  }
}
```

---

### TIRES ENDPOINTS

#### 🔹 GET /tires/alerts
**Descrizione**: Alert cambio pneumatici

**Query Parameters:**
- `giorni`: Giorni di preavviso (default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": 1,
        "vehicle": {
          "targa": "AB123CD",
          "marca": "Fiat",
          "modello": "500"
        },
        "customer": {
          "nome": "Giovanni Bianchi",
          "telefono": "+39 333 1234567",
          "email": "giovanni.bianchi@email.it"
        },
        "tipo_stagione": "estivo",
        "data_prossimo_cambio": "2026-03-15",
        "giorni_alla_scadenza": 34
      }
    ],
    "total": 15
  }
}
```

---

#### 🔹 POST /tires/send-alerts
**Descrizione**: Invia notifiche cambio pneumatici

**Request Body:**
```json
{
  "tire_ids": [1, 2, 3],
  "canali": ["email", "sms"],
  "messaggio_personalizzato": "Gentile cliente, le ricordiamo..."
}
```

---

### COURTESY CARS ENDPOINTS

#### 🔹 GET /courtesy-cars/available
**Descrizione**: Auto cortesia disponibili per date

**Query Parameters:**
- `data_inizio`: Data inizio (YYYY-MM-DD)
- `data_fine`: Data fine (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "auto_disponibili": [
      {
        "id": 1,
        "vehicle": {
          "targa": "CC001GA",
          "marca": "Fiat",
          "modello": "Panda"
        },
        "contratto_tipo": "leasing",
        "disponibile_dal": "2026-02-15",
        "disponibile_al": "2026-02-20"
      }
    ]
  }
}
```

---

### REPORTS ENDPOINTS

#### 🔹 GET /reports/dashboard
**Descrizione**: Statistiche dashboard

**Query Parameters:**
- `periodo`: oggi/settimana/mese/anno
- `ruolo`: GM/CMM/CBM (filtra dati per ruolo)

**Response:**
```json
{
  "success": true,
  "data": {
    "schede_lavoro": {
      "totali": 45,
      "in_corso": 12,
      "completate_oggi": 3,
      "appuntamenti_oggi": 5
    },
    "magazzino": {
      "valore_totale": 15420.50,
      "parti_sotto_scorta": 8,
      "ordini_in_arrivo": 3
    },
    "auto_cortesia": {
      "totali": 5,
      "disponibili": 2,
      "in_uso": 3
    },
    "scadenze": {
      "pneumatici_prossimi_30gg": 15,
      "manutenzioni_prossime": 8,
      "contratti_auto_scadenza": 1
    }
  }
}
```

---

#### 🔹 GET /reports/export
**Descrizione**: Export dati in PDF/Excel

**Query Parameters:**
- `tipo`: work-orders/inventory/customers
- `formato`: pdf/excel
- `data_da`: Data inizio periodo
- `data_a`: Data fine periodo

**Response:**
```json
{
  "success": true,
  "data": {
    "file_url": "https://api.garage.com/downloads/report_12345.pdf",
    "expires_at": "2026-02-09T15:30:00Z"
  }
}
```

---

## 🚨 CODICI DI ERRORE

| Codice | HTTP Status | Descrizione |
|--------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Token mancante o non valido |
| `FORBIDDEN` | 403 | Permessi insufficienti |
| `NOT_FOUND` | 404 | Risorsa non trovata |
| `VALIDATION_ERROR` | 422 | Dati di input non validi |
| `DUPLICATE_ENTRY` | 409 | Risorsa già esistente |
| `INTERNAL_ERROR` | 500 | Errore interno del server |
| `RATE_LIMIT_EXCEEDED` | 429 | Troppe richieste |

### Esempio Errore
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dati non validi",
    "details": [
      {
        "field": "email",
        "message": "Formato email non valido"
      },
      {
        "field": "telefono",
        "message": "Campo obbligatorio"
      }
    ]
  },
  "timestamp": "2026-02-09T14:30:00Z"
}
```

---

## ⏱️ RATE LIMITING

### Limiti per Ruolo

| Ruolo | Richieste/Minuto | Richieste/Ora |
|-------|------------------|---------------|
| ADMIN | 120 | 3600 |
| GM | 60 | 1800 |
| CMM/CBM | 30 | 900 |

### Headers Rate Limit
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1644415800
```

### Risposta Rate Limit Exceeded
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Limite di richieste superato",
    "retry_after": 45
  }
}
```

---

**Documento creato:** 09/02/2026  
**Versione:** 1.0  
**Swagger UI:** `/docs` (solo sviluppo)