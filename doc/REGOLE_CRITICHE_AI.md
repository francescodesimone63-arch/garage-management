📌 REGOLE CRITICHE - DA RISPETTARE SEMPRE
================================================

🔴 DATABASE
-----------
✓ Il database è SEMPRE: /backend/garage.db
✗ NON usare: db.sqlite3, altri file .db, backup
✓ Unico database di lavoro

🔴 MODIFICHE AI DATI - AUTORIZZAZIONE OBBLIGATORIA
---------------------------------------------------
PRIMA di qualsiasi operazione, DEVO CHIEDERE PERMESSO per:
  ❌ Cancellazione di record (DELETE)
  ❌ Modifica di dati (UPDATE)  
  ❌ Reset/reinizializzazione del database
  ❌ Migrazioni che alterano schema
  ❌ Pulizia tabelle
  ❌ Rimozione di file database

✓ Operazioni CONSENTITE senza chiedere:
  ✓ SELECT / letture
  ✓ Verifiche integrità dati
  ✓ Backup (solo copia, no cancellazione originale)
  ✓ Esame log e errori

🔴 OPERAZIONI CONSENTITE CON AUTORIZZAZIONE
---------------------------------------------
Se l'utente autorizza esplicitamente:
  ✓ Eseguire seed_test_data.py (carica dati demo)
  ✓ Cancellare garage.db se autorizzato
  ✓ Rigenerare schema
  ✓ Modificare record
  
🔴 FLUSSO DECISIONALE
---------------------
1. Vedo errore database? 
   → Prima chiedo: "Posso ...?"
   → NON agisco autonomamente

2. Script seed fallisce?
   → Prima chiedo: "Posso correggerlo e ricaricare?"
   → NON cancello database

3. Schema incompatibile?
   → CHIEDO: "Devo ricrearlo da zero?"
   → NON elimino garage.db

🟢 QUESTA REGOLA È NON NEGOZIABILE
==================================
Non ci sono eccezioni. Sempre chiedere prima di modificare.
L'utente ha il pieno controllo dei dati.

Memorizzato il: 20 febbraio 2026
