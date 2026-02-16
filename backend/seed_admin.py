#!/usr/bin/env python3
"""
Script per creare utente admin di default nel database
"""
import sys
sys.path.insert(0, '/Users/francescodesimone/Sviluppo Python/garage-management/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.core import security
from app.core.config import settings

# Create database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Check if admin exists
admin_exists = db.query(User).filter(User.email == "admin@garage.local").first()

if admin_exists:
    print("✅ Admin already exists!")
    sys.exit(0)

# Create admin user
admin = User(
    username="admin",
    email="admin@garage.local",
    password_hash=security.get_password_hash("admin123"),
    ruolo=UserRole.ADMIN,
    nome="Admin",
    cognome="User",
    attivo=True
)

db.add(admin)
db.commit()
db.refresh(admin)

print(f"✅ Admin created successfully!")
print(f"   - Email: admin@garage.local")
print(f"   - Username: admin")
print(f"   - Password: admin123")
print(f"   - Role: ADMIN")
print(f"   - ID: {admin.id}")

db.close()
