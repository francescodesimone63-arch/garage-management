"""
Script per popolare le tabelle di sistema con dati iniziali
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.system_tables import WorkOrderStatusType, PriorityType, DamageType, CustomerType


def seed_system_tables():
    db = SessionLocal()
    
    print("Popolamento tabelle di sistema...")
    
    # Seed Work Order Status Types
    statuses = [
        {"nome": "Bozza", "descrizione": "Scheda in bozza", "attivo": True},
        {"nome": "Approvata", "descrizione": "Scheda approvata", "attivo": True},
        {"nome": "In_lavorazione", "descrizione": "Lavoro in corso", "attivo": True},
        {"nome": "Completata", "descrizione": "Lavoro completato", "attivo": True},
        {"nome": "Annullata", "descrizione": "Scheda annullata", "attivo": True},
    ]

    for s in statuses:
        existing = db.query(WorkOrderStatusType).filter(WorkOrderStatusType.nome == s["nome"]).first()
        if not existing:
            db.add(WorkOrderStatusType(**s))
            print(f"  ✓ Creato stato: {s['nome']}")

    # Seed Priority Types
    priorities = [
        {"nome": "bassa", "descrizione": "Priorità bassa", "attivo": True},
        {"nome": "media", "descrizione": "Priorità media", "attivo": True},
        {"nome": "alta", "descrizione": "Priorità alta", "attivo": True},
        {"nome": "urgente", "descrizione": "Priorità urgente", "attivo": True},
    ]

    for p in priorities:
        existing = db.query(PriorityType).filter(PriorityType.nome == p["nome"]).first()
        if not existing:
            db.add(PriorityType(**p))
            print(f"  ✓ Creata priorità: {p['nome']}")

    # Seed Damage Types
    damages = [
        {"nome": "Grandine", "descrizione": "Danni da grandine", "attivo": True},
        {"nome": "Incidente", "descrizione": "Danni da incidente", "attivo": True},
        {"nome": "Usura", "descrizione": "Danni da usura", "attivo": True},
        {"nome": "Altro", "descrizione": "Altri danni", "attivo": True},
    ]

    for d in damages:
        existing = db.query(DamageType).filter(DamageType.nome == d["nome"]).first()
        if not existing:
            db.add(DamageType(**d))
            print(f"  ✓ Creato tipo danno: {d['nome']}")

    # Seed Customer Types
    customer_types = [
        {"nome": "Privato", "descrizione": "Cliente privato", "attivo": True},
        {"nome": "Azienda", "descrizione": "Cliente aziendale", "attivo": True},
        {"nome": "Assicurazione", "descrizione": "Compagnia assicurativa", "attivo": True},
    ]

    for c in customer_types:
        existing = db.query(CustomerType).filter(CustomerType.nome == c["nome"]).first()
        if not existing:
            db.add(CustomerType(**c))
            print(f"  ✓ Creato tipo cliente: {c['nome']}")

    db.commit()
    db.close()
    print("\n✅ Dati di sistema popolati con successo!")


if __name__ == "__main__":
    seed_system_tables()
