#!/usr/bin/env python3
"""
Script per resettare completamente il database
"""
import sys
import os
from pathlib import Path

# Aggiungi la directory parent al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.core.database import Base
from app.models import *  # Import tutti i modelli
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def reset_database():
    """Reset completo del database"""
    
    # Crea engine sincrono per le operazioni di reset
    DATABASE_URL = "sqlite:///./garage.db"
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("🗑️  Eliminazione tabelle esistenti...")
    Base.metadata.drop_all(bind=engine)
    
    print("📦 Creazione nuove tabelle...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database resettato con successo!")
    
    # Crea utente admin
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("\n👤 Creazione utente admin...")
        admin = User(
            email="admin@garage.local",
            username="admin",
            password_hash=get_password_hash("admin123"),
            nome="Admin",
            cognome="Garage",
            ruolo=UserRole.ADMIN,
            attivo=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Utente admin creato:")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print(f"   Ruolo: {admin.role}")
        
    except Exception as e:
        print(f"❌ Errore durante la creazione dell'admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        reset_database()
        print("\n✅ Reset completato con successo!")
    except Exception as e:
        print(f"\n❌ Errore durante il reset: {e}")
        sys.exit(1)
