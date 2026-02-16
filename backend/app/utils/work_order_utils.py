"""
Utility functions for work order management
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.work_order import WorkOrder


def generate_numero_scheda(db: Session, data_compilazione: datetime) -> str:
    """
    Genera il numero della scheda lavoro in formato YYZZ-XXXX
    
    Formato:
    - YY: mese della data compilazione (01-12)
    - ZZ: anno della data compilazione (es. 26 per 2026)
    - XXXX: numero progressivo per mese (0001, 0002, etc.)
    
    Esempio: 0226-0001 per il primo ordine di febbraio 2026
    
    Args:
        db: SQLAlchemy database session
        data_compilazione: Data di compilazione della scheda
    
    Returns:
        str: Numero scheda generato (es. "0226-0001")
    """
    # Estrai mese e anno
    month = data_compilazione.month
    year = data_compilazione.year % 100  # Prendi ultime 2 cifre dell'anno
    
    # Formatta il prefisso YYZZ
    prefix = f"{month:02d}{year:02d}"
    
    # Calcola l'inizio e la fine del mese
    start_of_month = datetime(data_compilazione.year, data_compilazione.month, 1)
    # Primo giorno del mese successivo meno un giorno
    if month == 12:
        end_of_month = datetime(data_compilazione.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_of_month = datetime(data_compilazione.year, month + 1, 1) - timedelta(seconds=1)
    
    # Conta schede ordini in questo mese/anno
    count = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.data_compilazione >= start_of_month,
        WorkOrder.data_compilazione <= end_of_month
    ).scalar()
    
    # Calcola il prossimo numero progressivo
    next_counter = count + 1
    
    # Formatta il numero progressivo con 4 cifre
    numero_scheda = f"{prefix}-{next_counter:04d}"
    
    print(f"🔍 DEBUG generate_numero_scheda: prefix={prefix}, count={count}, next_counter={next_counter}, numero_scheda={numero_scheda}")
    
    return numero_scheda
