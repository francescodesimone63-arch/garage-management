"""
Script per popolare il database con dati iniziali di test
"""
import sys
from pathlib import Path

# Aggiungi il parent directory al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, sync_engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder


def create_tables():
    """Crea tutte le tabelle nel database"""
    print("Creazione tabelle...")
    Base.metadata.create_all(bind=sync_engine)
    print("✓ Tabelle create")


def seed_users(db: Session):
    """Crea utenti di test"""
    print("\nCreazione utenti...")
    
    users = [
        {
            "email": "admin@garage.com",
            "username": "admin",
            "nome": "Admin",
            "cognome": "System",
            "password_hash": get_password_hash("admin123"),
            "ruolo": "ADMIN",
            "attivo": True
        },
        {
            "email": "gm@garage.com",
            "username": "gm",
            "nome": "General",
            "cognome": "Manager",
            "password_hash": get_password_hash("gm123"),
            "ruolo": "GM",
            "attivo": True
        },
        {
            "email": "officina@garage.com",
            "username": "officina",
            "nome": "Car Mechanic",
            "cognome": "Manager",
            "password_hash": get_password_hash("officina123"),
            "ruolo": "CMM",
            "attivo": True
        },
        {
            "email": "carrozzeria@garage.com",
            "username": "carrozzeria",
            "nome": "Car Body",
            "cognome": "Manager",
            "password_hash": get_password_hash("carrozzeria123"),
            "ruolo": "CBM",
            "attivo": True
        }
    ]
    
    for user_data in users:
        # Verifica se esiste già
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            print(f"  ✓ Creato utente: {user_data['username']} (password: {user_data['email'].split('@')[0]}123)")
    
    db.commit()
    print("✓ Utenti creati")


def seed_customers(db: Session):
    """Crea clienti di test"""
    print("\nCreazione clienti...")
    
    customers = [
        {
            "nome": "Mario",
            "cognome": "Rossi",
            "email": "mario.rossi@email.com",
            "telefono": "+39 333 1234567",
            "indirizzo": "Via Roma 123",
            "citta": "Milano",
            "cap": "20100",
            "codice_fiscale": "RSSMRA80A01F205X"
        },
        {
            "nome": "Luigi",
            "cognome": "Bianchi",
            "email": "luigi.bianchi@email.com",
            "telefono": "+39 333 2345678",
            "indirizzo": "Corso Italia 45",
            "citta": "Milano",
            "cap": "20122",
            "codice_fiscale": "BNCLGU75B15F205Z"
        },
        {
            "nome": "Giuseppe",
            "cognome": "Verdi",
            "email": "giuseppe.verdi@email.com",
            "telefono": "+39 333 3456789",
            "indirizzo": "Piazza Duomo 1",
            "citta": "Milano",
            "cap": "20121",
            "codice_fiscale": "VRDGPP85C20F205W",
            "ragione_sociale": "Verdi SRL",
            "partita_iva": "IT12345678901"
        }
    ]
    
    for customer_data in customers:
        # Verifica se esiste già
        existing = db.query(Customer).filter(Customer.email == customer_data["email"]).first()
        if not existing:
            customer = Customer(**customer_data)
            db.add(customer)
            print(f"  ✓ Creato cliente: {customer_data['nome']} {customer_data['cognome']}")
    
    db.commit()
    print("✓ Clienti creati")


def seed_vehicles(db: Session):
    """Crea veicoli di test"""
    print("\nCreazione veicoli...")
    
    # Ottieni i clienti
    customers = db.query(Customer).all()
    
    if not customers:
        print("  ⚠ Nessun cliente trovato, impossibile creare veicoli")
        return
    
    vehicles = [
        {
            "customer_id": customers[0].id,
            "targa": "AB123CD",
            "telaio": "WAUZZZ8V5BA123456",
            "marca": "Audi",
            "modello": "A4",
            "anno": 2020,
            "km_attuali": 45000
        },
        {
            "customer_id": customers[0].id,
            "targa": "EF456GH",
            "telaio": "WVWZZZ1KZ9W123456",
            "marca": "Volkswagen",
            "modello": "Golf",
            "anno": 2019,
            "km_attuali": 62000
        },
        {
            "customer_id": customers[1].id,
            "targa": "IJ789KL",
            "telaio": "WBA3A5C50FK123456",
            "marca": "BMW",
            "modello": "Serie 3",
            "anno": 2021,
            "km_attuali": 28000
        },
        {
            "customer_id": customers[2].id,
            "targa": "MN012OP",
            "telaio": "ZFA25000007123456",
            "marca": "Fiat",
            "modello": "Ducato",
            "anno": 2018,
            "km_attuali": 98000
        }
    ]
    
    for vehicle_data in vehicles:
        # Verifica se esiste già
        existing = db.query(Vehicle).filter(Vehicle.targa == vehicle_data["targa"]).first()
        if not existing:
            vehicle = Vehicle(**vehicle_data)
            db.add(vehicle)
            print(f"  ✓ Creato veicolo: {vehicle_data['targa']} - {vehicle_data['marca']} {vehicle_data['modello']}")
    
    db.commit()
    print("✓ Veicoli creati")


def seed_work_orders(db: Session):
    """Crea ordini di lavoro di test"""
    print("\nCreazione ordini di lavoro...")
    
    # Ottieni veicoli e utenti
    vehicles = db.query(Vehicle).all()
    users = db.query(User).all()
    
    if not vehicles or not users:
        print("  ⚠ Veicoli o utenti non trovati, impossibile creare ordini")
        return
    
    # Trova l'utente admin/gm per created_by
    creator = next((u for u in users if u.ruolo in ['ADMIN', 'GM']), users[0])
    
    # Ottieni i customer_id dai veicoli
    work_orders = [
        {
            "numero_scheda": "WO001",
            "customer_id": vehicles[0].customer_id,
            "vehicle_id": vehicles[0].id,
            "data_appuntamento": datetime.now() + timedelta(days=2),
            "stato": "BOZZA",
            "priorita": "MEDIA",
            "valutazione_danno": "Tagliando completo",
            "creato_da": creator.id,
            "costo_stimato": 350.00
        },
        {
            "numero_scheda": "WO002",
            "customer_id": vehicles[1].customer_id,
            "vehicle_id": vehicles[1].id,
            "data_appuntamento": datetime.now() + timedelta(days=5),
            "stato": "BOZZA",
            "priorita": "ALTA",
            "valutazione_danno": "Sostituzione freni anteriori",
            "creato_da": creator.id,
            "costo_stimato": 280.00
        },
        {
            "numero_scheda": "WO003",
            "customer_id": vehicles[2].customer_id,
            "vehicle_id": vehicles[2].id,
            "data_appuntamento": datetime.now() + timedelta(days=7),
            "stato": "APPROVATA",
            "priorita": "MEDIA",
            "valutazione_danno": "Riparazione paraurti posteriore",
            "creato_da": creator.id,
            "approvato_da": creator.id,
            "costo_stimato": 550.00
        }
    ]
    
    for wo_data in work_orders:
        work_order = WorkOrder(**wo_data)
        db.add(work_order)
        print(f"  ✓ Creato ordine: {wo_data['numero_scheda']} - {wo_data['valutazione_danno'][:30]}...")
    
    db.commit()
    print("✓ Ordini di lavoro creati")


def main():
    """Funzione principale per il seeding"""
    print("=" * 60)
    print("SEED DATABASE - Garage Management System")
    print("=" * 60)
    
    # Crea le tabelle
    create_tables()
    
    # Crea sessione database
    db = SessionLocal()
    
    try:
        # Esegui il seeding
        seed_users(db)
        seed_customers(db)
        seed_vehicles(db)
        seed_work_orders(db)
        
        print("\n" + "=" * 60)
        print("✓ SEEDING COMPLETATO CON SUCCESSO!")
        print("=" * 60)
        print("\nCredenziali utenti di test:")
        print("-" * 60)
        print("Admin:       admin@garage.com / admin123")
        print("GM:          gm@garage.com / gm123")
        print("Officina:    officina@garage.com / officina123")
        print("Carrozzeria: carrozzeria@garage.com / carrozzeria123")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRORE durante il seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
