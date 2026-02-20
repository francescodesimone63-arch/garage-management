"""
Script per aggiungere campi sinistro alla tabella work_orders
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings

# SQLite sincrono
DATABASE_URL = settings.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")

engine = create_engine(DATABASE_URL, echo=True)

# SQL per aggiungere i campi (SQLite friendly)
SQL_COMMANDS = [
    # Creare la tabella di lookup per i rami sinistro
    """
    CREATE TABLE IF NOT EXISTS insurance_branch_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) UNIQUE NOT NULL,
        codice VARCHAR(30) UNIQUE NOT NULL,
        descrizione TEXT,
        attivo BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # Aggiungere i campi sinistro a work_orders (con controlli)
    """
    ALTER TABLE work_orders
    ADD COLUMN sinistro BOOLEAN DEFAULT 0;
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN ramo_sinistro_id INTEGER REFERENCES insurance_branch_types(id);
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN legale TEXT;
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN autorita TEXT;
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN numero_sinistro VARCHAR(50);
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN compagnia_sinistro VARCHAR(200);
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN compagnia_debitrice_sinistro VARCHAR(200);
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN scoperto DECIMAL(10, 2);
    """,
    """
    ALTER TABLE work_orders
    ADD COLUMN perc_franchigia DECIMAL(5, 2);
    """,
    
    # Rimuovere il campo note
    "DROP TABLE IF EXISTS work_orders_backup;",
    """
    CREATE TABLE work_orders_backup AS 
    SELECT id, numero_scheda, customer_id, vehicle_id, data_creazione, data_compilazione, 
           data_appuntamento, data_fine_prevista, data_completamento, stato, priorita, 
           valutazione_danno, sinistro, ramo_sinistro_id, legale, autorita, numero_sinistro,
           compagnia_sinistro, compagnia_debitrice_sinistro, scoperto, perc_franchigia,
           creato_da, approvato_da, auto_cortesia_id, costo_stimato, costo_finale,
           google_event_id, created_at, updated_at
    FROM work_orders;
    """,
]

def apply_schema_updates():
    """Applica gli aggiornamenti dello schema"""
    conn = engine.connect()
    
    try:
        for i, sql in enumerate(SQL_COMMANDS, 1):
            try:
                conn.execute(text(sql))
                print(f"✓ Comando {i} eseguito")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print(f"⚠️  Comando {i} saltato (già esiste)")
                else:
                    print(f"❌ Errore comando {i}: {e}")
                    raise
        
        conn.commit()
        print("\n✓ Schema aggiornato con successo!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Errore: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Aggiornamento schema database...")
    apply_schema_updates()
