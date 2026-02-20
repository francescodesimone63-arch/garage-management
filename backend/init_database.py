#!/usr/bin/env python3
"""Initialize database from models"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base

# Import all models to ensure they are registered
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.work_order import WorkOrder
from app.models.work_order_audit import WorkOrderAudit
from app.models.part import Part
from app.models.tire import Tire
from app.models.maintenance_schedule import MaintenanceSchedule
from app.models.document import Document
from app.models.activity_log import ActivityLog
from app.models.notification import Notification
from app.models.intervention import Intervention
from app.models.google_oauth import GoogleOAuthToken
from app.models.calendar_event import CalendarEvent
from app.models.courtesy_car import CourtesyCar
from app.models.system_tables import InterventionStatusType, InsuranceBranchType


async def init_database():
    """Create all tables in the database"""
    engine = create_async_engine("sqlite+aiosqlite:///garage.db", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())
