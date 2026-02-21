"""
Script per popolare le tabelle RBAC (permissions e role_permissions) con valori iniziali
Seed: 54 permessi raggruppati per categoria
Default: Tutti i permessi assegnati in base al ruolo
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.rbac import Permission, RolePermission
from app.models.user import UserRole

# Correggi URL per SQLite sincrono
DATABASE_URL = settings.database_url.replace("sqlite+aiosqlite:///", "sqlite:///")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Definizione completa di tutti i permessi per categoria
PERMISSIONS_CATALOG = {
    "Sistema": [
        {"codice": "system.manage_users", "nome": "Gestione utenti", "descrizione": "Crea, modifica, elimina utenti"},
        {"codice": "system.manage_roles", "nome": "Configurazione permessi", "descrizione": "Configura permessi per ruolo"},
        {"codice": "system.manage_workshops", "nome": "Gestione officine", "descrizione": "Crea e gestisci officine"},
        {"codice": "system.settings", "nome": "Impostazioni sistema", "descrizione": "Configurazioni globali dell'app"},
    ],
    "Clienti": [
        {"codice": "customers.view", "nome": "Visualizza clienti", "descrizione": "Visualizza lista e dettagli clienti"},
        {"codice": "customers.create", "nome": "Crea cliente", "descrizione": "Crea nuovo cliente"},
        {"codice": "customers.edit", "nome": "Modifica cliente", "descrizione": "Modifica dati cliente"},
        {"codice": "customers.delete", "nome": "Elimina cliente", "descrizione": "Elimina cliente dal sistema"},
    ],
    "Veicoli": [
        {"codice": "vehicles.view", "nome": "Visualizza veicoli", "descrizione": "Visualizza lista e dettagli veicoli"},
        {"codice": "vehicles.create", "nome": "Crea veicolo", "descrizione": "Registra nuovo veicolo"},
        {"codice": "vehicles.edit", "nome": "Modifica veicolo", "descrizione": "Modifica dati veicolo"},
        {"codice": "vehicles.delete", "nome": "Elimina veicolo", "descrizione": "Elimina veicolo dal sistema"},
    ],
    "Schede Lavoro": [
        {"codice": "work_orders.view", "nome": "Visualizza schede", "descrizione": "Visualizza tutte le schede di lavoro"},
        {"codice": "work_orders.view_own", "nome": "Visualizza proprie schede", "descrizione": "Visualizza solo proprie schede"},
        {"codice": "work_orders.create", "nome": "Crea scheda", "descrizione": "Crea nuova scheda di lavoro"},
        {"codice": "work_orders.edit", "nome": "Modifica scheda", "descrizione": "Modifica scheda di lavoro"},
        {"codice": "work_orders.delete", "nome": "Elimina scheda", "descrizione": "Elimina scheda di lavoro"},
        {"codice": "work_orders.approve", "nome": "Approva scheda", "descrizione": "Approva scheda (BOZZA → APPROVATA)"},
        {"codice": "work_orders.start_work", "nome": "Avvia lavorazione", "descrizione": "Avvia lavorazione (APPROVATA → IN_LAVORAZIONE)"},
        {"codice": "work_orders.complete", "nome": "Completa scheda", "descrizione": "Completa scheda (IN_LAVORAZIONE → COMPLETATA)"},
        {"codice": "work_orders.cancel", "nome": "Annulla scheda", "descrizione": "Annulla scheda di lavoro"},
        {"codice": "work_orders.reopen", "nome": "Riapri scheda", "descrizione": "Riapri scheda completata"},
    ],
    "Interventi": [
        {"codice": "interventions.view", "nome": "Visualizza interventi", "descrizione": "Visualizza interventi"},
        {"codice": "interventions.create", "nome": "Crea intervento", "descrizione": "Crea nuovo intervento"},
        {"codice": "interventions.edit", "nome": "Modifica intervento", "descrizione": "Modifica intervento"},
        {"codice": "interventions.update_status", "nome": "Aggiorna stato", "descrizione": "Aggiorna stato intervento"},
    ],
    "Magazzino": [
        {"codice": "parts.view", "nome": "Visualizza ricambi", "descrizione": "Visualizza ricambi disponibili"},
        {"codice": "parts.create", "nome": "Crea ricambio", "descrizione": "Registra nuovo ricambio"},
        {"codice": "parts.edit", "nome": "Modifica ricambio", "descrizione": "Modifica ricambio"},
        {"codice": "parts.delete", "nome": "Elimina ricambio", "descrizione": "Elimina ricambio dal magazzino"},
    ],
    "Pneumatici": [
        {"codice": "tires.view", "nome": "Visualizza pneumatici", "descrizione": "Visualizza pneumatici"},
        {"codice": "tires.manage", "nome": "Gestisci pneumatici", "descrizione": "Crea, modifica, elimina pneumatici"},
    ],
    "Auto Cortesia": [
        {"codice": "courtesy_cars.view", "nome": "Visualizza auto cortesia", "descrizione": "Visualizza auto cortesia"},
        {"codice": "courtesy_cars.manage", "nome": "Gestisci auto cortesia", "descrizione": "Crea, modifica, elimina auto cortesia"},
        {"codice": "courtesy_cars.assign", "nome": "Assegna auto cortesia", "descrizione": "Assegna auto a cliente"},
    ],
    "Calendario": [
        {"codice": "calendar.view", "nome": "Visualizza calendario", "descrizione": "Visualizza calendario"},
        {"codice": "calendar.manage", "nome": "Gestisci calendario", "descrizione": "Crea, modifica, elimina eventi"},
    ],
    "Manutenzioni": [
        {"codice": "maintenance.view", "nome": "Visualizza scadenzario", "descrizione": "Visualizza manutenzioni"},
        {"codice": "maintenance.manage", "nome": "Gestisci manutenzioni", "descrizione": "Crea, modifica, elimina manutenzioni"},
    ],
    "Dashboard": [
        {"codice": "dashboard.view", "nome": "Visualizza dashboard", "descrizione": "Accesso a dashboard"},
        {"codice": "dashboard.stats", "nome": "Visualizza statistiche", "descrizione": "Visualizza statistiche complete"},
    ],
    "Documenti": [
        {"codice": "documents.view", "nome": "Visualizza documenti", "descrizione": "Visualizza documenti"},
        {"codice": "documents.upload", "nome": "Carica documenti", "descrizione": "Carica e crea documenti"},
        {"codice": "activity_logs.view", "nome": "Visualizza log", "descrizione": "Visualizza log attività"},
    ],
}

# Mapping: role -> lista di permission codici concessi (True) e negati (False)
# Per semplificare, assegno i permessi logici a ogni ruolo
ROLE_PERMISSION_DEFAULTS = {
    UserRole.ADMIN.value: {
        # ADMIN ha TUTTI i permessi
        "all": True,  # Marker speciale: assegna tutti i permessi
    },
    UserRole.GENERAL_MANAGER.value: {  # GM
        # GM gestisce praticamente tutto tranne sistema
        "denied": ["system.manage_users", "system.manage_roles", "system.manage_workshops", "system.settings"],
    },
    UserRole.GM_ASSISTANT.value: {  # GMA
        # GMA ha permessi ridotti, supporta GM
        "granted": [
            "customers.view", "customers.create", "customers.edit",
            "vehicles.view", "vehicles.create", "vehicles.edit",
            "work_orders.view", "work_orders.create", "work_orders.edit",
            "interventions.view", "interventions.create", "interventions.edit",
            "dashboard.view", "documents.view",
        ],
    },
    UserRole.FRONTEND_MANAGER.value: {  # FEM
        # FEM: accettazione veicoli, supporto customers
        "granted": [
            "customers.view", "customers.create", "customers.edit",
            "vehicles.view", "vehicles.create",
            "work_orders.view", "work_orders.create",
            "courtesy_cars.view", "courtesy_cars.assign",
            "dashboard.view",
        ],
    },
    UserRole.CMM.value: {  # Capo Meccanica
        # CMM: gestisce officina meccanica
        "granted": [
            "work_orders.view", "work_orders.start_work", "work_orders.complete",
            "interventions.view", "interventions.create", "interventions.edit", "interventions.update_status",
            "parts.view", "parts.create", "parts.edit",
            "dashboard.view", "work_orders.view_own",
        ],
    },
    UserRole.CBM.value: {  # Capo Carrozzeria
        # CBM: gestisce officina carrozzeria
        "granted": [
            "work_orders.view", "work_orders.start_work", "work_orders.complete",
            "interventions.view", "interventions.create", "interventions.edit", "interventions.update_status",
            "parts.view", "parts.create", "parts.edit",
            "dashboard.view", "work_orders.view_own",
        ],
    },
    UserRole.WORKSHOP.value: {  # Operatore Meccanica
        # WORKSHOP: operatore di officina (minori permessi)
        "granted": [
            "work_orders.view_own",
            "interventions.view", "interventions.edit", "interventions.update_status",
            "parts.view",
            "dashboard.view",
        ],
    },
    UserRole.BODYSHOP.value: {  # Operatore Carrozzeria
        # BODYSHOP: operatore carrozzeria (minori permessi)
        "granted": [
            "work_orders.view_own",
            "interventions.view", "interventions.edit", "interventions.update_status",
            "parts.view",
            "dashboard.view",
        ],
    },
}


def seed_permissions_and_roles():
    """Popola le tabelle permissions e role_permissions con dati iniziali"""
    db = SessionLocal()
    
    try:
        # Step 1: Crea i permessi
        print("🌱 Seeding permissions catalog...")
        total_permissions = 0
        
        for categoria, perms in PERMISSIONS_CATALOG.items():
            for perm_data in perms:
                existing = db.query(Permission).filter(
                    Permission.codice == perm_data["codice"]
                ).first()
                
                if not existing:
                    new_perm = Permission(
                        codice=perm_data["codice"],
                        nome=perm_data["nome"],
                        categoria=categoria,
                        descrizione=perm_data.get("descrizione"),
                        attivo=True,
                    )
                    db.add(new_perm)
                    print(f"  ✓ Permesso: {perm_data['codice']}")
                    total_permissions += 1
        
        db.commit()
        print(f"✅ {total_permissions} permessi creati\n")
        
        # Step 2: Crea i mappamenti role-permission
        print("🌱 Seeding role-permission mappings...")
        total_mappings = 0
        
        all_permissions = db.query(Permission).all()
        all_perm_codici = {p.codice: p for p in all_permissions}
        
        for ruolo_value, perm_config in ROLE_PERMISSION_DEFAULTS.items():
            print(f"\n  👤 Ruolo: {ruolo_value}")
            
            if perm_config.get("all") is True:
                # ADMIN: tutti i permessi concessi
                for perm_codice, perm in all_perm_codici.items():
                    existing = db.query(RolePermission).filter(
                        RolePermission.ruolo == ruolo_value,
                        RolePermission.permission_id == perm.id,
                    ).first()
                    
                    if not existing:
                        new_mapping = RolePermission(
                            ruolo=ruolo_value,
                            permission_id=perm.id,
                            granted=True,
                        )
                        db.add(new_mapping)
                        total_mappings += 1
                print(f"    ✅ Tutti i {len(all_perm_codici)} permessi concessi")
            
            else:
                # Ruoli con permessi specifici
                granted_list = perm_config.get("granted", [])
                denied_list = perm_config.get("denied", [])
                
                for perm_codice, perm in all_perm_codici.items():
                    existing = db.query(RolePermission).filter(
                        RolePermission.ruolo == ruolo_value,
                        RolePermission.permission_id == perm.id,
                    ).first()
                    
                    if not existing:
                        # Decidi se concedere o negare
                        if granted_list:
                            # Whitelist model: solo i permessi in granted_list
                            granted = perm_codice in granted_list
                        elif denied_list:
                            # Blacklist model: tutti tranne i denied_list
                            granted = perm_codice not in denied_list
                        else:
                            granted = False
                        
                        new_mapping = RolePermission(
                            ruolo=ruolo_value,
                            permission_id=perm.id,
                            granted=granted,
                        )
                        db.add(new_mapping)
                        total_mappings += 1
                
                granted_count = len(granted_list) if granted_list else (len(all_perm_codici) - len(denied_list))
                print(f"    ✅ {granted_count} permessi concessi")
        
        db.commit()
        print(f"\n✅ {total_mappings} mappamenti ruolo-permesso creati")
        print("\n✨ Seed RBAC completato con successo!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Errore durante il seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding RBAC system (permissions + role_permissions)...\n")
    seed_permissions_and_roles()
