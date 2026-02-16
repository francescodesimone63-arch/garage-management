"""
Database models for the Garage Management System
"""
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.intervention import Intervention
from app.models.work_order_audit import WorkOrderAudit, TransitionType
from app.models.part import Part
from app.models.tire import Tire, TireStatus
from app.models.courtesy_car import CourtesyCar, CourtesyCarStatus
from app.models.maintenance_schedule import MaintenanceSchedule
from app.models.notification import Notification, NotificationType
from app.models.calendar_event import CalendarEvent
from app.models.document import Document, DocumentType
from app.models.activity_log import ActivityLog
from app.models.system_tables import DamageType, CustomerType, WorkOrderStatusType, PriorityType
from app.models.google_oauth import GoogleOAuthToken

__all__ = [
    "User",
    "UserRole",
    "Customer",
    "Vehicle",
    "WorkOrder",
    "WorkOrderStatus",
    "Intervention",
    "WorkOrderAudit",
    "TransitionType",
    "Part",
    "Tire",
    "TireStatus",
    "CourtesyCar",
    "CourtesyCarStatus",
    "MaintenanceSchedule",
    "Notification",
    "NotificationType",
    "CalendarEvent",
    "Document",
    "DocumentType",
    "ActivityLog",
    "GoogleOAuthToken",
]
