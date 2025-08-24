# LogiScore Backend Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Authentication & Authorization](#authentication--authorization)
7. [Stripe Integration](#stripe-integration)
8. [SendGrid Integration](#sendgrid-integration)
9. [Business Logic](#business-logic)
10. [Deployment & Configuration](#deployment--configuration)
11. [Security Considerations](#security-considerations)
12. [Error Handling & Logging](#error-handling--logging)

## System Overview

LogiScore is a freight forwarder review and rating platform that provides a comprehensive API for managing users, freight forwarders, reviews, and subscriptions. The system supports both authenticated and anonymous users, with a sophisticated rating system based on weighted categories and questions.

**Key Features:**
- Multi-tenant user management (shippers, freight forwarders)
- Anonymous and authenticated review submissions
- Weighted rating system with category-based scoring
- Subscription management with Stripe integration
- Email notifications via SendGrid
- Advanced search and filtering capabilities
- Admin dashboard for dispute resolution

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (SvelteKit)   │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   External      │
                       │   Services      │
                       │  (Stripe,       │
                       │   SendGrid)     │
                       └─────────────────┘
```

### Application Structure
```
v0 backend/
├── main.py                 # FastAPI application entry point
├── auth/                   # Authentication module
├── database/              # Database models and connection
├── routes/                # API route handlers
├── services/              # Business logic services
├── requirements.txt       # Python dependencies
└── render.yaml           # Deployment configuration
```

### Design Patterns
- **Repository Pattern**: Database operations abstracted through models
- **Service Layer**: Business logic separated from route handlers
- **Dependency Injection**: FastAPI's dependency system for clean architecture
- **Middleware Pattern**: CORS, authentication, and error handling

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation using Python type annotations

### Database
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **PostgreSQL**: Primary database (with SQLite for development)
- **Alembic**: Database migration management

### External Integrations
- **Stripe**: Payment processing and subscription management
- **SendGrid**: Email delivery service
- **GitHub OAuth**: User authentication

### Development & Deployment
- **Python 3.7+**: Runtime environment
- **Render**: Cloud hosting platform
- **Docker**: Containerization support
- **Git**: Version control

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    github_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    full_name VARCHAR(255),
    avatar_url TEXT,
    company_name VARCHAR(255),
    hashed_password VARCHAR(255),
    user_type VARCHAR(20) DEFAULT 'shipper',
    subscription_tier VARCHAR(20) DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Freight Forwarders Table
```sql
CREATE TABLE freight_forwarders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    logo_url TEXT,
    description TEXT,
    headquarters_country VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Reviews Table
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    freight_forwarder_id UUID REFERENCES freight_forwarders(id) NOT NULL,
    branch_id UUID,
    city VARCHAR(100),
    country VARCHAR(100),
    review_type VARCHAR(50) DEFAULT 'general',
    is_anonymous BOOLEAN DEFAULT FALSE,
    review_weight NUMERIC(3,2) DEFAULT 1.0,
    aggregate_rating NUMERIC(3,2),
    weighted_rating NUMERIC(3,2),
    total_questions_rated INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Review Category Scores Table
```sql
CREATE TABLE review_category_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID REFERENCES reviews(id) ON DELETE CASCADE,
    category_id VARCHAR(100) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    question_id VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    rating INTEGER NOT NULL,
    rating_definition TEXT NOT NULL,
    weight NUMERIC(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Key Relationships
- **Users** → **Reviews** (One-to-Many)
- **Freight Forwarders** → **Reviews** (One-to-Many)
- **Reviews** → **Review Category Scores** (One-to-Many)
- **Freight Forwarders** → **Branches** (One-to-Many)

### Database Features
- **UUID Primary Keys**: Globally unique identifiers
- **Hybrid Properties**: Calculated fields for ratings and scores
- **Cascading Deletes**: Automatic cleanup of related records
- **Timestamps**: Created and updated tracking

## API Endpoints

### Base URL
```
Production: https://logiscore-backend.onrender.com
Development: http://localhost:8000
```

### Authentication Endpoints
```
POST /api/auth/login              # User login
POST /api/auth/register           # User registration
POST /api/auth/verify-email       # Email verification
POST /api/auth/forgot-password    # Password reset request
POST /api/auth/reset-password     # Password reset
POST /api/auth/logout             # User logout
GET  /api/auth/me                 # Get current user info
```

### User Management
```
GET    /api/users                 # List users (admin)
GET    /api/users/{user_id}       # Get user details
PUT    /api/users/{user_id}       # Update user
DELETE /api/users/{user_id}       # Delete user
POST   /api/users/update-profile  # Update user profile
```

### Freight Forwarders
```
GET    /api/freight-forwarders           # List all forwarders
GET    /api/freight-forwarders/{id}      # Get forwarder details
POST   /api/freight-forwarders           # Create new forwarder
PUT    /api/freight-forwarders/{id}      # Update forwarder
DELETE /api/freight-forwarders/{id}      # Delete forwarder
GET    /api/freight-forwarders/search    # Search forwarders
```

### Reviews System
```
GET    /api/reviews                      # List reviews
GET    /api/reviews/{id}                 # Get review details
POST   /api/reviews                      # Submit new review
PUT    /api/reviews/{id}                 # Update review
DELETE /api/reviews/{id}                 # Delete review
GET    /api/reviews/forwarder/{id}       # Get reviews for forwarder
POST   /api/reviews/{id}/dispute         # Report review
```

### Search & Analytics
```
GET /api/search/forwarders              # Search freight forwarders
GET /api/search/reviews                 # Search reviews
GET /api/search/aggregate               # Get aggregated search results
GET /api/search/suggestions             # Get search suggestions
```

### Subscription Management
```
POST   /api/subscriptions/create        # Create subscription
POST   /api/subscriptions/cancel        # Cancel subscription
POST   /api/subscriptions/reactivate    # Reactivate subscription
PUT    /api/subscriptions/update-plan   # Change subscription plan
GET    /api/subscriptions/status        # Get subscription status
GET    /api/subscriptions/history       # Get billing history
```

### Locations & Branches
```
GET /api/locations                      # Get all locations
GET /api/locations/cities               # Get cities list
GET /api/locations/countries            # Get countries list
GET /api/locations/forwarder/{id}      # Get forwarder locations
```

### Email Services
```
POST /api/email/contact-form            # Submit contact form
POST /api/email/send-verification       # Send verification email
POST /api/email/send-welcome            # Send welcome email
POST /api/email/review-thank-you        # Send review confirmation
```

### Admin Endpoints
```
GET    /admin/users                     # Admin user management
GET    /admin/reviews                   # Admin review management
GET    /admin/disputes                  # Dispute resolution
PUT    /admin/disputes/{id}/resolve     # Resolve dispute
GET    /admin/analytics                 # System analytics
```

### Webhooks
```
POST /api/webhooks/stripe               # Stripe webhook handler
POST /api/webhooks/github               # GitHub OAuth webhook
```

## Authentication & Authorization

### Authentication Methods
1. **GitHub OAuth**: Primary authentication method
2. **Email/Password**: Fallback authentication
3. **JWT Tokens**: Session management
4. **API Keys**: For admin operations

### JWT Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "user_type": "shipper",
  "subscription_tier": "premium",
  "exp": 1640995200,
  "iat": 1640908800
}
```

### Authorization Levels
- **Public**: Anonymous access to reviews and search
- **Authenticated**: User-specific operations
- **Premium**: Subscription-based features
- **Admin**: System administration and moderation

### Security Features
- **CORS Protection**: Configured for specific domains
- **Rate Limiting**: API request throttling
- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: Input sanitization

## Stripe Integration

### Service Architecture
The `StripeService` class provides a comprehensive interface for Stripe operations:

```python
class StripeService:
    def __init__(self):
        self.stripe = stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Configured price IDs for different subscription tiers
        self.STRIPE_PRICE_IDS = {
            'shipper_monthly': os.getenv('STRIPE_SHIPPER_MONTHLY_PRICE_ID'),
            'shipper_annual': os.getenv('STRIPE_SHIPPER_ANNUAL_PRICE_ID'),
            'forwarder_monthly': os.getenv('STRIPE_FORWARDER_MONTHLY_PRICE_ID'),
            'forwarder_annual': os.getenv('STRIPE_FORWARDER_ANNUAL_PRICE_ID'),
            'forwarder_annual_plus': os.getenv('STRIPE_FORWARDER_ANNUAL_PLUS_PRICE_ID')
        }
```

### Key Features
- **Customer Management**: Create, update, and delete Stripe customers
- **Subscription Handling**: Full subscription lifecycle management
- **Payment Processing**: Payment intents and payment methods
- **Webhook Verification**: Secure webhook signature validation
- **Plan Management**: Dynamic pricing based on user type and tier

### Subscription Tiers
1. **Free**: Basic access to reviews and search
2. **Shipper Monthly/Annual**: Enhanced features for shippers
3. **Forwarder Monthly/Annual**: Business features for forwarders
4. **Forwarder Annual Plus**: Premium features with priority support

### Webhook Events Handled
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `customer.subscription.trial_will_end`

### Error Handling
- **StripeError**: Comprehensive error handling for all Stripe operations
- **Fallback Mechanisms**: Graceful degradation when Stripe is unavailable
- **Logging**: Detailed logging for debugging and monitoring

## SendGrid Integration

### Email Service Architecture
The `EmailService` class manages all email communications:

```python
class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@logiscore.com')
        self.from_name = os.getenv('FROM_NAME', 'LogiScore')
```

### Email Types
1. **Verification Emails**: Email verification codes for new users
2. **Welcome Emails**: Onboarding emails for new registrations
3. **Review Thank You**: Confirmation emails after review submission
4. **Contact Form**: Team notifications and user acknowledgments
5. **Password Reset**: Security emails for account recovery

### Email Templates
- **HTML Formatting**: Professional, responsive email designs
- **Dynamic Content**: Personalized content based on user data
- **Brand Consistency**: Consistent LogiScore branding
- **Mobile Optimization**: Responsive design for all devices

### Features
- **EU Data Residency**: Configurable for GDPR compliance
- **Fallback Mode**: Console logging when SendGrid is unavailable
- **Template Management**: Centralized email template system
- **Error Handling**: Comprehensive error logging and fallbacks

### Email Routing
```python
def get_routing_email(self, contact_reason: str) -> str:
    routing_map = {
        "feedback": "feedback@logiscore.net",
        "support": "support@logiscore.net",
        "billing": "accounts@logiscore.net",
        "reviews": "dispute@logiscore.net",
        "privacy": "dpo@logiscore.net",
        "general": "support@logiscore.net"
    }
    return routing_map.get(contact_reason.lower(), "support@logiscore.net")
```

## Business Logic

### Review System
The review system implements a sophisticated weighted rating algorithm:

#### Rating Calculation
```python
@hybrid_property
def average_rating(self):
    """Calculate average rating from reviews.aggregate_rating"""
    if not self.reviews:
        return 0.0
    
    total_rating = sum(review.aggregate_rating or 0 for review in self.reviews if review.aggregate_rating is not None)
    valid_reviews = sum(1 for review in self.reviews if review.aggregate_rating is not None)
    
    if valid_reviews == 0:
        return 0.0
    
    return total_rating / valid_reviews
```

#### Weighted Scoring
- **Authenticated Reviews**: Weight = 1.0
- **Anonymous Reviews**: Weight = 0.5
- **Category Weights**: Configurable per question
- **Aggregate Calculation**: Sum of (rating × weight) / total weight

#### Review Categories
1. **Service Quality**: Overall service experience
2. **Communication**: Responsiveness and clarity
3. **Timeliness**: Meeting deadlines and schedules
4. **Cost Effectiveness**: Value for money
5. **Problem Resolution**: Handling issues and complaints

### Subscription Management
The subscription system provides flexible plan management:

#### Plan Types
- **Free Tier**: Basic access with limitations
- **Paid Plans**: Feature-rich subscriptions with different pricing
- **Trial Periods**: Configurable trial days for new subscribers
- **Plan Upgrades/Downgrades**: Seamless plan transitions

#### Billing Features
- **Automatic Renewal**: Configurable auto-renewal settings
- **Proration**: Fair billing for plan changes
- **Payment Methods**: Multiple payment method support
- **Invoice Management**: Detailed billing history

### Search & Filtering
Advanced search capabilities with multiple filter options:

#### Search Parameters
- **Text Search**: Company name, description, location
- **Geographic Filtering**: City, country, region
- **Rating Filtering**: Minimum rating thresholds
- **Review Count**: Minimum number of reviews
- **Service Type**: Import, export, domestic, warehousing

#### Search Algorithms
- **Fuzzy Matching**: Typo-tolerant search
- **Relevance Scoring**: Weighted results based on multiple factors
- **Geographic Proximity**: Location-based result ranking
- **Performance Optimization**: Efficient database queries

## Deployment & Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_URL_SQLITE=sqlite:///./test.db

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_SHIPPER_MONTHLY_PRICE_ID=price_...
STRIPE_SHIPPER_ANNUAL_PRICE_ID=price_...
STRIPE_FORWARDER_MONTHLY_PRICE_ID=price_...
STRIPE_FORWARDER_ANNUAL_PRICE_ID=price_...
STRIPE_FORWARDER_ANNUAL_PLUS_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SendGrid Configuration
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@logiscore.com
FROM_NAME=LogiScore
SENDGRID_EU_RESIDENCY=false

# GitHub OAuth
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# JWT Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Render Deployment
The `render.yaml` file configures the deployment:

```yaml
services:
  - type: web
    name: logiscore-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
```

### Database Migrations
The system includes comprehensive migration capabilities:

```python
@app.get("/api/migrate-db")
async def migrate_database():
    """Migrate database to add missing subscription fields"""
    try:
        from database.migrate_subscription_fields import safe_migrate_essential_fields
        safe_migrate_essential_fields()
        return {"message": "Database migration completed successfully"}
    except Exception as e:
        return {"error": f"Migration failed: {str(e)}"}
```

## Security Considerations

### Data Protection
- **Encryption**: All sensitive data encrypted at rest
- **HTTPS**: TLS encryption for all API communications
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy

### Authentication Security
- **JWT Tokens**: Secure, stateless authentication
- **Token Expiration**: Configurable token lifetime
- **Password Hashing**: Secure password storage
- **Rate Limiting**: Protection against brute force attacks

### API Security
- **CORS Configuration**: Restricted to trusted domains
- **Request Validation**: Pydantic model validation
- **Error Handling**: Secure error messages
- **Logging**: Comprehensive security event logging

### Compliance
- **GDPR**: EU data residency options
- **PCI DSS**: Secure payment processing
- **Data Privacy**: User consent and data control
- **Audit Trails**: Comprehensive activity logging

## Error Handling & Logging

### Global Exception Handler
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
```

### Logging Configuration
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Error Types
1. **HTTP Exceptions**: Standard HTTP error responses
2. **Validation Errors**: Pydantic model validation failures
3. **Database Errors**: SQLAlchemy operation failures
4. **External Service Errors**: Stripe, SendGrid failures
5. **Authentication Errors**: JWT and OAuth failures

### Monitoring & Alerting
- **Health Checks**: `/health` endpoint for system monitoring
- **Performance Metrics**: Request timing and response codes
- **Error Tracking**: Comprehensive error logging
- **External Service Status**: Integration health monitoring

## Recent Fixes & Maintenance

### Admin Dashboard Schema Fixes (August 2025)
The admin dashboard was experiencing database schema mismatches that have been resolved:

#### Issues Fixed
1. **Column Mismatch**: `disputes.reported_by` vs `disputes.resolved_by`
2. **Missing Relationships**: Dispute model lacked proper relationships to User and Review
3. **Null Reference Errors**: Admin routes accessing non-existent user attributes

#### Solutions Implemented
1. **Schema Migration**: Created `fix_dispute_schema.py` to align database with models
2. **Relationship Mapping**: Added proper SQLAlchemy relationships:
   ```python
   # Dispute model relationships
   review = relationship("Review", backref="disputes")
   reporter = relationship("User", foreign_keys=[reported_by], backref="reported_disputes")
   
   # User model additions
   reported_disputes = relationship("Dispute", foreign_keys="Dispute.reported_by", back_populates="reporter")
   
   # Review model additions
   disputes = relationship("Dispute", back_populates="review")
   ```

3. **Safe Data Access**: Updated admin routes to handle null values gracefully:
   ```python
   # Safe user name access
   user_name = "Anonymous"
   if review.user:
       user_name = review.user.username or review.user.full_name or review.user.email or "User"
   ```

#### Migration Endpoint
```bash
GET /api/fix-dispute-schema
```
This endpoint automatically fixes the dispute table schema and adds missing foreign key constraints.

#### Database Schema Alignment
The system now properly handles:
- **Dispute Reporting**: Users can report reviews through proper relationships
- **Admin Dashboard**: All statistics and recent activity load correctly
- **Data Integrity**: Foreign key constraints ensure referential integrity
- **Error Handling**: Graceful fallbacks for missing or null data

---

## Conclusion

The LogiScore backend is a robust, scalable system built with modern Python technologies. It provides comprehensive APIs for freight forwarder reviews, user management, and subscription services. The system's architecture emphasizes security, performance, and maintainability, with clear separation of concerns and comprehensive error handling.

The integration with Stripe and SendGrid provides enterprise-grade payment processing and email delivery capabilities, while the sophisticated review system offers accurate and fair ratings through weighted algorithms. The modular design allows for easy extension and maintenance, making it suitable for production deployment and future enhancements.

For technical support or questions about this documentation, please contact the development team or refer to the project's GitHub repository.
