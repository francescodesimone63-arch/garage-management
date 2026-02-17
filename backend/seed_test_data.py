#!/usr/bin/env python3
"""
Script per generare dati di test realistici nel database
"""

import sys
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, '/Users/francescodesimone/Sviluppo Python/garage-management/backend')

from app.core.config import settings
from app.models import User, UserRole
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderStatus, Priority
from app.core.security import get_password_hash


async def seed_database():
    """Popola il database con dati di test realistici"""
    # Crea engine asincrono
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
    )
    
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 1. Crea clienti (5-7)
            customers = [
                Customer(
                    tipo='privato',
                    nome="Marco",
                    cognome="Rossi",
                    email="marco.rossi@example.com",
                    cellulare="3201234567",
                    indirizzo="Via Roma 10, Milano",
                ),
                Customer(
                    tipo='privato',
                    nome="Luca",
                    cognome="Bianchi",
                    email="luca.bianchi@example.com",
                    cellulare="3209876543",
                    indirizzo="Via Milano 5, Torino",
                ),
                Customer(
                    tipo='azienda',
                    ragione_sociale="Transport SRL",
                    email="info@transportazienda.it",
                    telefono="0112345678",
                    indirizzo="Str. Industriale 20, Alessandria",
                    partita_iva="12345678900",
                ),
                Customer(
                    tipo='privato',
                    nome="Anna",
                    cognome="Ferrari",
                    email="anna.ferrari@gmail.com",
                    cellulare="3215555555",
                    indirizzo="Via Verdi 15, Genova",
                ),
                Customer(
                    tipo='privato',
                    nome="Giuseppe",
                    cognome="Neri",
                    email="giuseppe.neri@hotmail.com",
                    cellulare="3219999999",
                    indirizzo="Piazza Castello 3, Asti",
                ),
            ]
            session.add_all(customers)
            await session.flush()
            print(f"✅ Creati {len(customers)} clienti")
            
            # 2. Crea veicoli (10-12)
            vehicles = [
                Vehicle(
                    targa="AB123CD",
                    marca="Fiat",
                    modello="Punto",
                    anno=2020,
                    colore="Bianco",
                    telaio="ZFF1A6E3X2E111111",
                    cilindrata="1200 cc",
                    carburante="Benzina",
                    customer_id=customers[0].id,
                ),
                Vehicle(
                    targa="EF456GH",
                    marca="Volvo",
                    modello="XC60",
                    anno=2019,
                    colore="Nero",
                    telaio="YV1LS54DX22222222",
                    cilindrata="2000 cc",
                    carburante="Diesel",
                    customer_id=customers[1].id,
                ),
                Vehicle(
                    targa="IL789MN",
                    marca="Mercedes",
                    modello="Sprinter",
                    anno=2021,
                    colore="Bianco",
                    telaio="WDB9CCCC2C333333",
                    cilindrata="2100 cc",
                    carburante="Diesel",
                    customer_id=customers[2].id,
                ),
                Vehicle(
                    targa="OP012QR",
                    marca="BMW",
                    modello="X3",
                    anno=2020,
                    colore="Blu",
                    telaio="WBADT51451G444444",
                    cilindrata="1998 cc",
                    carburante="Benzina",
                    customer_id=customers[0].id,
                ),
                Vehicle(
                    targa="ST345UV",
                    marca="Audi",
                    modello="A4",
                    anno=2022,
                    colore="Grigio",
                    telaio="WAUZZZ8K5FD555555",
                    cilindrata="1800 cc",
                    carburante="Diesel",
                    customer_id=customers[3].id,
                ),
                Vehicle(
                    targa="WX678YZ",
                    marca="Toyota",
                    modello="Corolla",
                    anno=2021,
                    colore="Rosso",
                    telaio="JTNK78E36K5666666",
                    cilindrata="1600 cc",
                    carburante="Benzina",
                    customer_id=customers[4].id,
                ),
                Vehicle(
                    targa="AB901CD",
                    marca="Citroen",
                    modello="Jumper",
                    anno=2020,
                    colore="Bianco",
                    telaio="VNJPM1BJ7K7777777",
                    cilindrata="2000 cc",
                    carburante="Diesel",
                    customer_id=customers[2].id,
                ),
                Vehicle(
                    targa="EF234GH",
                    marca="Renault",
                    modello="Megane",
                    anno=2019,
                    colore="Nero",
                    telaio="VF1BA13J812888888",
                    cilindrata="1500 cc",
                    carburante="Benzina",
                    customer_id=customers[1].id,
                ),
                Vehicle(
                    targa="IJ567KL",
                    marca="Peugeot",
                    modello="3008",
                    anno=2021,
                    colore="Blu",
                    telaio="VF38NFJFL3A999999",
                    cilindrata="1600 cc",
                    carburante="Benzina",
                    customer_id=customers[3].id,
                ),
                Vehicle(
                    targa="MN890OP",
                    marca="Ford",
                    modello="Fiesta",
                    anno=2020,
                    colore="Arancione",
                    telaio="WF0BXXWPDA1000000",
                    cilindrata="1100 cc",
                    carburante="Benzina",
                    customer_id=customers[4].id,
                ),
            ]
            session.add_all(vehicles)
            await session.flush()
            print(f"✅ Creati {len(vehicles)} veicoli")
            
            # 3. Crea ordini di lavoro (15-20)
            now = datetime.now()
            statuses = [WorkOrderStatus.BOZZA, WorkOrderStatus.APPROVATA, WorkOrderStatus.COMPLETATA]
            
            work_orders = []
            descriptions = [
                "Cambio olio e filtri",
                "Riparazione freno anteriore",
                "Manutenzione revisione completa",
                "Sostituzione batteria",
                "Cambio gomme stagionali",
                "Allineamento e bilanciamento",
                "Riparazione serbatoio",
                "Sostituzione cinghia di distribuzione",
                "Pulizia radiatore",
                "Sostituzione spazzole tergicristallo",
                "Riparazione specchietto",
                "Cambio pastiglie freno",
                "Ricarica aria condizionata",
                "Diagnosi sistema motore",
                "Riparazione sportello",
            ]
            
            for i in range(15):
                vehicle = vehicles[i % len(vehicles)]
                customer = vehicle.customer
                days_ago = i * 2
                date = now - timedelta(days=days_ago)
                
                wo = WorkOrder(
                    numero_scheda=f"WO-2026-{1000 + i}",
                    customer_id=customer.id,
                    vehicle_id=vehicle.id,
                    data_compilazione=date,
                    data_creazione=date,
                    data_fine_prevista=date + timedelta(days=3),
                    valutazione_danno=descriptions[i % len(descriptions)],
                    stato=statuses[i % len(statuses)],
                    priorita=Priority.MEDIA,
                    costo_stimato=150.00 + (i * 50),
                    note=f"Ordine automatico di test #{i+1}",
                )
                work_orders.append(wo)
            
            session.add_all(work_orders)
            await session.flush()
            print(f"✅ Creati {len(work_orders)} ordini di lavoro")
            
            # Commit
            await session.commit()
            print("\n✅✅✅ Database poppolato con successo! ✅✅✅")
            print(f"  • Clienti: {len(customers)}")
            print(f"  • Veicoli: {len(vehicles)}")
            print(f"  • Ordini di lavoro: {len(work_orders)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Errore: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
