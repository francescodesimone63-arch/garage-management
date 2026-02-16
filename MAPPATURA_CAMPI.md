# 🗺️ Mappatura Campi Backend → Frontend

## CUSTOMERS (Clienti)

| Frontend (Inglese) | Backend (Italiano) | Note |
|--------------------|--------------------| -----|
| first_name         | nome               | |
| last_name          | cognome            | |
| company_name       | ragione_sociale    | Solo per aziende |
| fiscal_code        | codice_fiscale     | Obbligatorio |
| vat_number         | partita_iva        | Solo per aziende |
| address            | indirizzo          | |
| city               | citta              | |
| postal_code        | cap                | |
| province           | provincia          | |
| phone              | telefono           | |
| mobile             | cellulare          | |
| email              | email              | ✅ Uguale |
| notes              | note               | |
| type               | tipo               | privato/azienda |

## VEHICLES (Veicoli)

| Frontend (Inglese) | Backend (Italiano) | Note |
|--------------------|--------------------| -----|
| customer_id        | customer_id        | ✅ Uguale |
| brand              | marca              | |
| model              | modello            | |
| year               | anno               | |
| license_plate      | targa              | |
| vin                | numero_telaio      | 17 caratteri |
| engine_code        | ❌ NON ESISTE      | Usare cilindrata? |
| fuel_type          | alimentazione      | benzina/diesel/gpl/metano/ibrido/elettrico |
| current_km         | km_attuali         | |
| registration_date  | data_immatricolazione | |
| displacement       | cilindrata         | |
| notes              | note               | |

## WORK ORDERS (Schede Lavoro)

| Frontend (Inglese) | Backend (Italiano) | Note |
|--------------------|--------------------| -----|
| customer_id        | customer_id        | ✅ Uguale |
| vehicle_id         | vehicle_id         | ✅ Uguale |
| work_order_number  | numero_ordine      | |
| opening_date       | data_ingresso      | |
| expected_delivery_date | data_prevista_consegna | |
| delivery_date      | data_consegna      | |
| km_in              | km_ingresso        | |
| description        | descrizione_lavori | |
| internal_notes     | note_interne       | |
| status             | stato              | |
| estimate_number    | preventivo_numero  | |
| estimate_amount    | preventivo_importo | |
| estimate_accepted  | preventivo_accettato | |
| final_amount       | importo_finale     | |
| assigned_to        | assigned_to        | ✅ Uguale |

**ATTENZIONE:**  
- ❌ `diagnosis` e `work_done` **NON ESISTONO** nel backend!
- Usare `descrizione_lavori` per tutto
- Usare `note_interne` per note aggiuntive

## PARTS (Ricambi)

Schema Parts è per WorkOrderParts (ricambi usati nelle schede)!
Non per inventario ricambi!

**Per WorkOrderParts:**
| Frontend | Backend |
|----------|---------|
| code     | codice  |
| description | descrizione |
| quantity | quantita |
| unit_price | prezzo_unitario |
| supplier | fornitore |

---

## ⚡ AZIONI IMMEDIATE:

1. ✅ Aggiornare `types/index.ts`
2. ✅ Aggiornare `CustomersPage.tsx`
3. ✅ Aggiornare `VehiclesPage.tsx`  
4. ✅ Aggiornare `WorkOrdersPage.tsx`
5. ⏸️ PartsPage - da sistemare dopo (problema diverso)

**Temp stimato:** 2-3 ore
