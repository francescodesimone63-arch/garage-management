#!/usr/bin/env python3
"""
Script per pulire gli appuntamenti errati dal database
Cancella data_appuntamento, data_fine_prevista e google_event_id dalle schede lavori
"""
import os
import sys
import logging
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

# Disabilita logging SQLAlchemy
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Aggiungi backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.models.work_order import WorkOrder

def cleanup_appointments(force=False):
    """Cancella gli appuntamenti errati dal database
    
    Args:
        force: Se True, cancella senza chiedere conferma
    """
    
    # Crea connessione - converti da aiosqlite a sqlite
    db_url = settings.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")
    engine = create_engine(db_url)
    
    try:
        with Session(engine) as session:
            # 1. Mostra i record con appuntamenti
            query = select(WorkOrder).where(WorkOrder.data_appuntamento.isnot(None))
            rows_with_appointments = session.execute(query).scalars().all()
            
            print(f"\n📅 Schede lavori con appuntamenti: {len(rows_with_appointments)}\n")
            
            for row in rows_with_appointments:
                print(f"  ID: {row.id}")
                print(f"  Numero scheda: {row.numero_scheda}")
                print(f"  Data appuntamento: {row.data_appuntamento}")
                print(f"  Data fine prevista: {row.data_fine_prevista}")
                print(f"  Google Event ID: {row.google_event_id}")
                print()
            
            # 2. Chiedi conferma se non in force mode
            if rows_with_appointments:
                if not force:
                    confirm = input(f"❓ Cancellare appuntamenti per {len(rows_with_appointments)} schede? (yes/no): ").strip().lower()
                else:
                    confirm = "yes"
                
                if confirm == "yes":
                    # 3. Resetta i campi
                    stmt = update(WorkOrder).where(
                        WorkOrder.data_appuntamento.isnot(None)
                    ).values(
                        data_appuntamento=None,
                        data_fine_prevista=None,
                        google_event_id=None
                    )
                    
                    result = session.execute(stmt)
                    session.commit()
                    
                    print(f"\n✅ Appuntamenti cancellati: {result.rowcount} schede")
                else:
                    print("\n❌ Operazione annullata")
            else:
                print("✨ Nessun appuntamento da cancellare!")
                
    except Exception as e:
        print(f"\n❌ Errore: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Se esiste --force, cancella senza chiedere
    force = "--force" in sys.argv
    cleanup_appointments(force)
