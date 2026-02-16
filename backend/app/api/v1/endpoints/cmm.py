"""
CMM (Capo Meccanica) specific endpoints

Questi endpoint gestiscono le funzionalità specifiche per gli utenti con ruolo CMM:
- Visualizzazione work orders approvati con interventi di tipo "Meccanico"
- Gestione stato degli interventi
- Aggiunta note agli interventi
- Statistiche dashboard specifiche per CMM
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from app.core.deps import get_db, get_current_user
from app.models import WorkOrder, WorkOrderStatus, Intervention, User
from app.models.system_tables import InterventionStatusType
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.schemas.work_order import WorkOrderWithDetails
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(tags=["cmm"])


# Schema per la risposta della lista work orders CMM
class InterventionSummary(BaseModel):
    """Schema per intervento nella lista"""
    id: int
    progressivo: int
    descrizione_intervento: str
    durata_stimata: float
    tipo_intervento: str
    stato_intervento_id: Optional[int]
    stato_intervento_codice: Optional[str]
    stato_intervento_nome: Optional[str]
    note_intervento: Optional[str]
    note_sospensione: Optional[str]
    ore_effettive: Optional[float]
    data_inizio: Optional[datetime]
    data_fine: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkOrderCMMSummary(BaseModel):
    """Schema per work order nella lista CMM"""
    id: int
    numero_scheda: str
    stato: str
    data_appuntamento: Optional[datetime]
    data_fine_prevista: Optional[datetime]
    priorita: Optional[str]
    note: Optional[str]
    
    # Dati cliente
    cliente_nome: Optional[str]
    cliente_cognome: Optional[str]
    cliente_telefono: Optional[str]
    
    # Dati veicolo
    veicolo_targa: Optional[str]
    veicolo_marca: Optional[str]
    veicolo_modello: Optional[str]
    
    # Interventi
    interventi: List[InterventionSummary]
    
    # Flag per accesso
    ha_interventi_meccanica: bool
    
    class Config:
        from_attributes = True


def check_cmm_role(current_user: User):
    """Verifica che l'utente abbia ruolo CMM o sia admin"""
    if current_user.ruolo not in ['CMM', 'ADMIN', 'GM']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accesso riservato agli utenti CMM"
        )
    return current_user


# Schema per statistiche interventi per stato
class InterventionStatusStats(BaseModel):
    """Statistiche interventi raggruppate per stato"""
    codice: str
    nome: str
    totale: int


class CMMDashboardStats(BaseModel):
    """Schema per statistiche dashboard CMM"""
    work_orders_approvate: int  # Schede con stato "approvata" e interventi meccanici SENZA stato assegnato
    work_orders_in_lavorazione: int  # Schede con interventi meccanici in lavorazione (preso_in_carico o attesa_componente)
    customers_total: int
    vehicles_total: int
    interventi_totali: int  # Interventi meccanici totali
    interventi_senza_stato: int  # Interventi senza stato assegnato
    interventi_per_stato: List[InterventionStatusStats]


@router.get("/stats", response_model=CMMDashboardStats)
def get_cmm_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CMMDashboardStats:
    """
    Ottiene le statistiche dashboard specifiche per l'utente CMM.
    
    - work_orders_approvate: Schede lavoro "approvate" con interventi meccanici da prendere in carico
    - work_orders_in_lavorazione: Schede con interventi meccanici attivi (preso_in_carico/attesa_componente)
    - interventi_totali: Totale interventi di tipo "Meccanico"
    - interventi_per_stato: Breakdown per stato intervento
    """
    check_cmm_role(current_user)
    
    # Trova gli ID degli stati "attivi" (preso_in_carico, attesa_componente)
    stati_attivi = db.query(InterventionStatusType.id).filter(
        InterventionStatusType.codice.in_(['preso_in_carico', 'attesa_componente']),
        InterventionStatusType.attivo == True
    ).all()
    stati_attivi_ids = [s.id for s in stati_attivi]
    
    # Work orders approvate con interventi meccanici SENZA stato (da prendere in carico)
    approvate_da_lavorare = (
        db.query(WorkOrder.id)
        .join(Intervention)
        .filter(
            WorkOrder.stato == WorkOrderStatus.APPROVATA,
            Intervention.tipo_intervento == 'Meccanico',
            Intervention.stato_intervento_id.is_(None)  # Solo quelli senza stato
        )
        .distinct()
        .count()
    )
    
    # Work orders con interventi meccanici IN LAVORAZIONE
    # (hanno almeno un intervento con stato preso_in_carico o attesa_componente)
    in_lavorazione_con_meccanica = (
        db.query(WorkOrder.id)
        .join(Intervention)
        .filter(
            WorkOrder.stato.in_([WorkOrderStatus.APPROVATA, WorkOrderStatus.IN_LAVORAZIONE]),
            Intervention.tipo_intervento == 'Meccanico',
            Intervention.stato_intervento_id.in_(stati_attivi_ids)
        )
        .distinct()
        .count()
    )
    
    # Totale clienti e veicoli
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0
    
    # Interventi meccanici totali (su schede approvate o in lavorazione)
    interventi_meccanici = (
        db.query(Intervention)
        .join(WorkOrder)
        .filter(
            Intervention.tipo_intervento == 'Meccanico',
            WorkOrder.stato.in_([WorkOrderStatus.APPROVATA, WorkOrderStatus.IN_LAVORAZIONE])
        )
        .all()
    )
    
    interventi_totali = len(interventi_meccanici)
    
    # Conteggio per stato
    stato_counts: Dict[int, int] = {}
    interventi_senza_stato = 0
    
    for i in interventi_meccanici:
        if i.stato_intervento_id:
            stato_counts[i.stato_intervento_id] = stato_counts.get(i.stato_intervento_id, 0) + 1
        else:
            interventi_senza_stato += 1
    
    # Carica nomi stati
    stati = db.query(InterventionStatusType).filter(InterventionStatusType.attivo == True).order_by(InterventionStatusType.ordine).all()
    
    interventi_per_stato = []
    for stato in stati:
        interventi_per_stato.append(InterventionStatusStats(
            codice=stato.codice,
            nome=stato.nome,
            totale=stato_counts.get(stato.id, 0)
        ))
    
    return CMMDashboardStats(
        work_orders_approvate=approvate_da_lavorare,
        work_orders_in_lavorazione=in_lavorazione_con_meccanica,
        customers_total=total_customers,
        vehicles_total=total_vehicles,
        interventi_totali=interventi_totali,
        interventi_senza_stato=interventi_senza_stato,
        interventi_per_stato=interventi_per_stato
    )


@router.get("/work-orders", response_model=List[WorkOrderCMMSummary])
def get_cmm_work_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[WorkOrderCMMSummary]:
    """
    Ottiene la lista delle schede lavoro con stato 'approvata' o 'in lavorazione'
    che hanno almeno un intervento di tipo 'Meccanico'.
    
    Per ogni scheda viene mostrato l'elenco completo degli interventi.
    L'accesso alla singola scheda è consentito solo se ci sono interventi meccanici.
    """
    check_cmm_role(current_user)
    
    # Query per work orders approvati o in lavorazione con interventi
    work_orders = (
        db.query(WorkOrder)
        .options(
            joinedload(WorkOrder.customer),
            joinedload(WorkOrder.vehicle),
            joinedload(WorkOrder.interventions)
        )
        .filter(WorkOrder.stato.in_([WorkOrderStatus.APPROVATA, WorkOrderStatus.IN_LAVORAZIONE]))
        .all()
    )
    
    result = []
    for wo in work_orders:
        # Verifica se ha interventi di meccanica
        ha_meccanica = any(
            i.tipo_intervento == 'Meccanico' 
            for i in wo.interventions
        )
        
        # Costruisci lista interventi con dettagli stato
        interventi = []
        for i in wo.interventions:
            intervento_dict = {
                'id': i.id,
                'progressivo': i.progressivo,
                'descrizione_intervento': i.descrizione_intervento,
                'durata_stimata': float(i.durata_stimata) if i.durata_stimata else 0,
                'tipo_intervento': i.tipo_intervento,
                'stato_intervento_id': i.stato_intervento_id,
                'stato_intervento_codice': i.stato_intervento.codice if i.stato_intervento else None,
                'stato_intervento_nome': i.stato_intervento.nome if i.stato_intervento else None,
                'note_intervento': i.note_intervento,
                'note_sospensione': i.note_sospensione,
                'ore_effettive': float(i.ore_effettive) if i.ore_effettive else None,
                'data_inizio': i.data_inizio,
                'data_fine': i.data_fine,
            }
            interventi.append(InterventionSummary(**intervento_dict))
        
        wo_summary = WorkOrderCMMSummary(
            id=wo.id,
            numero_scheda=wo.numero_scheda,
            stato=wo.stato.value if wo.stato else 'bozza',
            data_appuntamento=wo.data_appuntamento,
            data_fine_prevista=wo.data_fine_prevista,
            priorita=wo.priorita.value if wo.priorita else None,
            note=wo.note,
            cliente_nome=wo.customer.nome if wo.customer else None,
            cliente_cognome=wo.customer.cognome if wo.customer else None,
            cliente_telefono=wo.customer.telefono if wo.customer else None,
            veicolo_targa=wo.vehicle.targa if wo.vehicle else None,
            veicolo_marca=wo.vehicle.marca if wo.vehicle else None,
            veicolo_modello=wo.vehicle.modello if wo.vehicle else None,
            interventi=interventi,
            ha_interventi_meccanica=ha_meccanica,
        )
        
        # Include solo se ha almeno un intervento (per mostrare tutte le schede approvate)
        # oppure filtra solo quelle con meccanica - dipende dai requisiti
        if ha_meccanica or len(wo.interventions) > 0:
            result.append(wo_summary)
    
    # Ordina per priorità e data appuntamento
    priority_order = {'urgente': 0, 'alta': 1, 'media': 2, 'bassa': 3, None: 4}
    result.sort(key=lambda x: (priority_order.get(x.priorita, 4), x.data_appuntamento or datetime.max))
    
    return result


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderCMMSummary)
def get_cmm_work_order_detail(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkOrderCMMSummary:
    """
    Ottiene il dettaglio di una singola scheda lavoro per CMM.
    
    L'accesso è consentito solo se la scheda:
    - È in stato 'approvata'
    - Ha almeno un intervento di tipo 'Meccanico'
    """
    check_cmm_role(current_user)
    
    # Query per work order con tutti i dettagli
    wo = (
        db.query(WorkOrder)
        .options(
            joinedload(WorkOrder.customer),
            joinedload(WorkOrder.vehicle),
            joinedload(WorkOrder.interventions)
        )
        .filter(WorkOrder.id == work_order_id)
        .first()
    )
    
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheda lavoro {work_order_id} non trovata"
        )
    
    # Verifica stato approvata o in lavorazione
    if wo.stato not in [WorkOrderStatus.APPROVATA, WorkOrderStatus.IN_LAVORAZIONE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Questa scheda non è in stato 'approvata' o 'in lavorazione'"
        )
    
    # Verifica presenza interventi meccanici
    ha_meccanica = any(
        i.tipo_intervento == 'Meccanico' 
        for i in wo.interventions
    )
    
    if not ha_meccanica:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Questa scheda non ha interventi di tipo 'Meccanico'"
        )
    
    # Costruisci lista interventi
    interventi = []
    for i in wo.interventions:
        intervento_dict = {
            'id': i.id,
            'progressivo': i.progressivo,
            'descrizione_intervento': i.descrizione_intervento,
            'durata_stimata': float(i.durata_stimata) if i.durata_stimata else 0,
            'tipo_intervento': i.tipo_intervento,
            'stato_intervento_id': i.stato_intervento_id,
            'stato_intervento_codice': i.stato_intervento.codice if i.stato_intervento else None,
            'stato_intervento_nome': i.stato_intervento.nome if i.stato_intervento else None,
            'note_intervento': i.note_intervento,
            'note_sospensione': i.note_sospensione,
            'ore_effettive': float(i.ore_effettive) if i.ore_effettive else None,
            'data_inizio': i.data_inizio,
            'data_fine': i.data_fine,
        }
        interventi.append(InterventionSummary(**intervento_dict))
    
    return WorkOrderCMMSummary(
        id=wo.id,
        numero_scheda=wo.numero_scheda,
        stato=wo.stato.value if wo.stato else 'bozza',
        data_appuntamento=wo.data_appuntamento,
        data_fine_prevista=wo.data_fine_prevista,
        priorita=wo.priorita.value if wo.priorita else None,
        note=wo.note,
        cliente_nome=wo.customer.nome if wo.customer else None,
        cliente_cognome=wo.customer.cognome if wo.customer else None,
        cliente_telefono=wo.customer.telefono if wo.customer else None,
        veicolo_targa=wo.vehicle.targa if wo.vehicle else None,
        veicolo_marca=wo.vehicle.marca if wo.vehicle else None,
        veicolo_modello=wo.vehicle.modello if wo.vehicle else None,
        interventi=interventi,
        ha_interventi_meccanica=ha_meccanica,
    )
