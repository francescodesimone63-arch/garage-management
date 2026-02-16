"""
Script per popolare gli stati intervento predefiniti nella tabella intervention_status_types
"""
import sys
import os

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.system_tables import InterventionStatusType

# Correggi URL per SQLite sincrono
DATABASE_URL = settings.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Stati intervento predefiniti
STATI_INTERVENTO = [
    {
        "codice": "preso_in_carico",
        "nome": "Preso in carico",
        "descrizione": "L'intervento è in lavorazione",
        "richiede_nota": False,
        "ordine": 1,
    },
    {
        "codice": "attesa_componente",
        "nome": "Attesa componente",
        "descrizione": "È stato richiesto l'acquisto di un componente o pezzo di ricambio durante la lavorazione",
        "richiede_nota": False,
        "ordine": 2,
    },
    {
        "codice": "sospeso",
        "nome": "Sospeso",
        "descrizione": "L'intervento è sospeso - richiede nota descrittiva del motivo",
        "richiede_nota": True,
        "ordine": 3,
    },
    {
        "codice": "concluso",
        "nome": "Concluso",
        "descrizione": "L'intervento è stato completato",
        "richiede_nota": False,
        "ordine": 4,
    },
]


def populate_intervention_status_types():
    """Popola gli stati intervento predefiniti"""
    db = SessionLocal()
    
    try:
        for stato_data in STATI_INTERVENTO:
            # Verifica se esiste già
            existing = db.query(InterventionStatusType).filter(
                InterventionStatusType.codice == stato_data["codice"]
            ).first()
            
            if existing:
                print(f"Stato '{stato_data['codice']}' già esistente, aggiornamento...")
                for key, value in stato_data.items():
                    setattr(existing, key, value)
            else:
                print(f"Creazione stato '{stato_data['codice']}'...")
                nuovo_stato = InterventionStatusType(**stato_data)
                db.add(nuovo_stato)
        
        db.commit()
        print("\n✅ Stati intervento popolati con successo!")
        
        # Mostra stati creati
        stati = db.query(InterventionStatusType).order_by(InterventionStatusType.ordine).all()
        print("\nStati intervento disponibili:")
        for stato in stati:
            nota_req = "⚠️ richiede nota" if stato.richiede_nota else ""
            print(f"  - [{stato.id}] {stato.codice}: {stato.nome} {nota_req}")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Errore: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_intervention_status_types()
