# 📋 SCHEMA ER - Garage Management System (garage.db)

## Memorizzazione del 20 febbraio 2026

### Struttura Principale del Database

```
garage.db (SQLite)
├── 26 Tabelle
├── 5 Clienti
├── 10 Veicoli  
├── 15 Ordini di Lavoro
└── Admin User: admin@garage.local / admin123
```

---

## 🔑 Entità Principali

### 1️⃣ CORE ENTITIES - NUCLEO DEL SISTEMA

#### **USERS** (Autenticazione)
- `id` (PK)
- `username`, `email`, `password_hash`
- `ruolo`: ADMIN, GENERAL_MANAGER, CMM, CBM
- `attivo`, `ultimo_accesso`
- **Relazioni:** Crea activity logs, assegna work orders

#### **CUSTOMERS** (Anagrafe Clienti)
- `id` (PK)
- `tipo`: privato, azienda
- `nome`, `cognome` (per privati)
- `ragione_sociale` (per aziende)
- `email`, `telefono`, `cellulare`
- `indirizzo`, `cap`, `provincia`
- `codice_fiscale`, `partita_iva`
- **Relazioni:** Possiede veicoli, richiede work orders

#### **VEHICLES** (Parco Auto)
- `id` (PK)
- `customer_id` (FK) - Cliente proprietario
- `marca`, `modello`, `anno`
- `targa`, `numero_seriale`
- `cilindrata`, `carburante`
- `note`, `disponibile`
- **Relazioni:** Soggetto di work orders, monta tires

#### **WORK_ORDERS** (Ordini di Lavoro - ENTITÀ CENTRALE)
- `id` (PK)
- `numero_scheda` (UNIQUE)
- `customer_id`, `vehicle_id` (FK)
- `data_compilazione`, `data_creazione`, `data_fine_prevista`
- `valutazione_danno` (descrizione danni)
- `stato`: BOZZA, APPROVATA, IN_LAVORAZIONE, COMPLETATA, ANNULLATA
- `priorita`: BASSA, MEDIA, ALTA, URGENTE
- `costo_stimato`, `costo_effettivo`
- `courtesy_car` (Boolean)
- **Relazioni:** Collega customers, vehicles, interventions, parts, documents

---

### 2️⃣ INTERVENTI E ATTIVITÀ

#### **INTERVENTIONS** (Interventi Tecnici)
- `id` (PK)
- `work_order_id` (FK)
- `tipo`: MECCANICA, CARROZZERIA
- `descrizione`
- `stato`: DA_FARE, IN_CORSO, COMPLETATA
- `data_inizio`, `data_fine`
- `tecnico_assegnato`
- **Relazioni:** Appartiene a work orders, genera activities

#### **WORK_ORDER_ACTIVITIES** (Attività Svolte)
- `id` (PK)
- `work_order_id`, `intervention_id` (FK)
- `tipo`: MECCANICA, CARROZZERIA
- `descrizione`
- `ore_lavoro`
- `stato`: DA_FARE, IN_CORSO, COMPLETATA
- **Relazioni:** Traccia attività un work order

#### **WORK_ORDER_PARTS** (Parti Utilizzate)
- `id` (PK)
- `work_order_id`, `part_id` (FK)
- `quantita`
- `prezzo_unitario`
- **Relazioni:** Lega work orders a parts

---

### 3️⃣ MAGAZZINO E INVENTARIO

#### **PARTS** (Catalogo Pezzi)
- `id` (PK)
- `codice` (UNIQUE)
- `descrizione`
- `categoria`
- `prezzo_acquisto`, `prezzo_vendita`
- `quantita_disponibile`
- `quantita_minima`
- **Relazioni:** Utilizzate in work order parts, movimenti stock

#### **STOCK_MOVEMENTS** (Movimenti Magazzino)
- `id` (PK)
- `part_id` (FK)
- `tipo`: INGRESSO, USCITA
- `quantita`
- `data_movimento`
- `motivo`
- **Relazioni:** Traccia history di parts

---

### 4️⃣ AUTO DI CORTESIA

#### **COURTESY_CARS** (Anagrafe Auto Cortesia)
- `id` (PK)
- `targa` (UNIQUE)
- `marca`, `modello`
- `disponibile` (Boolean)
- `note`
- **Relazioni:** Assegnate tramite car_assignments

#### **CAR_ASSIGNMENTS** (Assegnazioni Auto Cortesia)
- `id` (PK)
- `customer_id`, `vehicle_id`, `courtesy_car_id` (FK)
- `data_assegnazione`
- `data_restituzione`
- `km_consegnati`, `km_restituiti`
- `stato_auto`
- **Relazioni:** Lega customers a courtesy cars

---

### 5️⃣ MANUTENZIONE PROGRAMMATA

#### **MAINTENANCE_SCHEDULES** (Programmi Manutenzione)
- `id` (PK)
- `vehicle_id` (FK)
- `tipo_intervento`
- `km_previsti`
- `mesi_previsti`
- `data_prossima_manutenzione`
- `completata` (Boolean)
- **Relazioni:** Pianificazione per vehicles

---

### 6️⃣ DOCUMENTI E TRACCIABILITÀ

#### **DOCUMENTS** (Documenti)
- `id` (PK)
- `work_order_id` (FK)
- `type`: PREVENTIVO, FATTURA, RICEVUTA, REPORT
- `filename`, `filepath`
- `data_creazione`
- `creator_id`
- **Relazioni:** Associati a work orders

#### **WORK_ORDER_AUDITS** (Cronologia Transizioni)
- `id` (PK)
- `work_order_id` (FK)
- `stato_precedente`, `stato_nuovo`
- `data_transizione`
- `utente_id`
- `motivo`
- **Relazioni:** Traccia tutte le transizioni di stato

#### **ACTIVITY_LOGS** (Log Attività Utenti)
- `id` (PK)
- `user_id` (FK)
- `azione`: CREATE, UPDATE, DELETE, VIEW
- `entita`, `entita_id`
- `timestamp`
- `ip_address`, `user_agent`
- **Relazioni:** Traccia azioni di users

#### **NOTIFICATIONS** (Notifiche)
- `id` (PK)
- `user_id` (FK)
- `tipo`
- `messaggio`
- `letta` (Boolean)
- `data_creazione`
- **Relazioni:** Notifiche per users

---

### 7️⃣ INTEGRAZIONI

#### **GOOGLE_OAUTH_TOKENS**
- Token OAuth per Google Calendar
- Lega users a Google

#### **CALENDAR_EVENTS**
- `id` (PK)
- `work_order_id` (FK)
- `google_event_id`
- `titolo`, `descrizione`
- `data_inizio`, `data_fine`
- **Relazioni:** Sincronizzazione con Google Calendar

---

### 8️⃣ LOOKUP TABLES (Dati Fissi)

- **CUSTOMER_TYPES**: privato, azienda
- **WORK_ORDER_STATUS_TYPES**: BOZZA, APPROVATA, ...
- **INTERVENTION_STATUS_TYPES**: DA_FARE, IN_CORSO, ...
- **PRIORITY_TYPES**: BASSA, MEDIA, ALTA, URGENTE
- **DAMAGE_TYPES**: Tipologie danni
- **INSURANCE_BRANCH_TYPES**: Rami assicurativi

---

## 🔗 Relazioni Chiave

```
CUSTOMERS (1) ←→ (N) VEHICLES
        ↓
     (usa in)
        ↓
CUSTOMERS (1) ←→ (N) WORK_ORDERS
        ↑                ↓
        └────────────────┘
        
VEHICLES (1) ←→ (N) WORK_ORDERS
                    ↓
     ┌──────────────┼──────────────┐
     ↓              ↓              ↓
INTERVENTIONS  WORK_ORDER_PARTS   DOCUMENTS
     ↓              ↓
ACTIVITIES      PARTS → STOCK_MOVEMENTS

WORK_ORDERS → CALENDAR_EVENTS (Google) → NOTIFICATIONS
```

---

## 📊 DATI ATTUALI (loaded)

| Entità | Count |
|--------|-------|
| Users | 1 (admin) |
| Customers | 5 |
| Vehicles | 10 |
| Work Orders | 15 |
| Parts | - |
| Courtesy Cars | - |

---

## 🎯 FUNZIONALITÀ DA IMPLEMENTARE

### Priority 1 (Core) ⭐⭐⭐
- [ ] CRUD Customers (R)
- [ ] CRUD Vehicles (R)
- [ ] CRUD Work Orders (CRUD)
- [ ] Work Order Status Flow (BOZZA → APPROVATA → IN_LAVORAZIONE → COMPLETATA)
- [ ] Interventions & Activities

### Priority 2 (Important) ⭐⭐
- [ ] Parts Management
- [ ] Work Order Audits (Cronologia)
- [ ] Documents (Preventivi, Fatture)
- [ ] Courtesy Cars Assignment
- [ ] Notifications

### Priority 3 (Advanced) ⭐
- [ ] Google Calendar Integration
- [ ] Maintenance Schedules
- [ ] Stock Movements
- [ ] Reports & Analytics

---

## 📝 NOTE DI PROGETTAZIONE

1. **WORK_ORDERS è l'entità centrale** - collega tutto
2. **Approvazione obbligatoria** - tutte le schede richiedono GM approval
3. **Audit trail completo** - ogni transizione di stato è tracciata
4. **Multi-activity support** - una scheda può avere meccanica + carrozzeria
5. **Integration ready** - Google Calendar pre-integrato

Documento creato: 20 febbraio 2026, 15:00
