"""
Interventions endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import Intervention, WorkOrder, User
from app.schemas.intervention import Intervention as InterventionSchema, InterventionCreate, InterventionUpdate

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
        tipo_intervento=intervention_in.tipo_intervento
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
