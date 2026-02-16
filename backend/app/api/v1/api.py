"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    customers,
    vehicles,
    work_orders,
    interventions,
    parts,
    tires,
    courtesy_cars,
    maintenance_schedules,
    notifications,
    calendar_events,
    calendar,
    documents,
    activity_logs,
    dashboard,
    system_tables,
    google_oauth,
    lavori_calendar,
    cmm,
    auto
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# User management endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Customer management endpoints
api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["customers"]
)

# Vehicle management endpoints
api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"]
)

# Work order management endpoints
api_router.include_router(
    work_orders.router,
    prefix="/work-orders",
    tags=["work-orders"]
)

# Interventions (Interventi) management endpoints
api_router.include_router(
    interventions.router,
    prefix="/work-orders",
    tags=["interventions"]
)

# Parts (ricambi) management endpoints
api_router.include_router(
    parts.router,
    prefix="/parts",
    tags=["parts"]
)

# Tires (pneumatici) management endpoints
api_router.include_router(
    tires.router,
    prefix="/tires",
    tags=["tires"]
)

# Courtesy cars (auto cortesia) management endpoints
api_router.include_router(
    courtesy_cars.router,
    prefix="/courtesy-cars",
    tags=["courtesy-cars"]
)

# Maintenance schedules (scadenzario) endpoints
api_router.include_router(
    maintenance_schedules.router,
    prefix="/maintenance-schedules",
    tags=["maintenance-schedules"]
)

# Notifications endpoints
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)

# Calendar events endpoints
api_router.include_router(
    calendar_events.router,
    prefix="/calendar-events",
    tags=["calendar-events"]
)

# Documents endpoints
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

# Activity logs endpoints
api_router.include_router(
    activity_logs.router,
    prefix="/activity-logs",
    tags=["activity-logs"]
)

# Dashboard endpoints
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

# System tables endpoints
api_router.include_router(
    system_tables.router,
    prefix="/system-tables",
    tags=["system-tables"]
)

# Google OAuth endpoints
api_router.include_router(
    google_oauth.router,
    tags=["google-oauth"]
)

# Google Calendar booking endpoints
api_router.include_router(
    calendar.router,
    tags=["calendar"]
)

# Work order calendar integration endpoints
api_router.include_router(
    lavori_calendar.router,
    tags=["work-order-calendar"]
)

# CMM (Capo Meccanica) specific endpoints
api_router.include_router(
    cmm.router,
    prefix="/cmm",
    tags=["cmm"]
)

# Auto (marche, modelli, verifica targa) endpoints
api_router.include_router(
    auto.router,
    prefix="/auto",
    tags=["auto"]
)

# TODO: Future endpoints
# - reports (generazione report personalizzati)
# - analytics (statistiche avanzate)
# - integrations (Google Calendar, email, SMS, etc.)
