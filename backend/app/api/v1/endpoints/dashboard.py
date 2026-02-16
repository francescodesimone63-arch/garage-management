"""
API endpoints per il dashboard (viste aggregate per ruoli).
"""
from typing import Dict, Any
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.part import Part
from app.models.tire import Tire, TireCondition
from app.models.courtesy_car import CourtesyCar, CourtesyCarStatus
from app.models.maintenance_schedule import MaintenanceSchedule, MaintenanceStatus
from app.models.notification import Notification, NotificationStatus
from app.models.calendar_event import CalendarEvent
from app.models.activity_log import ActivityLog

router = APIRouter()


@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dashboard principale - dati aggregati per ruolo utente.
    """
    # Dati base per tutti i ruoli
    today = datetime.utcnow().date()
    
    # Contatori globali
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    total_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0
    
    # Schede lavoro
    work_orders_open = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.stato == WorkOrderStatus.BOZZA
    ).scalar() or 0
    
    work_orders_in_progress = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.stato == WorkOrderStatus.IN_LAVORAZIONE
    ).scalar() or 0
    
    work_orders_pending_approval = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.stato == WorkOrderStatus.APPROVATA
    ).scalar() or 0
    
    # Ricambi in esaurimento
    parts_low_stock = db.query(func.count(Part.id)).filter(
        Part.quantita <= Part.quantita_minima
    ).scalar() or 0
    
    # Auto cortesia disponibili
    courtesy_cars_available = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE
    ).scalar() or 0
    
    # Manutenzioni in scadenza/scadute
    maintenance_alerts = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVA,
            MaintenanceSchedule.data_scadenza <= today
        )
    ).scalar() or 0
    
    # Notifiche non lette utente corrente
    unread_notifications = db.query(func.count(Notification.id)).filter(
        and_(
            Notification.destinatario == current_user.email,
            Notification.stato == NotificationStatus.PENDING
        )
    ).scalar() or 0
    
    # Schede lavoro recenti (ultime 5)
    recent_work_orders = db.query(WorkOrder).order_by(
        WorkOrder.created_at.desc()
    ).limit(5).all()
    
    recent_work_orders_data = []
    for wo in recent_work_orders:
        recent_work_orders_data.append({
            "id": wo.id,
            "work_order_number": wo.numero_scheda,
            "status": wo.stato.value if hasattr(wo.stato, 'value') else str(wo.stato),
            "opening_date": wo.data_creazione.isoformat() if wo.data_creazione else None,
            "description": wo.valutazione_danno or "",
            "vehicle_id": wo.vehicle_id,
            "customer_id": wo.customer_id
        })
    
    return {
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "stats": {
            "work_orders_open": work_orders_open,
            "work_orders_in_progress": work_orders_in_progress,
            "work_orders_pending_approval": work_orders_pending_approval,
            "customers_total": total_customers,
            "vehicles_total": total_vehicles,
            "parts_low_stock": parts_low_stock,
            "courtesy_cars_available": courtesy_cars_available,
            "maintenance_alerts": maintenance_alerts,
            "unread_notifications": unread_notifications
        },
        "recent_work_orders": recent_work_orders_data,
        "alerts": []
    }


def get_gm_dashboard(db: Session, today: date, week_start: date, month_start: date) -> Dict[str, Any]:
    """
    Dashboard per General Manager - vista completa gestionale.
    """
    # KPI Operativi
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    new_customers_month = db.query(func.count(Customer.id)).filter(
        Customer.created_at >= datetime.combine(month_start, datetime.min.time())
    ).scalar() or 0
    
    # Schede lavoro
    total_work_orders = db.query(func.count(WorkOrder.id)).scalar() or 0
    pending_approval = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.stato == WorkOrderStatus.APPROVATA
    ).scalar() or 0
    in_progress = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.stato == WorkOrderStatus.IN_LAVORAZIONE
    ).scalar() or 0
    completed_month = db.query(func.count(WorkOrder.id)).filter(
        and_(
            WorkOrder.stato == WorkOrderStatus.COMPLETATA,
            WorkOrder.updated_at >= datetime.combine(month_start, datetime.min.time())
        )
    ).scalar() or 0
    
    # Fatturato stimato mese (schede completate)
    revenue_month = db.query(func.sum(WorkOrder.final_total)).filter(
        and_(
            WorkOrder.stato == WorkOrderStatus.COMPLETATA,
            WorkOrder.updated_at >= datetime.combine(month_start, datetime.min.time())
        )
    ).scalar() or 0
    
    # Alert e scadenze
    overdue_maintenance = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVA,
            MaintenanceSchedule.data_scadenza < today
        )
    ).scalar() or 0
    
    low_stock_parts = db.query(func.count(Part.id)).filter(
        Part.quantita <= Part.quantita_minima
    ).scalar() or 0
    
    # Auto cortesia
    available_cars = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE
    ).scalar() or 0
    cars_on_loan = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.ASSEGNATA
    ).scalar() or 0
    
    # Pneumatici da sostituire
    tires_to_replace = db.query(func.count(Tire.id)).filter(
        or_(
            Tire.tread_depth < 3.0,
            Tire.condition.in_([TireCondition.POOR, TireCondition.WORN_OUT])
        )
    ).scalar() or 0
    
    # Attività recente (ultimi 7 giorni)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activities = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.timestamp >= week_ago
    ).scalar() or 0
    
    return {
        "role": "GENERAL_MANAGER",
        "kpi": {
            "customers": {
                "total": total_customers,
                "new_this_month": new_customers_month
            },
            "work_orders": {
                "total": total_work_orders,
                "pending_approval": pending_approval,
                "in_progress": in_progress,
                "completed_this_month": completed_month
            },
            "revenue": {
                "this_month": float(revenue_month),
                "currency": "EUR"
            }
        },
        "alerts": {
            "overdue_maintenance": overdue_maintenance,
            "low_stock_parts": low_stock_parts,
            "tires_to_replace": tires_to_replace
        },
        "resources": {
            "courtesy_cars": {
                "available": available_cars,
                "on_loan": cars_on_loan
            }
        },
        "activity": {
            "recent_actions_7d": recent_activities
        }
    }


def get_workshop_dashboard(db: Session, current_user: User, today: date) -> Dict[str, Any]:
    """
    Dashboard per Officina/Carrozzeria - vista operativa lavori.
    """
    # Schede lavoro assegnate/in corso
    my_work_orders = db.query(func.count(WorkOrder.id)).filter(
        and_(
            WorkOrder.assigned_to_id == current_user.id,
            WorkOrder.stato.in_([WorkOrderStatus.IN_LAVORAZIONE, WorkOrderStatus.APPROVATA])
        )
    ).scalar() or 0
    
    # Schede completate oggi
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    completed_today = db.query(func.count(WorkOrder.id)).filter(
        and_(
            WorkOrder.assigned_to_id == current_user.id,
            WorkOrder.stato == WorkOrderStatus.COMPLETATA,
            WorkOrder.updated_at >= today_start,
            WorkOrder.updated_at <= today_end
        )
    ).scalar() or 0
    
    # Appuntamenti oggi
    my_events_today = db.query(func.count(CalendarEvent.id)).filter(
        and_(
            CalendarEvent.assigned_to_id == current_user.id,
            CalendarEvent.start_datetime >= today_start,
            CalendarEvent.start_datetime <= today_end
        )
    ).scalar() or 0
    
    # Auto cortesia disponibili
    available_cars = db.query(func.count(CourtesyCar.id)).filter(
        CourtesyCar.stato == CourtesyCarStatus.DISPONIBILE
    ).scalar() or 0
    
    # Ricambi scorte basse
    low_stock_parts = db.query(func.count(Part.id)).filter(
        Part.quantita <= Part.quantita_minima
    ).scalar() or 0
    
    # Manutenzioni in scadenza (prossimi 7 giorni)
    week_from_now = today + timedelta(days=7)
    upcoming_maintenance = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVA,
            MaintenanceSchedule.data_scadenza >= today,
            MaintenanceSchedule.data_scadenza <= week_from_now
        )
    ).scalar() or 0
    
    return {
        "role": current_user.role.value,
        "my_work": {
            "active_work_orders": my_work_orders,
            "completed_today": completed_today,
            "appointments_today": my_events_today
        },
        "resources": {
            "available_courtesy_cars": available_cars,
            "low_stock_parts": low_stock_parts
        },
        "upcoming": {
            "maintenance_next_7days": upcoming_maintenance
        }
    }


@router.get("/alerts", response_model=Dict[str, Any])
def get_dashboard_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Alert e notifiche dashboard.
    """
    today = datetime.utcnow().date()
    alerts = []
    
    # Schede in attesa approvazione (solo GM)
    if current_user.role == UserRole.GENERAL_MANAGER:
        pending_count = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.stato == WorkOrderStatus.APPROVATA
        ).scalar() or 0
        
        if pending_count > 0:
            alerts.append({
                "type": "work_orders",
                "level": "warning",
                "message": f"{pending_count} schede lavoro in attesa di approvazione",
                "count": pending_count
            })
    
    # Manutenzioni scadute
    overdue_maintenance = db.query(func.count(MaintenanceSchedule.id)).filter(
        and_(
            MaintenanceSchedule.stato == MaintenanceStatus.ATTIVA,
            MaintenanceSchedule.data_scadenza < today
        )
    ).scalar() or 0
    
    if overdue_maintenance > 0:
        alerts.append({
            "type": "maintenance",
            "level": "critical",
            "message": f"{overdue_maintenance} manutenzioni scadute",
            "count": overdue_maintenance
        })
    
    # Ricambi esauriti
    out_of_stock = db.query(func.count(Part.id)).filter(
        Part.quantita == 0
    ).scalar() or 0
    
    if out_of_stock > 0:
        alerts.append({
            "type": "inventory",
            "level": "critical",
            "message": f"{out_of_stock} ricambi esauriti",
            "count": out_of_stock
        })
    
    # Ricambi scorte basse
    low_stock = db.query(func.count(Part.id)).filter(
        and_(
            Part.quantita > 0,
            Part.quantita <= Part.quantita_minima
        )
    ).scalar() or 0
    
    if low_stock > 0:
        alerts.append({
            "type": "inventory",
            "level": "warning",
            "message": f"{low_stock} ricambi sotto scorta minima",
            "count": low_stock
        })
    
    # Pneumatici da sostituire
    tires_critical = db.query(func.count(Tire.id)).filter(
        or_(
            Tire.tread_depth < 1.6,  # Limite legale
            Tire.condition == TireCondition.WORN_OUT
        )
    ).scalar() or 0
    
    if tires_critical > 0:
        alerts.append({
            "type": "tires",
            "level": "critical",
            "message": f"{tires_critical} pneumatici da sostituire urgentemente",
            "count": tires_critical
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }


@router.get("/recent-activity", response_model=Dict[str, Any])
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Attività recenti per dashboard.
    """
    # Ultimi work orders
    recent_work_orders = db.query(WorkOrder).order_by(
        WorkOrder.updated_at.desc()
    ).limit(limit).all()
    
    work_orders_data = []
    for wo in recent_work_orders:
        work_orders_data.append({
            "id": wo.id,
            "customer_name": wo.customer.full_name if wo.customer else None,
            "vehicle": f"{wo.vehicle.make} {wo.vehicle.model}" if wo.vehicle else None,
            "status": wo.status.value,
            "updated_at": wo.updated_at.isoformat()
        })
    
    # Ultimi eventi calendario
    upcoming_events = db.query(CalendarEvent).filter(
        CalendarEvent.start_datetime >= datetime.utcnow()
    ).order_by(CalendarEvent.start_datetime.asc()).limit(limit).all()
    
    events_data = []
    for event in upcoming_events:
        events_data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_datetime.isoformat(),
            "type": event.event_type.value if event.event_type else None
        })
    
    return {
        "recent_work_orders": work_orders_data,
        "upcoming_events": events_data
    }


@router.get("/stats/overview", response_model=Dict[str, Any])
def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Statistiche generali sistema.
    """
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    month_start_dt = datetime.combine(month_start, datetime.min.time())
    
    # Contatori base
    stats = {
        "entities": {
            "customers": db.query(func.count(Customer.id)).scalar() or 0,
            "vehicles": db.query(func.count(Vehicle.id)).scalar() or 0,
            "work_orders": db.query(func.count(WorkOrder.id)).scalar() or 0,
            "parts": db.query(func.count(Part.id)).scalar() or 0
        },
        "this_month": {
            "new_customers": db.query(func.count(Customer.id)).filter(
                Customer.created_at >= month_start_dt
            ).scalar() or 0,
            "completed_work_orders": db.query(func.count(WorkOrder.id)).filter(
                and_(
                    WorkOrder.stato == WorkOrderStatus.COMPLETATA,
                    WorkOrder.updated_at >= month_start_dt
                )
            ).scalar() or 0,
            "revenue": float(db.query(func.sum(WorkOrder.final_total)).filter(
                and_(
                    WorkOrder.stato == WorkOrderStatus.COMPLETATA,
                    WorkOrder.updated_at >= month_start_dt
                )
            ).scalar() or 0)
        }
    }
    
    return stats
