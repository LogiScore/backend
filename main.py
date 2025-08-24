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
from routes import users, freight_forwarders, reviews, search, subscriptions, auth, locations, email, admin

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
        "https://www.logiscore.net",  # WWW subdomain
        "http://www.logiscore.net",  # WWW subdomain HTTP
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
    allow_credentials=True,  # Required for JWT authentication headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
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
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(freight_forwarders.router, prefix="/api/freight-forwarders", tags=["freight-forwarders"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])  # Locations API for frontend integration
app.include_router(email.router, prefix="/api/email", tags=["email"])  # Email API for sending emails
app.include_router(admin.router, prefix="/admin", tags=["admin"])  # Admin API for 8x7k9m2p dashboard

@app.get("/api/migrate-db")
async def migrate_database():
    """Migrate database to add missing subscription fields"""
    try:
        from database.migrate_subscription_fields import safe_migrate_essential_fields
        safe_migrate_essential_fields()
        return {"message": "Database migration completed successfully"}
    except Exception as e:
        return {"error": f"Migration failed: {str(e)}"}

@app.get("/api/fix-username-constraint")
async def fix_username_constraint():
    """Remove unique constraint on username column"""
    try:
        from database.migrate_subscription_fields import remove_username_unique_constraint
        remove_username_unique_constraint()
        return {"message": "Username constraint fix completed successfully"}
    except Exception as e:
        return {"error": f"Username constraint fix failed: {str(e)}"}

@app.get("/api/fix-dispute-schema")
async def fix_dispute_schema():
    """Fix dispute table schema mismatch"""
    try:
        from database.fix_dispute_schema import fix_dispute_schema, add_dispute_relationships
        if fix_dispute_schema():
            if add_dispute_relationships():
                return {"message": "Dispute schema fix completed successfully"}
            else:
                return {"message": "Dispute schema fixed but relationships failed"}
        else:
            return {"error": "Dispute schema fix failed"}
    except Exception as e:
        return {"error": f"Dispute schema fix failed: {str(e)}"}

# Add backward compatibility routes for auth endpoints
app.include_router(auth.router, prefix="/auth", tags=["auth-compat"])

# Import and include webhook router
from routes import webhooks
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS test successful",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True
    }

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

@app.get("/api/locations-test")
async def locations_test():
    """Test endpoint to verify locations router is loaded"""
    return {"message": "Locations router is accessible", "status": "ready"}

@app.get("/api/locations-simple")
async def locations_simple():
    """Simple test endpoint directly in main.py"""
    return {
        "message": "Direct locations endpoint working",
        "data": [
            {"id": "test-1", "name": "Test Location 1", "city": "Test City"},
            {"id": "test-2", "name": "Test Location 2", "city": "Test City 2"}
        ]
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 