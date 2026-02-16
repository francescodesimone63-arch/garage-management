"""
Pydantic schemas for request/response models
"""
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB, Token, TokenData
from app.schemas.customer import (
    Customer, CustomerCreate, CustomerUpdate,
    CustomerWithVehicles, CustomerWithStats
)
from app.schemas.vehicle import (
    Vehicle, VehicleCreate, VehicleUpdate,
    VehicleWithCustomer, VehicleWithHistory
)
from app.schemas.work_order import (
    WorkOrder, WorkOrderCreate, WorkOrderUpdate,
    WorkOrderWithDetails
)
from app.schemas.part import Part, PartCreate, PartUpdate
from app.schemas.tire import Tire, TireCreate, TireUpdate
from app.schemas.courtesy_car import CourtesyCar, CourtesyCarCreate, CourtesyCarUpdate
from app.schemas.maintenance_schedule import MaintenanceSchedule, MaintenanceScheduleCreate, MaintenanceScheduleUpdate
from app.schemas.notification import Notification, NotificationCreate, NotificationUpdate
from app.schemas.calendar_event import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.schemas.activity_log import ActivityLog, ActivityLogCreate

# Rebuild models to resolve forward references
# This must be done after all schemas are imported
CustomerWithVehicles.model_rebuild()
VehicleWithCustomer.model_rebuild()
VehicleWithHistory.model_rebuild()
WorkOrderWithDetails.model_rebuild()

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserInDB", "Token", "TokenData",
    # Customer schemas
    "Customer", "CustomerCreate", "CustomerUpdate", "CustomerWithVehicles", "CustomerWithStats",
    # Vehicle schemas
    "Vehicle", "VehicleCreate", "VehicleUpdate", "VehicleWithCustomer", "VehicleWithHistory",
    # Work order schemas
    "WorkOrder", "WorkOrderCreate", "WorkOrderUpdate", "WorkOrderWithDetails",
    # Part schemas
    "Part", "PartCreate", "PartUpdate",
    # Tire schemas
    "Tire", "TireCreate", "TireUpdate",
    # Courtesy car schemas
    "CourtesyCar", "CourtesyCarCreate", "CourtesyCarUpdate",
    # Maintenance schedule schemas
    "MaintenanceSchedule", "MaintenanceScheduleCreate", "MaintenanceScheduleUpdate",
    # Notification schemas
    "Notification", "NotificationCreate", "NotificationUpdate",
    # Calendar event schemas
    "CalendarEvent", "CalendarEventCreate", "CalendarEventUpdate",
    # Document schemas
    "Document", "DocumentCreate", "DocumentUpdate",
    # Activity log schemas
    "ActivityLog", "ActivityLogCreate",
]
