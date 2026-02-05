"""
Content Analytics Platform - FastAPI Backend
============================================
Main application entry point.
"""

import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

from src.database import init_database, check_database_connection, get_database_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting Content Analytics API...")
    
    # Initialize database
    if check_database_connection():
        init_database()
        logger.info("Database initialized")
    else:
        logger.warning("Database connection failed - running in limited mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Content Analytics API...")


# Create FastAPI app
app = FastAPI(
    title="Content Analytics Platform",
    description="YouTube & Instagram Creator Performance Analytics API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8501,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include routers
from server.routes import youtube, instagram, analytics, ml, ai

app.include_router(youtube.router, prefix="/api/youtube", tags=["YouTube"])
app.include_router(instagram.router, prefix="/api/instagram", tags=["Instagram"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ml.router, prefix="/api/ml", tags=["Machine Learning"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Insights"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Content Analytics Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = check_database_connection()
    
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }


@app.get("/info")
async def system_info():
    """System information endpoint."""
    try:
        db_info = get_database_info()
    except Exception:
        db_info = {"status": "unavailable"}
    
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": db_info,
        "features": {
            "youtube": True,
            "instagram": True,
            "ml_predictions": True,
            "forecasting": True
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "server.main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
