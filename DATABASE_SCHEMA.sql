-- =====================================================
-- GARAGE MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =====================================================
-- Database: SQLite (sviluppo) / PostgreSQL (produzione)
-- Versione: 1.0
-- Data: 09/02/2026
-- =====================================================

-- Nota: Questo schema è compatibile sia con SQLite che PostgreSQL
-- Per SQLite: AUTOINCREMENT
-- Per PostgreSQL: sostituire con SERIAL

-- =====================================================
-- TABELLA 1: users - Utenti del sistema
-- =====================================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ruolo VARCHAR(20) NOT NULL CHECK(ruolo IN ('GM', 'CMM', 'CBM', 'ADMIN')),
    nome VARCHAR(100),
    cognome VARCHAR(100),
    attivo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici per ottimizzazione
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_ruolo ON users(ruolo);

-- =====================================================
-- TABELLA 2: customers - Anagrafica clienti
-- =====================================================
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    ragione_sociale VARCHAR(200),
    codice_fiscale VARCHAR(16),
    partita_iva VARCHAR(11),
    telefono VARCHAR(20),
    email VARCHAR(100),
    indirizzo TEXT,
    citta VARCHAR(100),
    cap VARCHAR(10),
    provincia VARCHAR(2),
    preferenze_notifica TEXT, -- JSON: {"email": true, "sms": false, "whatsapp": true}
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_telefono ON customers(telefono);
CREATE INDEX idx_customers_cf ON customers(codice_fiscale);

-- =====================================================
-- TABELLA 3: vehicles - Veicoli (clienti + cortesia)
-- =====================================================
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    targa VARCHAR(10) UNIQUE NOT NULL,
    telaio VARCHAR(17),
    marca VARCHAR(50),
    modello VARCHAR(50),
    anno INTEGER,
    colore VARCHAR(30),
    km_attuali INTEGER,
    customer_id INTEGER,
    tipo VARCHAR(20) CHECK(tipo IN ('cliente', 'cortesia')) DEFAULT 'cliente',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE INDEX idx_vehicles_targa ON vehicles(targa);
CREATE INDEX idx_vehicles_customer ON vehicles(customer_id);
CREATE INDEX idx_vehicles_tipo ON vehicles(tipo);

-- =====================================================
-- TABELLA 4: work_orders - Schede lavoro
-- =====================================================
CREATE TABLE work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_scheda VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_appuntamento TIMESTAMP,
    data_fine_prevista TIMESTAMP,
    data_completamento TIMESTAMP,
    stato VARCHAR(20) CHECK(stato IN ('bozza', 'approvata', 'in_lavorazione', 'completata', 'annullata')) DEFAULT 'bozza',
    tipo_danno VARCHAR(50),
    priorita VARCHAR(20) CHECK(priorita IN ('bassa', 'media', 'alta', 'urgente')) DEFAULT 'media',
    valutazione_danno TEXT,
    note TEXT,
    creato_da INTEGER,
    approvato_da INTEGER,
    auto_cortesia_id INTEGER,
    costo_stimato DECIMAL(10,2),
    costo_finale DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (creato_da) REFERENCES users(id),
    FOREIGN KEY (approvato_da) REFERENCES users(id)
    -- FK auto_cortesia_id aggiunta dopo creazione tabella courtesy_cars
);

CREATE INDEX idx_work_orders_numero ON work_orders(numero_scheda);
CREATE INDEX idx_work_orders_customer ON work_orders(customer_id);
CREATE INDEX idx_work_orders_vehicle ON work_orders(vehicle_id);
CREATE INDEX idx_work_orders_stato ON work_orders(stato);
CREATE INDEX idx_work_orders_data_app ON work_orders(data_appuntamento);

-- =====================================================
-- TABELLA 5: work_order_activities - Attività per scheda
-- =====================================================
CREATE TABLE work_order_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    descrizione TEXT NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('meccanica', 'carrozzeria')) NOT NULL,
    assegnato_a VARCHAR(10) CHECK(assegnato_a IN ('CMM', 'CBM')),
    stato VARCHAR(20) CHECK(stato IN ('da_fare', 'in_corso', 'completata')) DEFAULT 'da_fare',
    ore_stimate DECIMAL(5,2),
    ore_effettive DECIMAL(5,2),
    costo_manodopera DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_activities_work_order ON work_order_activities(work_order_id);
CREATE INDEX idx_activities_tipo ON work_order_activities(tipo);
CREATE INDEX idx_activities_stato ON work_order_activities(stato);

-- =====================================================
-- TABELLA 6: parts - Parti di ricambio
-- =====================================================
CREATE TABLE parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descrizione TEXT,
    categoria VARCHAR(100),
    marca VARCHAR(100),
    modello VARCHAR(100),
    quantita DECIMAL(10,2) DEFAULT 0,
    quantita_minima DECIMAL(10,2) DEFAULT 5,
    prezzo_acquisto DECIMAL(10,2),
    prezzo_vendita DECIMAL(10,2),
    fornitore VARCHAR(200),
    posizione_magazzino VARCHAR(100),
    tipo VARCHAR(20) CHECK(tipo IN ('ricambio', 'fornitura')) DEFAULT 'ricambio',
    unita_misura VARCHAR(10) DEFAULT 'pz',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parts_codice ON parts(codice);
CREATE INDEX idx_parts_categoria ON parts(categoria);
CREATE INDEX idx_parts_quantita ON parts(quantita);

-- =====================================================
-- TABELLA 7: work_order_parts - Parti associate a schede
-- =====================================================
CREATE TABLE work_order_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    quantita_richiesta DECIMAL(10,2) NOT NULL,
    quantita_utilizzata DECIMAL(10,2) DEFAULT 0,
    stato VARCHAR(20) CHECK(stato IN ('da_ordinare', 'in_arrivo', 'disponibile', 'utilizzata', 'non_utilizzata')) DEFAULT 'da_ordinare',
    data_ordine TIMESTAMP,
    data_arrivo TIMESTAMP,
    data_utilizzo TIMESTAMP,
    fornitore_ordine VARCHAR(200),
    prezzo_acquisto DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

CREATE INDEX idx_wo_parts_work_order ON work_order_parts(work_order_id);
CREATE INDEX idx_wo_parts_part ON work_order_parts(part_id);
CREATE INDEX idx_wo_parts_stato ON work_order_parts(stato);

-- =====================================================
-- TABELLA 8: stock_movements - Movimenti magazzino
-- =====================================================
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id INTEGER NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('carico', 'scarico', 'rettifica')) NOT NULL,
    quantita DECIMAL(10,2) NOT NULL,
    quantita_precedente DECIMAL(10,2),
    quantita_nuova DECIMAL(10,2),
    work_order_id INTEGER,
    data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    utente_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (utente_id) REFERENCES users(id)
);

CREATE INDEX idx_movements_part ON stock_movements(part_id);
CREATE INDEX idx_movements_data ON stock_movements(data_movimento);
CREATE INDEX idx_movements_tipo ON stock_movements(tipo);

-- =====================================================
-- TABELLA 9: tires - Pneumatici depositati
-- =====================================================
CREATE TABLE tires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    tipo_stagione VARCHAR(20) CHECK(tipo_stagione IN ('estivo', 'invernale')) NOT NULL,
    marca VARCHAR(50),
    modello VARCHAR(50),
    misura VARCHAR(30),
    data_deposito TIMESTAMP,
    data_ultimo_cambio TIMESTAMP,
    data_prossimo_cambio TIMESTAMP,
    stato VARCHAR(20) CHECK(stato IN ('depositati', 'montati')) DEFAULT 'depositati',
    posizione_deposito VARCHAR(50),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_tires_vehicle ON tires(vehicle_id);
CREATE INDEX idx_tires_prossimo_cambio ON tires(data_prossimo_cambio);
CREATE INDEX idx_tires_stato ON tires(stato);

-- =====================================================
-- TABELLA 10: courtesy_cars - Auto di cortesia
-- =====================================================
CREATE TABLE courtesy_cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER UNIQUE NOT NULL,
    contratto_tipo VARCHAR(20) CHECK(contratto_tipo IN ('leasing', 'affitto', 'proprieta')) NOT NULL,
    fornitore_contratto VARCHAR(200),
    data_inizio_contratto DATE,
    data_scadenza_contratto DATE,
    canone_mensile DECIMAL(10,2),
    km_inclusi_anno INTEGER,
    stato VARCHAR(20) CHECK(stato IN ('disponibile', 'assegnata', 'manutenzione', 'fuori_servizio')) DEFAULT 'disponibile',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_courtesy_stato ON courtesy_cars(stato);
CREATE INDEX idx_courtesy_scadenza ON courtesy_cars(data_scadenza_contratto);

-- Aggiunta FK mancante in work_orders
-- ALTER TABLE work_orders ADD CONSTRAINT fk_auto_cortesia 
-- FOREIGN KEY (auto_cortesia_id) REFERENCES courtesy_cars(id);

-- =====================================================
-- TABELLA 11: car_assignments - Assegnazioni auto cortesia
-- =====================================================
CREATE TABLE car_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    courtesy_car_id INTEGER NOT NULL,
    work_order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    data_inizio TIMESTAMP NOT NULL,
    data_fine_prevista TIMESTAMP NOT NULL,
    data_fine_effettiva TIMESTAMP,
    km_inizio INTEGER,
    km_fine INTEGER,
    stato VARCHAR(20) CHECK(stato IN ('prenotata', 'in_corso', 'completata', 'annullata')) DEFAULT 'prenotata',
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courtesy_car_id) REFERENCES courtesy_cars(id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE INDEX idx_assignments_courtesy_car ON car_assignments(courtesy_car_id);
CREATE INDEX idx_assignments_work_order ON car_assignments(work_order_id);
CREATE INDEX idx_assignments_date ON car_assignments(data_inizio, data_fine_prevista);
CREATE INDEX idx_assignments_stato ON car_assignments(stato);

-- =====================================================
-- TABELLA 12: maintenance_schedules - Scadenziari manutenzione
-- =====================================================
CREATE TABLE maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    tipo VARCHAR(20) CHECK(tipo IN ('ordinaria', 'straordinaria')) NOT NULL,
    descrizione TEXT NOT NULL,
    km_scadenza INTEGER,
    data_scadenza DATE,
    km_preavviso INTEGER DEFAULT 1000,
    giorni_preavviso INTEGER DEFAULT 30,
    stato VARCHAR(20) CHECK(stato IN ('attivo', 'completato', 'annullato')) DEFAULT 'attivo',
    ricorrente BOOLEAN DEFAULT FALSE,
    intervallo_km INTEGER,
    intervallo_giorni INTEGER,
    ultima_notifica TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

CREATE INDEX idx_schedules_vehicle ON maintenance_schedules(vehicle_id);
CREATE INDEX idx_schedules_scadenza ON maintenance_schedules(data_scadenza);
CREATE INDEX idx_schedules_stato ON maintenance_schedules(stato);

-- =====================================================
-- TABELLA 13: notifications - Log notifiche inviate
-- =====================================================
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo VARCHAR(20) CHECK(tipo IN ('email', 'sms', 'whatsapp')) NOT NULL,
    destinatario VARCHAR(200) NOT NULL,
    oggetto VARCHAR(200),
    messaggio TEXT NOT NULL,
    stato VARCHAR(20) CHECK(stato IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    data_invio TIMESTAMP,
    errore TEXT,
    riferimento_tipo VARCHAR(50),
    riferimento_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_stato ON notifications(stato);
CREATE INDEX idx_notifications_tipo ON notifications(tipo);
CREATE INDEX idx_notifications_data ON notifications(data_invio);
CREATE INDEX idx_notifications_destinatario ON notifications(destinatario);

-- =====================================================
-- TABELLA 14: calendar_events - Eventi Google Calendar
-- =====================================================
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER UNIQUE NOT NULL,
    google_event_id VARCHAR(255) UNIQUE,
    titolo VARCHAR(200) NOT NULL,
    descrizione TEXT,
    data_inizio TIMESTAMP NOT NULL,
    data_fine TIMESTAMP NOT NULL,
    partecipanti TEXT, -- JSON array
    sincronizzato BOOLEAN DEFAULT FALSE,
    ultima_sincronizzazione TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_calendar_work_order ON calendar_events(work_order_id);
CREATE INDEX idx_calendar_google_id ON calendar_events(google_event_id);
CREATE INDEX idx_calendar_data ON calendar_events(data_inizio, data_fine);

-- =====================================================
-- VISTE UTILI
-- =====================================================

-- Vista: Schede lavoro con dettagli cliente e veicolo
CREATE VIEW v_work_orders_detail AS
SELECT 
    wo.id,
    wo.numero_scheda,
    wo.stato,
    wo.data_appuntamento,
    wo.tipo_danno,
    wo.priorita,
    c.nome || ' ' || c.cognome AS cliente_nome,
    c.telefono AS cliente_telefono,
    c.email AS cliente_email,
    v.targa,
    v.marca || ' ' || v.modello AS veicolo,
    u1.username AS creato_da_username,
    u2.username AS approvato_da_username
FROM work_orders wo
LEFT JOIN customers c ON wo.customer_id = c.id
LEFT JOIN vehicles v ON wo.vehicle_id = v.id
LEFT JOIN users u1 ON wo.creato_da = u1.id
LEFT JOIN users u2 ON wo.approvato_da = u2.id;

-- Vista: Parti sotto scorta
CREATE VIEW v_parts_sotto_scorta AS
SELECT 
    p.id,
    p.codice,
    p.nome,
    p.categoria,
    p.quantita,
    p.quantita_minima,
    p.fornitore,
    p.posizione_magazzino,
    (p.quantita_minima - p.quantita) AS quantita_da_ordinare
FROM parts p
WHERE p.quantita <= p.quantita_minima
ORDER BY (p.quantita_minima - p.quantita) DESC;

-- Vista: Auto cortesia disponibili
CREATE VIEW v_courtesy_cars_disponibili AS
SELECT 
    cc.id,
    v.targa,
    v.marca,
    v.modello,
    cc.stato,
    cc.contratto_tipo,
    cc.data_scadenza_contratto
FROM courtesy_cars cc
JOIN vehicles v ON cc.vehicle_id = v.id
WHERE cc.stato = 'disponibile';

-- Vista: Scadenze pneumatici prossime
CREATE VIEW v_tires_scadenze AS
SELECT 
    t.id,
    v.targa,
    v.marca || ' ' || v.modello AS veicolo,
    c.nome || ' ' || c.cognome AS cliente,
    c.telefono,
    c.email,
    t.tipo_stagione,
    t.data_prossimo_cambio,
    JULIANDAY(t.data_prossimo_cambio) - JULIANDAY('now') AS giorni_alla_scadenza
FROM tires t
JOIN vehicles v ON t.vehicle_id = v.id
LEFT JOIN customers c ON v.customer_id = c.id
WHERE t.stato = 'depositati'
  AND t.data_prossimo_cambio IS NOT NULL
  AND JULIANDAY(t.data_prossimo_cambio) - JULIANDAY('now') <= 30
ORDER BY t.data_prossimo_cambio;

-- =====================================================
-- DATI INIZIALI
-- =====================================================

-- Inserimento utenti di default
INSERT INTO users (username, email, password_hash, ruolo, nome, cognome, attivo) VALUES
('admin', 'admin@garage.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH1lUKjmJe', 'ADMIN', 'Admin', 'Sistema', TRUE),
('gm.rossi', 'gm@garage.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH1lUKjmJe', 'GM', 'Mario', 'Rossi', TRUE),
('cmm.bianchi', 'cmm@garage.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH1lUKjmJe', 'CMM', 'Luigi', 'Bianchi', TRUE),
('cbm.verdi', 'cbm@garage.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGH1lUKjmJe', 'CBM', 'Giuseppe', 'Verdi', TRUE);

-- Password di default per tutti: "password123" (da cambiare al primo accesso)

-- Inserimento categorie parti di esempio
INSERT INTO parts (codice, nome, categoria, quantita, quantita_minima, prezzo_acquisto, prezzo_vendita, unita_misura) VALUES
('OIL-5W30', 'Olio motore 5W30', 'Lubrificanti', 50, 10, 15.00, 25.00, 'litri'),
('FILTER-OIL-001', 'Filtro olio universale', 'Filtri', 20, 5, 8.00, 15.00, 'pz'),
('BRAKE-PAD-001', 'Pastiglie freno anteriori', 'Freni', 15, 5, 25.00, 45.00, 'set'),
('SPARK-PLUG-001', 'Candele accensione', 'Motore', 30, 10, 5.00, 12.00, 'pz');

-- =====================================================
-- TRIGGER PER UPDATED_AT (PostgreSQL)
-- =====================================================
-- Per PostgreSQL, decommentare le seguenti righe:

/*
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_orders_updated_at BEFORE UPDATE ON work_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_order_activities_updated_at BEFORE UPDATE ON work_order_activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parts_updated_at BEFORE UPDATE ON parts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_order_parts_updated_at BEFORE UPDATE ON work_order_parts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tires_updated_at BEFORE UPDATE ON tires
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courtesy_cars_updated_at BEFORE UPDATE ON courtesy_cars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_car_assignments_updated_at BEFORE UPDATE ON car_assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_schedules_updated_at BEFORE UPDATE ON maintenance_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calendar_events_updated_at BEFORE UPDATE ON calendar_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
*/

-- =====================================================
-- FINE SCHEMA DATABASE
-- =====================================================