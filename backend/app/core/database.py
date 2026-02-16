"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import MetaData, create_engine

from app.core.config import settings

# Create async engine (for API)
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# Create sync engine (for scripts/migrations)
# Convert async database URLs to sync versions
def get_sync_database_url(url: str) -> str:
    """Convert async database URL to sync version"""
    if '+aiosqlite' in url:
        # SQLite: sqlite+aiosqlite:/// -> sqlite:///
        return url.replace('+aiosqlite', '')
    elif '+asyncpg' in url:
        # PostgreSQL: postgresql+asyncpg:// -> postgresql://
        return url.replace('+asyncpg', '')
    else:
        return url

sync_engine = create_engine(
    get_sync_database_url(settings.database_url),
    echo=settings.debug
)

# Create async session factory (for API)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory (for scripts)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Create Base class for models
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

Base = declarative_base(metadata=metadata)


# Dependency to get DB session
async def get_db() -> AsyncSession:
    """
    Dependency function to get database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Database initialization
async def init_db():
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models import (
            user, customer, vehicle, work_order, part, 
            tire, courtesy_car, maintenance_schedule, 
            notification, calendar_event
        )
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


# Database cleanup
async def close_db():
    """
    Close database connections
    """
    await engine.dispose()