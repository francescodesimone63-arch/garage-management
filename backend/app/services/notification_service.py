"""
Notification Service for Work Order state transitions
Handles email notifications, in-app notifications, and alerts
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import WorkOrder, User, Notification, NotificationType


class NotificationService:
    """Manages notifications for work order events"""
    
    async def notify_work_order_approved(
        self,
        work_order: WorkOrder,
        recipient: User,
        approved_by: User
    ):
        """Notify technician that work order is approved and ready to start"""
        subject = f"Scheda approvata: {work_order.numero_scheda}"
        message = f"""
La scheda di lavoro {work_order.numero_scheda} è stata approvata da {approved_by.full_name}.
        
Cliente: {work_order.customer.nome}
Veicolo: {work_order.vehicle.targa}
Data prevista: {work_order.data_fine_prevista.strftime('%d/%m/%Y') if work_order.data_fine_prevista else 'Non specificata'}

Puoi iniziare a lavorare sulla scheda.
        """
        
        await self._create_notification(
            recipient=recipient,
            work_order=work_order,
            subject=subject,
            message=message,
            notification_type=NotificationType.WORK_ORDER_APPROVED if hasattr(NotificationType, 'WORK_ORDER_APPROVED') else NotificationType.INFO
        )
        
        # TODO: Invia email
        await self._send_email(recipient.email, subject, message)
    
    async def notify_work_started(
        self,
        work_order: WorkOrder,
        recipient: User,
        started_by: User
    ):
        """Notify GM that work has started"""
        subject = f"Lavoro iniziato: {work_order.numero_scheda}"
        message = f"""
Il lavoro sulla scheda {work_order.numero_scheda} è stato iniziato da {started_by.full_name}.
        
Cliente: {work_order.customer.nome}
Veicolo: {work_order.vehicle.targa}
Valutazione danno: {work_order.valutazione_danno or 'Non specificato'}
        """
        
        await self._create_notification(
            recipient=recipient,
            work_order=work_order,
            subject=subject,
            message=message,
            notification_type=NotificationType.INFO
        )
        
        # TODO: Invia email
        await self._send_email(recipient.email, subject, message)
    
    async def notify_work_completed(
        self,
        work_order: WorkOrder,
        recipient: User,
        completed_by: User
    ):
        """Notify GM that work is completed"""
        subject = f"Lavoro completato: {work_order.numero_scheda}"
        message = f"""
Il lavoro sulla scheda {work_order.numero_scheda} è stato completato da {completed_by.full_name}.
        
Cliente: {work_order.customer.nome}
Veicolo: {work_order.vehicle.targa}
Costo stimato: €{work_order.costo_stimato or '0'}
Costo finale: €{work_order.costo_finale or 'Da definire'}
        
Procedi con la fatturazione se necessario.
        """
        
        await self._create_notification(
            recipient=recipient,
            work_order=work_order,
            subject=subject,
            message=message,
            notification_type=NotificationType.INFO
        )
        
        # TODO: Invia email
        await self._send_email(recipient.email, subject, message)
    
    async def notify_work_order_cancelled(
        self,
        work_order: WorkOrder,
        recipient: User,
        cancelled_by: User
    ):
        """Notify all users that work order is cancelled"""
        subject = f"Scheda annullata: {work_order.numero_scheda}"
        message = f"""
La scheda di lavoro {work_order.numero_scheda} è stata annullata da {cancelled_by.full_name}.
        
Cliente: {work_order.customer.nome}
Veicolo: {work_order.vehicle.targa}
        """
        
        await self._create_notification(
            recipient=recipient,
            work_order=work_order,
            subject=subject,
            message=message,
            notification_type=NotificationType.INFO
        )
        
        # TODO: Invia email
        await self._send_email(recipient.email, subject, message)
    
    async def _create_notification(
        self,
        recipient: User,
        work_order: WorkOrder,
        subject: str,
        message: str,
        notification_type: NotificationType
    ):
        """Create in-app notification"""
        # TODO: Implement database storage when Notification model is ready
        pass
    
    async def _send_email(self, email: str, subject: str, message: str):
        """Send email notification"""
        # TODO: Implement email sending via SMTP or email service
        # For now, just log it
        print(f"Email to {email}: {subject}")
        print(message)
