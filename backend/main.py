"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import sync_engine, Base
from app.api.v1.api import api_router
from app.core.logging_config import setup_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware

# Setup logging system
logger = setup_logging("garage_management", level="DEBUG")
logger.info("=" * 80)
logger.info("🚀 GARAGE MANAGEMENT SYSTEM - AVVIO")
logger.info("=" * 80)

# Create database tables using sync engine
Base.metadata.create_all(bind=sync_engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema di Gestione Officina Meccanica - API Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    redirect_slashes=False  # Disabilita redirect automatici da /vehicles a /vehicles/
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add session middleware (for Google OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Add logging middleware to track all requests
app.add_middleware(LoggingMiddleware)
logger.info("✅ Logging middleware attivato")

# Include API router
app.include_router(api_router, prefix=settings.api_v1_str)
logger.info(f"✅ API router registrato: {settings.api_v1_str}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Garage Management System API",
        "version": settings.app_version,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )