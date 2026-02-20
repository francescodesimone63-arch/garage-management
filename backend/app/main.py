"""
Main FastAPI application for Garage Management System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load .env file at startup
load_dotenv()

from app.core.config import Settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.middleware.cors_preflight import CORSPreflightMiddleware

# Create tables
async def create_tables_async():
    """Create tables using async engine"""
    from sqlalchemy import text
    
    # For async SQLite, we need to use the engine in a different way
    # The tables are typically created during app startup or via migrations
    pass

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - tables are created by Alembic migrations
    yield
    # Shutdown
    pass

# Initialize settings
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CORS preflight middleware (must be added after CORSMiddleware to execute first)
app.add_middleware(CORSPreflightMiddleware)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_str)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }

# Root endpoint - intercepts Google OAuth callback
@app.get("/")
async def root(code: str = None, state: str = None):
    """
    Root endpoint that handles both root requests and Google OAuth callbacks.
    
    If code and state are present (from Google), redirects to the actual callback endpoint.
    Otherwise, returns API info.
    """
    # Check if this is a Google OAuth callback
    if code and state:
        # Redirect to the actual callback endpoint
        return RedirectResponse(
            url=f"/api/v1/google/oauth/callback?code={code}&state={state}",
            status_code=302
        )
    
    # Otherwise, return API info
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/docs",
        "api_url": settings.api_v1_str,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
