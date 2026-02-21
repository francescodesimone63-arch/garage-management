"""
Main FastAPI application entry point
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import sync_engine, Base
from app.api.v1.api import api_router
from app.core.logging_config import setup_logging, get_logger

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Caricato .env da: {env_path}")
else:
    print(f"⚠️  File .env non trovato: {env_path}")

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

# ============================================================================
# MIDDLEWARE STACK
# ============================================================================
# Ordine: i middleware aggiunti per ULTIMO sono i più ESTERNI e eseguiti per PRIMI
# Quindi l'ordine di aggiunta è inverso all'ordine di esecuzione
#
# Stack finale (da outer a inner):
#   1. CORS → gestisce preflight OPTIONS e aggiunge header CORS
#   2. GZip → comprime risposte
#   3. Session → gestisce sessioni per Google OAuth
# ============================================================================

# 1. CORS middleware - DEVE ESSERE AGGIUNTO PER ULTIMO (eseguito PRIMO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend porta standard
        "http://localhost:3001",  # Frontend porta alternativa (Vite)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
logger.info("✅ CORS middleware attivato")

# 2. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)
logger.info("✅ GZip middleware attivato")

# 3. Session middleware (per Google OAuth)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
logger.info("✅ Session middleware attivato")

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