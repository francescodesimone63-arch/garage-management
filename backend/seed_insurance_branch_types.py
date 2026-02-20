"""
Script per popolare i rami sinistro predefiniti nella tabella insurance_branch_types
"""
import sys
import os

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.system_tables import InsuranceBranchType

# Correggi URL per SQLite sincrono
DATABASE_URL = settings.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Rami sinistro predefiniti
RAMI_SINISTRO = [
    {
        "codice": "rc",
        "nome": "Responsabilità Civile",
        "descrizione": "Copertura per danni a terzi",
        "attivo": True,
    },
    {
        "codice": "furto",
        "nome": "Furto",
        "descrizione": "Copertura per furto del veicolo",
        "attivo": True,
    },
    {
        "codice": "kasko_parziale",
        "nome": "Kasko Parziale",
        "descrizione": "Copertura parziale per danni al veicolo",
        "attivo": True,
    },
    {
        "codice": "kasko_totale",
        "nome": "Kasko Totale",
        "descrizione": "Copertura totale per danni al veicolo",
        "attivo": True,
    },
    {
        "codice": "cristalli",
        "nome": "Cristalli",
        "descrizione": "Copertura per rottura cristalli",
        "attivo": True,
    },
    {
        "codice": "incendio",
        "nome": "Incendio e Furto",
        "descrizione": "Copertura per incendio e furto",
        "attivo": True,
    },
    {
        "codice": "altro",
        "nome": "Altro",
        "descrizione": "Altro tipo di sinistro",
        "attivo": True,
    },
]


def seed_insurance_branch_types():
    """Popola la tabella insurance_branch_types con i rami predefiniti"""
    db = SessionLocal()
    
    try:
        # Verifica se i record esistono già
        count = db.query(InsuranceBranchType).count()
        if count > 0:
            print(f"✓ Tabella insurance_branch_types contiene già {count} record. Skip.")
            return
        
        # Inserisci i rami sinistro
        for ramo in RAMI_SINISTRO:
            existing = db.query(InsuranceBranchType).filter(
                InsuranceBranchType.codice == ramo["codice"]
            ).first()
            
            if not existing:
                new_ramo = InsuranceBranchType(**ramo)
                db.add(new_ramo)
                print(f"✓ Aggiunto ramo sinistro: {ramo['nome']}")
            else:
                print(f"⚠️  Ramo sinistro già esiste: {ramo['nome']}")
        
        db.commit()
        print(f"\n✓ Seed completato! Inseriti {len(RAMI_SINISTRO)} rami sinistro.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Errore durante il seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding insurance_branch_types...")
    seed_insurance_branch_types()
    print("✓ Fatto!")
