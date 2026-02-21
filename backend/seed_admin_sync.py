#!/usr/bin/env python3
"""
Seed script per creare l'utente admin
Uses sync engine since seed_admin.py tries async
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings

# Create sync session
sync_db_url = "sqlite:///./garage.db"
sync_engine = create_engine(sync_db_url, echo=False)
SyncSession = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
db = SyncSession()

try:
    # Check if admin exists
    admin_exists = db.query(User).filter(User.email == "admin@garage.local").first()
    
    if admin_exists:
        print("✅ Admin user already exists")
        sys.exit(0)
    
    # Create admin user
    admin = User(
        username="admin",
        email="admin@garage.local",
        password_hash=get_password_hash("admin123"),
        ruolo=UserRole.ADMIN,
        nome="Admin",
        cognome="System",
        attivo=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✅ Admin user created successfully")
    print(f"   Email: admin@garage.local")
    print(f"   Password: admin123")
    print(f"   ID: {admin.id}")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error creating admin user: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
