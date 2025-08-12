from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import stripe
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional
import logging
from fastapi.responses import JSONResponse

# Import our modules
from database.database import get_db, get_engine
from database.models import Base
from auth.auth import get_current_user, create_access_token
from routes import users, freight_forwarders, reviews, search, subscriptions

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LogiScore API",
    description="Freight forwarder review and rating platform API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://logiscore.net",  # HTTP version
        "https://logiscore.net",  # HTTPS version
        "https://logiscore-frontend.vercel.app",
        "https://logiscore-frontend-git-main-evaluratenet.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel subdomains
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=False,  # Changed to False to avoid CORS issues
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create database tables (only if database is available)
try:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    logger.warning(f"Could not create database tables: {e}")

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(freight_forwarders.router, prefix="/api/freight-forwarders", tags=["freight-forwarders"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LogiScore API is running",
        "version": "1.0.5",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        db = next(get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for development"""
    return {"message": "API is working correctly"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "CORS preflight handled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 