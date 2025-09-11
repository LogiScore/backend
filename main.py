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
from routes import users, freight_forwarders, reviews, search, subscriptions, auth, locations, email, admin, review_subscriptions, notifications, score_threshold_subscriptions, analytics, promotions

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
app.include_router(review_subscriptions.router, prefix="/api/review-subscriptions", tags=["review-subscriptions"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])  # Notification system endpoints
app.include_router(score_threshold_subscriptions.router, prefix="/api/score-threshold-subscriptions", tags=["score-threshold-subscriptions"])  # Score threshold notification system
app.include_router(score_threshold_subscriptions.router, prefix="/api/threshold-subscriptions", tags=["threshold-subscriptions"])  # Alias for frontend compatibility
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])  # Locations API for frontend integration
app.include_router(email.router, prefix="/api/email", tags=["email"])  # Email API for sending emails
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])  # Admin API for 8x7k9m2p dashboard
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])  # Analytics API for score trends
app.include_router(promotions.router, prefix="/api/promotions", tags=["promotions"])  # Promotion API for reward system

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

@app.get("/api/add-notification-indexes")
async def add_notification_indexes():
    """Add database indexes for notification system performance"""
    try:
        from database.add_notification_indexes import add_notification_indexes
        if add_notification_indexes():
            return {"message": "Notification indexes added successfully"}
        else:
            return {"error": "Failed to add notification indexes"}
    except Exception as e:
        return {"error": f"Notification index creation failed: {str(e)}"}

@app.get("/api/fix-rating-constraint")
async def fix_rating_constraint():
    """Fix review_category_scores rating constraint to accept 0-5 range instead of 0-4"""
    try:
        from database.fix_rating_constraint import fix_rating_constraint
        if fix_rating_constraint():
            return {"message": "Rating constraint updated successfully to accept 0-5 range"}
        else:
            return {"error": "Failed to update rating constraint"}
    except Exception as e:
        return {"error": f"Rating constraint fix failed: {str(e)}"}

@app.get("/api/update-review-questions-5-point")
async def update_review_questions_5_point(db: Session = Depends(get_db)):
    """Update review questions table to use proper 5-point rating system"""
    try:
        from database.models import ReviewQuestion
        
        # Clear existing questions
        db.query(ReviewQuestion).delete()
        db.commit()
        
        # All 33 questions from LogiScore Review Questions document
        all_questions = [
            # 1. Responsiveness (5 questions)
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_001",
                "question_text": "Acknowledges receipt of requests (for quotation or information) within 30 minutes (even if full response comes later)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_002",
                "question_text": "Provides clear estimated response time if immediate resolution is not possible",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_003",
                "question_text": "Responds within 6 hours to rate requests to/from locations within the same region",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_004",
                "question_text": "Responds within 24 hours to rate requests to/from other regions (e.g. Asia to US, US to Europe)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_005",
                "question_text": "Responds to emergency requests (e.g., urgent shipment delay, customs issues) within 30 minutes",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            
            # 2. Shipment Management (5 questions)
            {
                "category_id": "shipment_management",
                "category_name": "Shipment Management",
                "question_id": "ship_001",
                "question_text": "Proactively sends shipment milestones (e.g., pickup, departure, arrival, delivery) without being asked",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "shipment_management",
                "category_name": "Shipment Management",
                "question_id": "ship_002",
                "question_text": "Sends pre-alerts before vessel ETA",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "shipment_management",
                "category_name": "Shipment Management",
                "question_id": "ship_003",
                "question_text": "Provides POD (proof of delivery) within 24 hours of delivery",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "shipment_management",
                "category_name": "Shipment Management",
                "question_id": "ship_004",
                "question_text": "Proactively notifies delays or disruptions",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "shipment_management",
                "category_name": "Shipment Management",
                "question_id": "ship_005",
                "question_text": "Offers recovery plans in case of delays or missed transshipments",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            
            # 3. Documentation (4 questions)
            {
                "category_id": "documentation",
                "category_name": "Documentation",
                "question_id": "doc_001",
                "question_text": "Issues draft B/L or HAWB within 24 hours of cargo departure",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "documentation",
                "category_name": "Documentation",
                "question_id": "doc_002",
                "question_text": "Sends final invoices within 48 hours of shipment completion",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "documentation",
                "category_name": "Documentation",
                "question_id": "doc_003",
                "question_text": "Ensures documentation is accurate and complete on first submission",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "documentation",
                "category_name": "Documentation",
                "question_id": "doc_004",
                "question_text": "Final invoice matches quotation (no hidden costs and all calculations and volumes are correct)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            
            # 4. Customer Experience (6 questions)
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_001",
                "question_text": "Follows up on pending issues without the need for reminders",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_002",
                "question_text": "Rectifies documentation (shipping documents and invoices/credit notes) within 48 hours",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_003",
                "question_text": "Provides named contact person(s) for operations and customer service",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_004",
                "question_text": "Offers single point of contact for issue escalation",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_005",
                "question_text": "Replies in professional tone, avoids jargon unless relevant",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Never", "2": "Seldom", "3": "Usually", "4": "Most of the time", "5": "Every time"
                }
            },
            {
                "category_id": "customer_experience",
                "category_name": "Customer Experience",
                "question_id": "cust_006",
                "question_text": "Customer Service and Operations have vertical specific knowledge (e.g. Chemicals, Pharma, Hightech)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "None", "2": "Some", "3": "Aware but not knowledgable", "4": "Knowledgable", "5": "Very knowledgable"
                }
            },
            
            # 5. Technology Process (4 questions)
            {
                "category_id": "technology_process",
                "category_name": "Technology Process",
                "question_id": "tech_001",
                "question_text": "Offers online track-and-trace",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "Only via phone, messaging or email", "3": "Provided via the website, however data doesn't seem dynamic nor current", "4": "Provided via the website and data seems dynamic and current", "5": "Provided via web or mobile app, data is dynamic and current, able to schedule reports and triggered by milestones"
                }
            },
            {
                "category_id": "technology_process",
                "category_name": "Technology Process",
                "question_id": "tech_002",
                "question_text": "Has an online document portal to access shipment documents and invoices",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "Limited availability - only for selected customers", "3": "Basic availability - documents are not current or complete", "4": "On demand access - documents are available on scheduled basis", "5": "Available via web or mobile app on demand, with download and notification options"
                }
            },
            {
                "category_id": "technology_process",
                "category_name": "Technology Process",
                "question_id": "tech_003",
                "question_text": "Integrates with customer systems (e.g., EDI/API) where required",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "Limited availability - only for selected customers", "3": "Available however Forwarder lacks experience; project management and frequent technical issues", "4": "Standard capability - available and able to implement effortlessly", "5": "Advanced integration capabilities offering mature, flexible and secure integration services to a variety of ERP/TMS/WMS systems"
                }
            },
            {
                "category_id": "technology_process",
                "category_name": "Technology Process",
                "question_id": "tech_004",
                "question_text": "Able to provides regular reporting (e.g., weekly shipment report, KPI report)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "Reporting is manual", "3": "Limited available - only select customers", "4": "Standardized access for all customers. Available and setup either by provider or via a web portal.", "5": "Advances, customizable reporting via interactive dashboards on the web or mobile devices with advances analytical functions"
                }
            },
            
            # 6. Reliability & Execution (6 questions)
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_001",
                "question_text": "On-time pickup",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Seldom", "2": "Occasionally", "3": "Usually", "4": "Often", "5": "Always"
                }
            },
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_002",
                "question_text": "Shipped as promised",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Seldom", "2": "Occasionally", "3": "Usually", "4": "Often", "5": "Always"
                }
            },
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_003",
                "question_text": "On-time delivery",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Seldom", "2": "Occasionally", "3": "Usually", "4": "Often", "5": "Always"
                }
            },
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_004",
                "question_text": "Compliance with clients' SOP",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Does not define SOP's and has no quality system (ISO 9001)", "2": "Follows quality system, SOP's for large customers", "3": "Defines and usually follows", "4": "Defines and follows most of the time", "5": "Always follows clients' SOP"
                }
            },
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_005",
                "question_text": "Customs declaration errors",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Very often", "2": "Frequent errors", "3": "Occasional errors", "4": "Seldom errors", "5": "No errors"
                }
            },
            {
                "category_id": "reliability_execution",
                "category_name": "Reliability & Execution",
                "question_id": "rel_006",
                "question_text": "Claims ratio (number of claims / total shipments)",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Often", "2": "Regularly", "3": "Occasionally", "4": "Rarely", "5": "Never"
                }
            },
            
            # 7. Proactivity & Insight (3 questions)
            {
                "category_id": "proactivity_insight",
                "category_name": "Proactivity & Insight",
                "question_id": "pro_001",
                "question_text": "Provides trends relating to rates, capacities, carriers, customs and geopolitical issues that might impact global trade and the client and mitigation options the client could consider",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not able to provide any information", "2": "Provides some information when requested", "3": "Provides detailed updates when requested", "4": "Proactively provides regular periodic updates", "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
                }
            },
            {
                "category_id": "proactivity_insight",
                "category_name": "Proactivity & Insight",
                "question_id": "pro_002",
                "question_text": "Notifies customer of upcoming GRI or BAF changes in advance and mitigation options",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not able to provide any information", "2": "Provides some information when requested", "3": "Provides detailed updates when requested", "4": "Proactively provides regular periodic updates", "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
                }
            },
            {
                "category_id": "proactivity_insight",
                "category_name": "Proactivity & Insight",
                "question_id": "pro_003",
                "question_text": "Provides suggestions for consolidation, better routings, or mode shifts",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not able to provide any information", "2": "Provides some information when requested", "3": "Provides detailed updates when requested", "4": "Proactively provides regular periodic updates", "5": "Proactive and advisory - acts as a trusted advisor that actively monitors and proactively updates and recommendations"
                }
            },
            
            # 8. After Hours Support (2 questions)
            {
                "category_id": "after_hours_support",
                "category_name": "After Hours Support",
                "question_id": "after_001",
                "question_text": "Has 24/7 support or provides emergency contact for after-hours escalation",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "Helpdesk/control tower only responds during working hours", "3": "Provides a helpdesk/control tower however responds only after 2-4 hours", "4": "Provides a helpdesk/control tower that responds within 1-2 hours", "5": "Provides 24/7 helpdesk/control tower"
                }
            },
            {
                "category_id": "after_hours_support",
                "category_name": "After Hours Support",
                "question_id": "after_002",
                "question_text": "Weekend or holiday contact provided in advance for critical shipments",
                "rating_definitions": {
                    "0": "Not applicable", "1": "Not available", "2": "No contact available on weekends or holidays", "3": "Contact responds within 2-4 hours", "4": "Contact responds within 1-2 hours", "5": "Provides 24/7 contact"
                }
            }
        ]
        
        # Insert all questions
        for question_data in all_questions:
            question = ReviewQuestion(
                category_id=question_data["category_id"],
                category_name=question_data["category_name"],
                question_id=question_data["question_id"],
                question_text=question_data["question_text"],
                rating_definitions=question_data["rating_definitions"],
                is_active=True
            )
            db.add(question)
        
        db.commit()
        
        return {
            "message": "All 33 review questions updated to 5-point system successfully",
            "questions_added": len(all_questions),
            "categories": [
                "Responsiveness (5 questions)",
                "Shipment Management (5 questions)", 
                "Documentation (4 questions)",
                "Customer Experience (6 questions)",
                "Technology Process (4 questions)",
                "Reliability & Execution (6 questions)",
                "Proactivity & Insight (3 questions)",
                "After Hours Support (2 questions)"
            ],
            "total_categories": 8,
            "rating_scale": "0-5 (5-point system)"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {"error": f"Review questions update failed: {str(e)}", "details": error_details}

@app.get("/api/test-endpoint")
async def test_endpoint():
    """Test endpoint to verify deployment is working"""
    return {"message": "Backend is working", "status": "ok"}

@app.get("/api/update-review-questions-simple")
async def update_review_questions_simple(db: Session = Depends(get_db)):
    """Simple version of review questions update - direct database approach"""
    try:
        from database.models import ReviewQuestion
        
        # Clear existing questions
        db.query(ReviewQuestion).delete()
        db.commit()
        
        # Sample questions for testing (first 3 questions)
        sample_questions = [
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_001",
                "question_text": "Acknowledges receipt of requests (for quotation or information) within 30 minutes (even if full response comes later)",
                "rating_definitions": {
                    "0": "Not applicable",
                    "1": "Never",
                    "2": "Seldom",
                    "3": "Usually",
                    "4": "Most of the time",
                    "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_002",
                "question_text": "Provides clear estimated response time if immediate resolution is not possible",
                "rating_definitions": {
                    "0": "Not applicable",
                    "1": "Never",
                    "2": "Seldom",
                    "3": "Usually",
                    "4": "Most of the time",
                    "5": "Every time"
                }
            },
            {
                "category_id": "responsiveness",
                "category_name": "Responsiveness",
                "question_id": "resp_003",
                "question_text": "Responds within 6 hours to rate requests to/from locations within the same region",
                "rating_definitions": {
                    "0": "Not applicable",
                    "1": "Never",
                    "2": "Seldom",
                    "3": "Usually",
                    "4": "Most of the time",
                    "5": "Every time"
                }
            }
        ]
        
        # Insert sample questions
        for question_data in sample_questions:
            question = ReviewQuestion(
                category_id=question_data["category_id"],
                category_name=question_data["category_name"],
                question_id=question_data["question_id"],
                question_text=question_data["question_text"],
                rating_definitions=question_data["rating_definitions"],
                is_active=True
            )
            db.add(question)
        
        db.commit()
        
        return {
            "message": "Sample review questions updated successfully",
            "questions_added": len(sample_questions),
            "note": "This is a simplified version with 3 sample questions"
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {"error": f"Simple update failed: {str(e)}", "details": error_details}

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

@app.get("/api/stripe-config-test")
async def stripe_config_test():
    """Test Stripe configuration"""
    try:
        stripe_key = os.getenv("STRIPE_SECRET_KEY")
        publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if not stripe_key or stripe_key == "sk_test_your_test_secret_key_here":
            return {
                "status": "error",
                "message": "Stripe secret key not configured properly",
                "stripe_secret_configured": bool(stripe_key and stripe_key != "sk_test_your_test_secret_key_here"),
                "stripe_publishable_configured": bool(publishable_key and publishable_key != "pk_test_your_test_publishable_key_here")
            }
        
        # Test Stripe API call
        stripe.api_key = stripe_key
        account = stripe.Account.retrieve()
        
        return {
            "status": "success",
            "message": "Stripe configuration is working",
            "stripe_account_id": account.id,
            "stripe_secret_configured": True,
            "stripe_publishable_configured": bool(publishable_key and publishable_key != "pk_test_your_test_publishable_key_here")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Stripe configuration error: {str(e)}",
            "stripe_secret_configured": bool(os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_SECRET_KEY") != "sk_test_your_test_secret_key_here"),
            "stripe_publishable_configured": bool(os.getenv("STRIPE_PUBLISHABLE_KEY") and os.getenv("STRIPE_PUBLISHABLE_KEY") != "pk_test_your_test_publishable_key_here")
        }

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