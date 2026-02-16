"""
Work Order State Manager Service
Manages state transitions, prerequisites validation, and audit trail
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from app.models import (
    WorkOrder, WorkOrderStatus, WorkOrderAudit, TransitionType, User, UserRole
)
from app.services.notification_service import NotificationService


class StateTransitionRule:
    """Defines a valid state transition with prerequisites and post-actions"""
    
    def __init__(
        self,
        from_state: WorkOrderStatus,
        to_state: WorkOrderStatus,
        allowed_roles: List[UserRole],
        prerequisites: Optional[Dict[str, Any]] = None,
        post_action_callback=None,
        reason_required: bool = False
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.allowed_roles = allowed_roles
        self.prerequisites = prerequisites or {}
        self.post_action_callback = post_action_callback
        self.reason_required = reason_required
    
    def can_execute(
        self, 
        work_order: WorkOrder, 
        user: User,
        form_overrides: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str]:
        """Check if transition can be executed
        
        Args:
            work_order: La scheda di lavoro dal database
            user: L'utente che esegue la transizione
            form_overrides: Valori dalla form che sovrascrivono quelli del DB
                - interventions_count: numero di interventi nella form
                - has_descrizione: se la descrizione è compilata nella form
        """
        # Check role authorization
        if user.ruolo not in self.allowed_roles:
            return False, f"Ruolo {user.ruolo} non autorizzato per questa transizione"
        
        # Check prerequisites
        prereq_ok, prereq_error = self._check_prerequisites(work_order, form_overrides)
        if not prereq_ok:
            return False, prereq_error
        
        return True, ""
    
    def _check_prerequisites(
        self, 
        work_order: WorkOrder,
        form_overrides: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str]:
        """Validate prerequisites for transition
        
        Uses form_overrides if provided, otherwise falls back to DB values
        
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        form_overrides = form_overrides or {}
        
        # APPROVATA: almeno un intervento
        if self.to_state == WorkOrderStatus.APPROVATA:
            # Usa il conteggio dalla form se fornito, altrimenti dal DB
            if 'interventions_count' in form_overrides:
                interventions_count = form_overrides['interventions_count']
            else:
                interventions_count = len(work_order.interventions) if work_order.interventions else 0
            
            if interventions_count == 0:
                return False, "Per approvare la scheda lavoro deve essere inserito almeno un intervento"
        
        # IN_LAVORAZIONE: deve essere approvata e assegnata a un tecnico
        elif self.to_state == WorkOrderStatus.IN_LAVORAZIONE:
            if work_order.stato != WorkOrderStatus.APPROVATA:
                return False, "La scheda deve essere prima approvata"
        
        # COMPLETATA: tutte le attività devono essere complete
        elif self.to_state == WorkOrderStatus.COMPLETATA:
            if work_order.stato != WorkOrderStatus.IN_LAVORAZIONE:
                return False, "La scheda deve essere in lavorazione"
            if not work_order.activities:
                return False, "Devono essere presenti delle attività"
            if not all(act.stato.value == "completata" for act in work_order.activities):
                return False, "Tutte le attività devono essere completate"
        
        return True, ""
    
    async def execute_post_actions(self, work_order: WorkOrder, db: Session):
        """Execute post-action callbacks"""
        if self.post_action_callback:
            await self.post_action_callback(work_order, db)


class WorkOrderStateManager:
    """Manages work order state transitions with authorization and audit"""
    
    # Define all valid state transitions
    VALID_TRANSITIONS = [
        # BOZZA → APPROVATA (GM approval required)
        StateTransitionRule(
            from_state=WorkOrderStatus.BOZZA,
            to_state=WorkOrderStatus.APPROVATA,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=False
        ),
        
        # APPROVATA → IN_LAVORAZIONE (Tecnico inizia il lavoro)
        StateTransitionRule(
            from_state=WorkOrderStatus.APPROVATA,
            to_state=WorkOrderStatus.IN_LAVORAZIONE,
            allowed_roles=[UserRole.WORKSHOP, UserRole.BODYSHOP, UserRole.ADMIN],
            reason_required=False
        ),
        
        # IN_LAVORAZIONE → COMPLETATA (Lavoro terminato)
        StateTransitionRule(
            from_state=WorkOrderStatus.IN_LAVORAZIONE,
            to_state=WorkOrderStatus.COMPLETATA,
            allowed_roles=[UserRole.WORKSHOP, UserRole.BODYSHOP, UserRole.ADMIN],
            reason_required=False
        ),
        
        # COMPLETATA → IN_LAVORAZIONE (Riapertura per correzioni)
        StateTransitionRule(
            from_state=WorkOrderStatus.COMPLETATA,
            to_state=WorkOrderStatus.IN_LAVORAZIONE,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=True
        ),
        
        # Qualunque stato → ANNULLATA (Cancellazione)
        StateTransitionRule(
            from_state=WorkOrderStatus.BOZZA,
            to_state=WorkOrderStatus.ANNULLATA,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=True
        ),
        StateTransitionRule(
            from_state=WorkOrderStatus.APPROVATA,
            to_state=WorkOrderStatus.ANNULLATA,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=True
        ),
        StateTransitionRule(
            from_state=WorkOrderStatus.IN_LAVORAZIONE,
            to_state=WorkOrderStatus.ANNULLATA,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=True
        ),
        
        # ANNULLATA → BOZZA (Ripristino scheda annullata)
        StateTransitionRule(
            from_state=WorkOrderStatus.ANNULLATA,
            to_state=WorkOrderStatus.BOZZA,
            allowed_roles=[UserRole.GENERAL_MANAGER, UserRole.ADMIN],
            reason_required=True
        ),
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()
    
    def _get_transition_recipients(self, allowed_roles: List[UserRole]) -> List[Dict[str, Any]]:
        """Get all active users with the allowed roles"""
        try:
            # Converti i ruoli enum a stringhe per il filtro
            allowed_roles_values = [role.value for role in allowed_roles]
            
            users = self.db.query(User).filter(
                User.ruolo.in_(allowed_roles_values),
                User.attivo == True
            ).all()
            
            return [
                {
                    "id": u.id,
                    "name": u.full_name,
                    "email": u.email,
                    "role": u.ruolo.value
                }
                for u in users
            ]
        except Exception as e:
            print(f"❌ ERRORE in _get_transition_recipients: {str(e)}")
            return []
    
    def get_available_transitions(
        self,
        work_order: WorkOrder,
        user: User,
        form_overrides: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get list of available state transitions for current user
        
        Args:
            work_order: La scheda di lavoro
            user: L'utente corrente
            form_overrides: Valori dalla form per validazione (opzionale)
        """
        available = []
        
        for rule in self.VALID_TRANSITIONS:
            if rule.from_state == work_order.stato:
                can_execute, reason = rule.can_execute(work_order, user, form_overrides)
                
                # Ottieni i destinatari (utenti con i ruoli autorizzati)
                recipients = self._get_transition_recipients(rule.allowed_roles)
                
                available.append({
                    "to_state": rule.to_state.value,
                    "allowed": can_execute,
                    "reason_required": rule.reason_required,
                    "explanation": reason if not can_execute else "",
                    "allowed_roles": [role.value for role in rule.allowed_roles],
                    "recipients": recipients
                })
        
        return available
    
    async def transition(
        self,
        work_order_id: int,
        new_state: WorkOrderStatus,
        user: User,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        form_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute state transition with full validation and audit trail
        
        Args:
            work_order_id: ID della scheda di lavoro
            new_state: Nuovo stato desiderato
            user: Utente che esegue la transizione
            reason: Motivo della transizione (richiesto per alcune transizioni)
            ip_address: Indirizzo IP dell'utente
            user_agent: User agent del browser
            form_overrides: Valori dalla form per validazione prerequisiti
                - interventions_count: numero interventi nella form
                - has_descrizione: se descrizione è compilata
        
        Returns:
            Dict con risultato della transizione
        
        Raises:
            HTTPException: Se la transizione non è valida
        """
        # Carica la scheda
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not work_order:
            raise HTTPException(status_code=404, detail="Scheda non trovata")
        
        # Trova la regola di transizione
        rule = self._find_transition_rule(work_order.stato, new_state)
        if not rule:
            raise HTTPException(
                status_code=400,
                detail=f"Transizione da {work_order.stato.value} a {new_state.value} non consentita"
            )
        
        # Valida la transizione
        can_execute, error_msg = rule.can_execute(work_order, user, form_overrides)
        if not can_execute:
            raise HTTPException(status_code=403, detail=error_msg)
        
        # Valida che il motivo sia fornito se richiesto
        if rule.reason_required and not reason:
            raise HTTPException(
                status_code=400,
                detail="Motivo della transizione obbligatorio per questa azione"
            )
        
        # Esegui la transizione
        old_state = work_order.stato
        work_order.stato = new_state
        
        # Aggiorna timestamp per COMPLETATA
        if new_state == WorkOrderStatus.COMPLETATA:
            work_order.data_completamento = datetime.utcnow()
        
        # Registra l'audit
        audit_entry = WorkOrderAudit(
            work_order_id=work_order_id,
            from_state=old_state,
            to_state=new_state,
            transition_type=TransitionType.MANUAL,
            executed_by=user.id,
            user_role=user.ruolo.value,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_entry)
        self.db.commit()
        
        # Esegui post-actions (notifiche, etc.)
        await self._execute_post_actions(work_order, old_state, new_state, user)
        
        return {
            "success": True,
            "work_order_id": work_order_id,
            "from_state": old_state.value,
            "to_state": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "executed_by": {
                "id": user.id,
                "name": user.full_name,
                "role": user.ruolo.value
            }
        }
    
    def _find_transition_rule(
        self,
        from_state: WorkOrderStatus,
        to_state: WorkOrderStatus
    ) -> Optional[StateTransitionRule]:
        """Find transition rule matching from/to states"""
        for rule in self.VALID_TRANSITIONS:
            if rule.from_state == from_state and rule.to_state == to_state:
                return rule
        return None
    
    async def _execute_post_actions(
        self,
        work_order: WorkOrder,
        old_state: WorkOrderStatus,
        new_state: WorkOrderStatus,
        user: User
    ):
        """Execute post-transition actions (notifications, etc.)"""
        try:
            # APPROVATA: Notifica al tecnico che può iniziare il lavoro
            if new_state == WorkOrderStatus.APPROVATA:
                # Cerca tecnici WORKSHOP o BODYSHOP based on tipo_danno
                tecnici = self.db.query(User).filter(
                    User.ruolo.in_([UserRole.WORKSHOP, UserRole.BODYSHOP]),
                    User.attivo == True
                ).all()
                
                for tecnico in tecnici:
                    await self.notification_service.notify_work_order_approved(
                        work_order, tecnico, user
                    )
            
            # IN_LAVORAZIONE: Notifica al GM che il lavoro è iniziato
            elif new_state == WorkOrderStatus.IN_LAVORAZIONE:
                gm_users = self.db.query(User).filter(
                    User.ruolo == UserRole.GENERAL_MANAGER,
                    User.attivo == True
                ).all()
                
                for gm in gm_users:
                    await self.notification_service.notify_work_started(
                        work_order, gm, user
                    )
            
            # COMPLETATA: Notifica al GM e al cliente
            elif new_state == WorkOrderStatus.COMPLETATA:
                gm_users = self.db.query(User).filter(
                    User.ruolo == UserRole.GENERAL_MANAGER,
                    User.attivo == True
                ).all()
                
                for gm in gm_users:
                    await self.notification_service.notify_work_completed(
                        work_order, gm, user
                    )
            
            # ANNULLATA: Notifica a tutti gli stakeholder
            elif new_state == WorkOrderStatus.ANNULLATA:
                all_users = self.db.query(User).filter(
                    User.attivo == True
                ).all()
                
                for stakeholder in all_users:
                    await self.notification_service.notify_work_order_cancelled(
                        work_order, stakeholder, user
                    )
        
        except Exception as e:
            # Log l'errore ma non interrompere il flusso
            print(f"Errore durante post-actions: {str(e)}")
    
    def get_audit_trail(
        self,
        work_order_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a work order"""
        audits = self.db.query(WorkOrderAudit).filter(
            WorkOrderAudit.work_order_id == work_order_id
        ).order_by(WorkOrderAudit.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": audit.id,
                "from_state": audit.from_state.value,
                "to_state": audit.to_state.value,
                "executed_by": {
                    "id": audit.executor.id,
                    "name": audit.executor.full_name,
                    "role": audit.executor.ruolo.value
                },
                "reason": audit.reason,
                "timestamp": audit.created_at.isoformat()
            }
            for audit in audits
        ]
