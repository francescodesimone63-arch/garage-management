#!/usr/bin/env python3
"""
Script per creare utente amministratore
"""
import sys
import os

# Aggiungi il path del backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
from app.core.database import Base

# Configurazione database
DATABASE_URL = "sqlite:///./backend/garage_management.db"

# Crea engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crea tutte le tabelle
Base.metadata.create_all(bind=engine)

# Crea sessione
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Verifica se admin esiste già
    existing_admin = db.query(User).filter(User.email == "admin@garage.local").first()
    
    if existing_admin:
        print("✅ Utente admin già esistente")
        print(f"   Email: {existing_admin.email}")
        print(f"   ID: {existing_admin.id}")
    else:
        # Crea nuovo admin
        admin = User(
            email="admin@garage.local",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Utente admin creato con successo!")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print(f"   ID: {admin.id}")
        
except Exception as e:
    print(f"❌ Errore: {e}")
    db.rollback()
finally:
    db.close()
