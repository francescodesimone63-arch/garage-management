#!/usr/bin/env python3
"""
Script per ricreattrivare pulitamente il database dai modelli SQLAlchemy.
Questo bypassa i problemi di migrazioni e crea le tabelle di base da zero.
"""
import os
import sys
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import Base
from sqlalchemy import inspect, text, create_engine


def init_database():
    """Crea il database da zero dai modelli SQLAlchemy."""
    
    db_path = Path(__file__).parent / "garage.db"
    db_url = f"sqlite:///{db_path}"
    alembic_version_table = "alembic_version"
    
    print(f"🗑️  Eliminando database precedente: {db_path}")
    if db_path.exists():
        db_path.unlink()
    
    print("📦 Importando modelli SQLAlchemy...")
    # Importa tutti i modelli per registrarli con Base
    from app.models import (  # noqa: F401
        User, Vehicle, Customer, WorkOrder,
        Intervention, Part, Tire,
        CourtesyCar, MaintenanceSchedule,
        Notification, CalendarEvent, Document,
        ActivityLog, GoogleOAuthToken,
        InsuranceBranchType, InterventionStatusType,
        Workshop, Permission, RolePermission,
        WorkOrderAudit, DamageType, CustomerType,
        WorkOrderStatusType, PriorityType
    )
    
    print(f"📝 Creando tabelle dal modello Base...")
    # Crea un engine sincronico per l'inizializzazione
    sync_engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Tabelle create")
    
    # Ispeziona il database per verificare
    with sync_engine.connect() as conn:
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Database inizializzato con {len(tables)} tabelle:")
        for table in sorted(tables):
            if table != alembic_version_table:
                col_count = len(inspector.get_columns(table))
                print(f"   ✓ {table} ({col_count} colonne)")
    
    sync_engine.dispose()
    print("\n✅ Database inizializzato con successo!")
    return True


if __name__ == "__main__":
    try:
        init_database()
        print("\n🎉 Pronto per l'esecuzione del seed script!")
    except Exception as e:
        print(f"\n❌ Errore: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
