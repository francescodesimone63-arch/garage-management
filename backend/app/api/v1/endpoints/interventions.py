"""
Interventions endpoints
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import Intervention, WorkOrder, User, InterventionStatusType
from app.models.work_order import WorkOrderStatus
from app.models.work_order_audit import WorkOrderAudit, TransitionType
from app.schemas.intervention import (
    Intervention as InterventionSchema,
    InterventionCreate,
    InterventionUpdate,
    InterventionStatusUpdate
)

router = APIRouter(tags=["interventions"])


@router.post("/{work_order_id}/interventions", response_model=InterventionSchema, status_code=status.HTTP_201_CREATED)
def create_intervention(
    work_order_id: int,
    intervention_in: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterventionSchema:
    """
    Crea un nuovo intervento per una scheda lavoro.
    
    I campi obbligatori sono:
    - descrizione_intervento
    - durata_stimata
    - tipo_intervento (Meccanico o Carrozziere)
    
    Il progressivo viene assegnato automaticamente se non fornito.
    """
    # Verifica che la scheda lavoro esista
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheda lavoro con ID {work_order_id} non trovata"
        )
    
    # Calcola il progressivo automaticamente se non fornito
    if intervention_in.progressivo is None:
        last_intervention = (
            db.query(Intervention)
            .filter(Intervention.work_order_id == work_order_id)
            .order_by(Intervention.progressivo.desc())
            .first()
        )
        progressivo = 1 if not last_intervention else last_intervention.progressivo + 1
    else:
        progressivo = intervention_in.progressivo
    
    # Crea il nuovo intervento
    intervention = Intervention(
        work_order_id=work_order_id,
        progressivo=progressivo,
        descrizione_intervento=intervention_in.descrizione_intervento,
        durata_stimata=intervention_in.durata_stimata,
        tipo_intervento=intervention_in.tipo_intervento,
        stato_intervento_id=intervention_in.stato_intervento_id,
        note_intervento=intervention_in.note_intervento
    )
    
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


@router.get("/{work_order_id}/interventions", response_model=List[InterventionSchema])
def list_interventions(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InterventionSchema]:
    """
    Ottiene la lista di tutti gli interventi per una scheda lavoro,
    ordinati per progressivo.
    """
    # Verifica che la scheda lavoro esista
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheda lavoro con ID {work_order_id} non trovata"
        )
    
    interventions = (
        db.query(Intervention)
        .filter(Intervention.work_order_id == work_order_id)
        .order_by(Intervention.progressivo)
        .all()
    )
    return interventions


@router.get("/{intervention_id}", response_model=InterventionSchema)
def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterventionSchema:
    """Ottiene i dettagli di un singolo intervento"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervento con ID {intervention_id} non trovato"
        )
    return intervention


@router.put("/{work_order_id}/interventions/{intervention_id}", response_model=InterventionSchema)
def update_intervention(
    work_order_id: int,
    intervention_id: int,
    intervention_update: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterventionSchema:
    """Aggiorna un intervento esistente"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervento con ID {intervention_id} non trovato"
        )
    
    # Aggiorna solo i campi forniti
    update_data = intervention_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(intervention, field, value)
    
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


@router.delete("/{work_order_id}/interventions/{intervention_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intervention(
    work_order_id: int,
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Cancella un intervento"""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervento con ID {intervention_id} non trovato"
        )
    
    db.delete(intervention)
    db.commit()


@router.patch("/{work_order_id}/interventions/{intervention_id}/status", response_model=InterventionSchema)
def update_intervention_status(
    work_order_id: int,
    intervention_id: int,
    status_update: InterventionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InterventionSchema:
    """
    Aggiorna lo stato di un intervento (per utenti CMM/CBM).
    
    Stati disponibili:
    - preso_in_carico: L'intervento è in lavorazione
    - attesa_componente: È stato richiesto l'acquisto di un componente
    - sospeso: Intervento sospeso (richiede nota_sospensione obbligatoria)
    - concluso: L'intervento è stato completato
    """
    # Verifica che l'intervento esista
    intervention = db.query(Intervention).filter(
        Intervention.id == intervention_id,
        Intervention.work_order_id == work_order_id
    ).first()
    
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervento con ID {intervention_id} non trovato per la scheda {work_order_id}"
        )
    
    # Verifica che lo stato esista
    stato = db.query(InterventionStatusType).filter(
        InterventionStatusType.id == status_update.stato_intervento_id,
        InterventionStatusType.attivo == True
    ).first()
    
    if not stato:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stato intervento non valido"
        )
    
    # Se lo stato richiede nota e non è fornita, errore
    if stato.richiede_nota and not status_update.note_sospensione:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lo stato '{stato.nome}' richiede una nota descrittiva"
        )
    
    # Aggiorna l'intervento
    intervention.stato_intervento_id = status_update.stato_intervento_id
    
    if status_update.note_intervento is not None:
        intervention.note_intervento = status_update.note_intervento
        
    if status_update.note_sospensione is not None:
        intervention.note_sospensione = status_update.note_sospensione
    
    # Se stato è "preso_in_carico" e non c'è data_inizio, la imposta
    if stato.codice == "preso_in_carico" and not intervention.data_inizio:
        intervention.data_inizio = datetime.now()
    
    # Se stato è "concluso", imposta data_fine
    if stato.codice == "concluso" and not intervention.data_fine:
        intervention.data_fine = datetime.now()
    
    # Cambio automatico stato scheda lavoro:
    # Se la scheda è "approvata" e l'intervento viene preso in carico,
    # la scheda passa automaticamente a "in lavorazione"
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if work_order and work_order.stato == WorkOrderStatus.APPROVATA:
        if stato.codice in ["preso_in_carico", "attesa_componente"]:
            old_stato = work_order.stato
            work_order.stato = WorkOrderStatus.IN_LAVORAZIONE
            db.add(work_order)
            
            # Crea record di audit per il cambio automatico
            audit = WorkOrderAudit(
                work_order_id=work_order_id,
                from_state=old_stato,
                to_state=WorkOrderStatus.IN_LAVORAZIONE,
                transition_type=TransitionType.AUTOMATIC,
                executed_by=current_user.id,
                user_role=current_user.ruolo,
                reason=f"Cambio automatico: intervento #{intervention.progressivo} preso in carico da CMM"
            )
            db.add(audit)
    
    # Se tutti gli interventi della scheda sono "conclusi", la scheda passa a "completata"
    if work_order and stato.codice == "concluso":
        # Trova l'ID dello stato "concluso"
        stato_concluso = db.query(InterventionStatusType).filter(
            InterventionStatusType.codice == "concluso",
            InterventionStatusType.attivo == True
        ).first()
        
        if stato_concluso:
            # Conta interventi della scheda
            tutti_interventi = db.query(Intervention).filter(
                Intervention.work_order_id == work_order_id
            ).all()
            
            # Verifica se tutti sono conclusi (considerando l'aggiornamento corrente)
            tutti_conclusi = all(
                (i.id == intervention_id and status_update.stato_intervento_id == stato_concluso.id) or
                (i.id != intervention_id and i.stato_intervento_id == stato_concluso.id)
                for i in tutti_interventi
            )
            
            if tutti_conclusi and work_order.stato in [WorkOrderStatus.APPROVATA, WorkOrderStatus.IN_LAVORAZIONE]:
                old_stato = work_order.stato
                work_order.stato = WorkOrderStatus.COMPLETATA
                db.add(work_order)
                
                # Crea record di audit per il cambio automatico
                audit = WorkOrderAudit(
                    work_order_id=work_order_id,
                    from_state=old_stato,
                    to_state=WorkOrderStatus.COMPLETATA,
                    transition_type=TransitionType.AUTOMATIC,
                    executed_by=current_user.id,
                    user_role=current_user.ruolo,
                    reason="Cambio automatico: tutti gli interventi completati"
                )
                db.add(audit)
    
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention
