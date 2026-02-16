"""
Script per creare un utente admin
"""
import sys
from pathlib import Path

# Aggiungi il parent directory al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from getpass import getpass
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, sync_engine, Base
from app.core.security import get_password_hash
from app.models.user import User


def create_admin():
    """Crea un utente amministratore"""
    print("=" * 60)
    print("CREAZIONE UTENTE AMMINISTRATORE")
    print("=" * 60)
    
    # Richiedi informazioni
    email = input("\nEmail: ").strip()
    username = input("Username: ").strip()
    full_name = input("Nome completo: ").strip()
    password = getpass("Password: ")
    password_confirm = getpass("Conferma password: ")
    
    # Valida input
    if not all([email, username, full_name, password]):
        print("❌ Tutti i campi sono obbligatori!")
        return
    
    if password != password_confirm:
        print("❌ Le password non corrispondono!")
        return
    
    if len(password) < 6:
        print("❌ La password deve essere di almeno 6 caratteri!")
        return
    
    # Crea utente
    db = SessionLocal()
    
    try:
        # Verifica se esiste già
        existing = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing:
            print(f"❌ Un utente con email '{email}' o username '{username}' esiste già!")
            return
        
        # Crea nuovo admin
        admin = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "=" * 60)
        print("✓ AMMINISTRATORE CREATO CON SUCCESSO!")
        print("=" * 60)
        print(f"\nID: {admin.id}")
        print(f"Email: {admin.email}")
        print(f"Username: {admin.username}")
        print(f"Nome: {admin.full_name}")
        print(f"Ruolo: {admin.role}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRORE durante la creazione: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
