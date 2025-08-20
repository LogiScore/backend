from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from database.database import get_db
from database.models import User, FreightForwarder, Review, Dispute
from auth.auth import get_current_user

router = APIRouter()

# Pydantic models for admin responses
class DashboardStats(BaseModel):
    total_users: int
    total_companies: int
    total_reviews: int
    pending_disputes: int
    pending_reviews: int
    total_revenue: float

class AdminUser(BaseModel):
    id: str
    email: str
    username: Optional[str]
    full_name: Optional[str]
    company_name: Optional[str]
    user_type: str
    subscription_tier: str
    is_verified: bool
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        try:
            # Convert UUID to string for the id field
            # Convert datetime to ISO string for created_at
            data = {
                'id': str(obj.id) if obj.id else None,
                'email': str(obj.email) if obj.email else None,
                'username': str(obj.username) if obj.username else None,
                'full_name': str(obj.full_name) if obj.full_name else None,
                'company_name': str(obj.company_name) if obj.company_name else None,
                'user_type': str(obj.user_type) if obj.user_type else None,
                'subscription_tier': str(obj.subscription_tier) if obj.subscription_tier else None,
                'is_verified': bool(obj.is_verified) if obj.is_verified is not None else False,
                'is_active': bool(obj.is_active) if obj.is_active is not None else True,
                'created_at': obj.created_at.isoformat() if obj.created_at else None
            }
            return cls(**data)
        except Exception as e:
            print(f"ERROR in AdminUser.from_orm: {str(e)}")
            print(f"Object type: {type(obj)}")
            print(f"Object attributes: {dir(obj)}")
            raise

class AdminReview(BaseModel):
    id: str
    freight_forwarder_name: str
    reviewer_name: str
    rating: int
    comment: Optional[str]
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert UUID to string for the id field
        # Convert datetime to ISO string for created_at
        data = {
            'id': str(obj.id),
            'freight_forwarder_name': "Company ID: " + str(obj.freight_forwarder_id)[:8] + "..." if hasattr(obj, 'freight_forwarder_id') and obj.freight_forwarder_id else "Unknown Company",
            'reviewer_name': obj.user.username if obj.user and hasattr(obj.user, 'username') else "Anonymous",
            'rating': int(obj.aggregate_rating) if obj.aggregate_rating else 0,
            'comment': "",  # review_text field removed from database
            'status': "active" if obj.is_active else "inactive",
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
        return cls(**data)

class AdminDispute(BaseModel):
    id: str
    freight_forwarder_name: str
    issue: str
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convert UUID to string for the id field
        # Convert datetime to ISO string for created_at
        # Handle both production and development schemas
        issue = "Unknown Issue"
        if hasattr(obj, 'reason') and obj.reason:
            issue = obj.reason
        elif hasattr(obj, 'dispute_type') and obj.dispute_type:
            issue = obj.dispute_type
        elif hasattr(obj, 'description') and obj.description:
            issue = obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
        
        freight_forwarder_name = "Unknown Company"
        if hasattr(obj, 'freight_forwarder_id') and obj.freight_forwarder_id:
            # Production schema - direct ID
            freight_forwarder_name = "Company ID: " + str(obj.freight_forwarder_id)[:8] + "..."
        elif obj.freight_forwarder:
            # Development schema - relationship
            freight_forwarder_name = obj.freight_forwarder.name
        
        data = {
            'id': str(obj.id),
            'freight_forwarder_name': freight_forwarder_name,
            'issue': issue,
            'status': obj.status,
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }
        return cls(**data)

class AdminCompany(BaseModel):
    id: str
    name: str
    website: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    headquarters_country: Optional[str]
    reviews_count: int
    status: str

    class Config:
        from_attributes = True

class SubscriptionUpdate(BaseModel):
    tier: str
    payment_method_id: Optional[str] = None
    trial_days: Optional[int] = 0
    is_paid: Optional[bool] = False

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    user_type: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"
    
    def __init__(self, **data):
        # Pre-process the data to handle type conversions
        processed_data = {}
        for key, value in data.items():
            if key in ['username', 'full_name', 'email', 'company_name', 'user_type']:
                if value is not None:
                    processed_data[key] = str(value).strip() if value else None
                else:
                    processed_data[key] = None
            elif key in ['is_verified', 'is_active']:
                if value is not None:
                    processed_data[key] = bool(value)
                else:
                    processed_data[key] = None
            else:
                processed_data[key] = value
        
        super().__init__(**processed_data)

class CompanyCreate(BaseModel):
    name: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    headquarters_country: Optional[str] = None

class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    headquarters_country: Optional[str] = None
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"
    
    def __init__(self, **data):
        # Pre-process the data to handle type conversions
        processed_data = {}
        for key, value in data.items():
            if key in ['name', 'website', 'logo_url', 'description', 'headquarters_country']:
                if value is not None:
                    processed_data[key] = str(value).strip() if value else None
                else:
                    processed_data[key] = None
            else:
                processed_data[key] = value
        
        super().__init__(**processed_data)

class RecentActivity(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str
    company_name: Optional[str] = None
    user_name: Optional[str] = None

class AnalyticsData(BaseModel):
    review_growth: dict
    user_engagement: dict
    revenue_metrics: dict
    top_companies: List[dict]

# Helper function to check if user is admin
async def get_admin_user(current_user: User = Depends(get_current_user)):
    print(f"DEBUG: get_admin_user called with user: {current_user.email}, type: {current_user.user_type}")  # Debug log
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/test-auth")
async def test_admin_auth(admin_user: User = Depends(get_admin_user)):
    """Test endpoint to verify admin authentication is working"""
    return {
        "message": "Admin authentication successful",
        "user": {
            "id": str(admin_user.id),
            "email": admin_user.email,
            "user_type": admin_user.user_type
        }
    }

@router.get("/test-token")
async def test_token_validation(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify token validation without admin requirements"""
    return {
        "message": "Token validation successful",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "user_type": current_user.user_type
        }
    }

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    print(f"DEBUG: Dashboard accessed by admin user: {admin_user.email}")  # Debug log
    """Get dashboard statistics"""
    try:
        # Count total users
        total_users = db.query(User).count()
        
        # Count total companies
        total_companies = db.query(FreightForwarder).count()
        
        # Count total reviews
        total_reviews = db.query(Review).count()
        
        # Count pending disputes
        pending_disputes = db.query(Dispute).filter(Dispute.status == "open").count()
        
        # Count pending reviews (reviews that need moderation)
        # For now, we'll count all active reviews as pending moderation
        # In a real app, you might have a separate moderation status field
        pending_reviews = db.query(Review).filter(Review.is_active == True).count()
        
        # Calculate revenue (mock calculation for now)
        # In a real app, this would come from subscription payments
        total_revenue = 45600.0  # Mock value
        
        return DashboardStats(
            total_users=total_users,
            total_companies=total_companies,
            total_reviews=total_reviews,
            pending_disputes=pending_disputes,
            pending_reviews=pending_reviews,
            total_revenue=total_revenue
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard stats: {str(e)}"
        )

@router.get("/recent-activity", response_model=List[RecentActivity])
async def get_recent_activity(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get recent platform activities for admin dashboard"""
    try:
        activities = []
        
        # Get recent reviews
        recent_reviews = db.query(Review).order_by(Review.created_at.desc()).limit(limit//2).all()
        for review in recent_reviews:
            try:
                # Get user name safely
                user_name = "Anonymous"
                if review.user and hasattr(review.user, 'username'):
                    user_name = review.user.username or review.user.full_name or review.user.email or "User"
                
                # Get freight forwarder name safely - handle both schemas
                company_name = "Unknown Company"
                if hasattr(review, 'freight_forwarder_id') and review.freight_forwarder_id:
                    # Production schema - direct ID
                    freight_forwarder = db.query(FreightForwarder).filter(FreightForwarder.id == review.freight_forwarder_id).first()
                    if freight_forwarder:
                        company_name = freight_forwarder.name
                elif review.freight_forwarder and hasattr(review.freight_forwarder, 'name'):
                    # Development schema - relationship
                    company_name = review.freight_forwarder.name
                
                activities.append(RecentActivity(
                    id=str(review.id),
                    type="review",
                    message=f"New review submitted for {company_name}",
                    timestamp=review.created_at.isoformat() if review.created_at else "",
                    company_name=company_name,
                    user_name=user_name
                ))
            except Exception as e:
                print(f"Warning: Skipping review {review.id} due to error: {str(e)}")
                continue
        
        # Get recent disputes
        recent_disputes = db.query(Dispute).order_by(Dispute.created_at.desc()).limit(limit//2).all()
        for dispute in recent_disputes:
            # Get freight forwarder name - try multiple possible fields for production schema compatibility
            freight_forwarder_name = "Unknown"
            if hasattr(dispute, 'freight_forwarder_id') and dispute.freight_forwarder_id:
                # Direct freight_forwarder_id field (production schema)
                freight_forwarder = db.query(FreightForwarder).filter(FreightForwarder.id == dispute.freight_forwarder_id).first()
                if freight_forwarder:
                    freight_forwarder_name = freight_forwarder.name
            elif dispute.review and dispute.review.freight_forwarder:
                # Through review relationship (development schema)
                freight_forwarder_name = dispute.review.freight_forwarder.name
            
            # Get reporter name safely - try multiple possible fields for production schema compatibility
            reporter_name = "Unknown"
            if hasattr(dispute, 'user_id') and dispute.user_id:
                # Direct user_id field (production schema)
                user = db.query(User).filter(User.id == dispute.user_id).first()
                if user:
                    reporter_name = user.username or user.full_name or user.email or "User"
            elif hasattr(dispute, 'reported_by') and dispute.reported_by:
                # reported_by field (expected schema)
                user = db.query(User).filter(User.id == dispute.reported_by).first()
                if user:
                    reporter_name = user.username or user.full_name or user.email or "User"
            elif dispute.reporter:
                # Through reporter relationship
                reporter_name = dispute.reporter.username or dispute.reporter.full_name or dispute.reporter.email or "User"
            
            activities.append(RecentActivity(
                id=str(dispute.id),
                type="dispute",
                message=f"Dispute opened for {freight_forwarder_name} review",
                timestamp=dispute.created_at.isoformat() if dispute.created_at else "",
                company_name=freight_forwarder_name,
                user_name=reporter_name
            ))
        
        # Sort by timestamp and return limited results
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        )

@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform analytics for admin dashboard"""
    try:
        # Mock analytics data for now
        # In a real app, this would calculate actual metrics from database
        analytics = AnalyticsData(
            review_growth={
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "data": [65, 78, 90, 85, 95, 120]
            },
            user_engagement={
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "data": [1200, 1350, 1420, 1380, 1500, 1680]
            },
            revenue_metrics={
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "data": [2500, 3200, 3800, 3500, 4200, 4800]
            },
            top_companies=[
                {
                    "name": "DHL Supply Chain",
                    "reviews": 156,
                    "rating": 4.2
                },
                {
                    "name": "Kuehne + Nagel",
                    "reviews": 142,
                    "rating": 4.1
                },
                {
                    "name": "DB Schenker",
                    "reviews": 128,
                    "rating": 4.3
                }
            ]
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )

@router.get("/users", response_model=List[AdminUser])
async def get_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    user_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all users with filtering and pagination"""
    try:
        query = db.query(User)
        
        if search:
            query = query.filter(
                User.email.contains(search) | 
                User.username.contains(search) |
                User.full_name.contains(search)
            )
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        users = query.offset(skip).limit(limit).all()
        
        return [
            AdminUser(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                company_name=user.company_name,
                user_type=user.user_type,
                subscription_tier=user.subscription_tier,
                is_verified=user.is_verified,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.put("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: str,
    subscription_update: SubscriptionUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user subscription with Stripe integration"""
    try:
        from services.subscription_service import SubscriptionService
        subscription_service = SubscriptionService()
        
        # Get user first
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create subscription using the service
        subscription_result = await subscription_service.create_subscription(
            user_id=user_id,
            tier=subscription_update.tier,
            user_type=user.user_type,
            payment_method_id=subscription_update.payment_method_id,
            trial_days=subscription_update.trial_days,
            is_paid=subscription_update.is_paid,
            db=db
        )
        
        return {
            "message": "Subscription updated successfully",
            "subscription_id": subscription_result['subscription_id'],
            "status": subscription_result['status']
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=AdminUser)
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user information (admin only)"""
    try:
        # Debug logging
        print(f"DEBUG: Updating user {user_id} with data: {user_update.dict()}")
        print(f"DEBUG: user_id type: {type(user_id)}, value: {user_id}")
        print(f"DEBUG: user_update object type: {type(user_update)}")
        print(f"DEBUG: user_update fields: {user_update.__dict__}")
        
        # Validate user_id format
        try:
            import uuid
            uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
                # Get user to update
        try:
            # Check if database session is valid
            if not db.is_active:
                print(f"ERROR: Database session is not active")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session error"
                )
            
            # Test database connection with a simple query
            from sqlalchemy import text
            test_result = db.execute(text("SELECT 1")).scalar()
            print(f"DEBUG: Database connection test result: {test_result}")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            print(f"DEBUG: Found user in database: {user.email}")
        except Exception as db_query_error:
            print(f"ERROR: Database query failed: {str(db_query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query failed: {str(db_query_error)}"
            )
        
        print(f"DEBUG: Found user: {user.email}, current type: {user.user_type}")
        
        # Update fields if provided
        if user_update.username is not None:
            # Ensure username is a string and not empty
            username = str(user_update.username).strip() if user_update.username else None
            user.username = username if username else None
            print(f"DEBUG: Updated username to: {username}")
        if user_update.full_name is not None:
            # Ensure full_name is a string and not empty
            full_name = str(user_update.full_name).strip() if user_update.full_name else None
            user.full_name = full_name if full_name else None
            print(f"DEBUG: Updated full_name to: {full_name}")
        if user_update.email is not None:
            # Ensure email is a string and properly formatted
            email = str(user_update.email).lower().strip() if user_update.email else None
            if email:
                # Check if email is already taken by another user
                existing_user = db.query(User).filter(
                    User.email == email,
                    User.id != user_id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email is already taken by another user"
                    )
                user.email = email
                print(f"DEBUG: Updated email to: {email}")
        if user_update.company_name is not None:
            # Ensure company_name is a string and not empty
            company_name = str(user_update.company_name).strip() if user_update.company_name else None
            user.company_name = company_name if company_name else None
            print(f"DEBUG: Updated company_name to: {company_name}")
        if user_update.user_type is not None:
            # Ensure user_type is a string and validate it
            user_type = str(user_update.user_type).lower().strip() if user_update.user_type else None
            if user_type:
                # Validate user_type
                if user_type not in ["shipper", "forwarder", "admin"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid user type. Must be 'shipper', 'forwarder', or 'admin'"
                    )
                user.user_type = user_type
                print(f"DEBUG: Updated user_type to: {user_type}")
        if user_update.is_verified is not None:
            # Ensure is_verified is a boolean
            is_verified = bool(user_update.is_verified) if user_update.is_verified is not None else None
            user.is_verified = is_verified
            print(f"DEBUG: Updated is_verified to: {is_verified}")
        if user_update.is_active is not None:
            # Ensure is_active is a boolean
            is_active = bool(user_update.is_active) if user_update.is_active is not None else None
            user.is_active = is_active
            print(f"DEBUG: Updated is_active to: {is_active}")
        
        print(f"DEBUG: About to commit changes to database")
        try:
            # Check if there are any pending changes
            if db.is_modified(user):
                print(f"DEBUG: User object has pending changes, committing...")
                db.commit()
                print(f"DEBUG: Database commit successful")
            else:
                print(f"DEBUG: No changes detected, skipping commit")
            
            # Refresh the user object
            db.refresh(user)
            print(f"DEBUG: User object refreshed successfully")
        except Exception as db_error:
            print(f"ERROR: Database commit failed: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database update failed: {str(db_error)}"
            )
        
        print(f"DEBUG: Converting user to AdminUser model")
        try:
            # Debug the user object before conversion
            print(f"DEBUG: User object before conversion:")
            print(f"  - id: {user.id} (type: {type(user.id)})")
            print(f"  - email: {user.email} (type: {type(user.email)})")
            print(f"  - username: {user.username} (type: {type(user.username)})")
            print(f"  - full_name: {user.full_name} (type: {type(user.full_name)})")
            print(f"  - company_name: {user.company_name} (type: {type(user.company_name)})")
            print(f"  - user_type: {user.user_type} (type: {type(user.user_type)})")
            print(f"  - subscription_tier: {user.subscription_tier} (type: {type(user.subscription_tier)})")
            print(f"  - is_verified: {user.is_verified} (type: {type(user.is_verified)})")
            print(f"  - is_active: {user.is_active} (type: {type(user.is_active)})")
            print(f"  - created_at: {user.created_at} (type: {type(user.created_at)})")
            
            result = AdminUser.from_orm(user)
            print(f"DEBUG: Successfully converted to AdminUser: {result.dict()}")
            return result
        except Exception as conversion_error:
            print(f"ERROR: Failed to convert user to AdminUser: {str(conversion_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert user data: {str(conversion_error)}"
            )
        
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ERROR: Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to update user: {str(e)}")
        print(f"ERROR: Failed to update user: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.get("/reviews", response_model=List[AdminReview])
async def get_reviews(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get reviews for admin moderation"""
    try:
        query = db.query(Review).join(FreightForwarder)
        
        if status_filter:
            query = query.filter(Review.is_active == True)
        
        reviews = query.offset(skip).limit(limit).all()
        
        return [
            AdminReview(
                id=str(review.id),
                freight_forwarder_name="Company ID: " + str(review.freight_forwarder_id)[:8] + "..." if hasattr(review, 'freight_forwarder_id') and review.freight_forwarder_id else "Unknown Company",
                reviewer_name=review.user.username if review.user and hasattr(review.user, 'username') else "Anonymous",
                rating=int(review.aggregate_rating) if review.aggregate_rating else 0,
                comment="",  # review_text field removed from database
                status="active" if review.is_active else "inactive",
                created_at=review.created_at.isoformat() if review.created_at else None
            )
            for review in reviews
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviews: {str(e)}"
        )

@router.put("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Approve a review"""
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        review.is_active = True
        db.commit()
        
        return {"message": "Review approved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve review: {str(e)}"
        )

@router.put("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Reject a review"""
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        review.is_active = False
        db.commit()
        
        return {"message": "Review rejected successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject review: {str(e)}"
        )

@router.get("/disputes", response_model=List[AdminDispute])
async def get_disputes(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get disputes for admin resolution"""
    try:
        # Query disputes without join to avoid schema compatibility issues
        query = db.query(Dispute)
        
        if status_filter:
            query = query.filter(Dispute.status == status_filter)
        
        disputes = query.offset(skip).limit(limit).all()
        
        return [
            AdminDispute.from_orm(dispute) for dispute in disputes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disputes: {str(e)}"
        )

@router.put("/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Resolve a dispute"""
    try:
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found"
            )
        
        dispute.status = "resolved"
        db.commit()
        
        return {"message": "Dispute resolved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve dispute: {str(e)}"
        )

@router.get("/companies", response_model=List[AdminCompany])
async def get_companies(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all companies with stats"""
    try:
        query = db.query(FreightForwarder)
        
        if search:
            query = query.filter(FreightForwarder.name.contains(search))
        
        companies = query.offset(skip).limit(limit).all()
        
        result = []
        for company in companies:
            # Count reviews
            reviews_count = db.query(Review).filter(Review.freight_forwarder_id == company.id).count()
            
            result.append(AdminCompany(
                id=str(company.id),
                name=company.name,
                website=company.website,
                logo_url=company.logo_url,
                description=company.description,
                headquarters_country=company.headquarters_country,
                reviews_count=reviews_count,
                status="active"
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get companies: {str(e)}"
        )

@router.post("/companies", response_model=AdminCompany)
async def create_company(
    company_data: CompanyCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new company"""
    try:
        # Check if company already exists
        existing_company = db.query(FreightForwarder).filter(
            FreightForwarder.name == company_data.name
        ).first()
        
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists"
            )
        
        new_company = FreightForwarder(
            id=str(uuid.uuid4()),
            name=company_data.name,
            website=company_data.website,
            logo_url=company_data.logo_url,
            description=company_data.description,
            headquarters_country=company_data.headquarters_country
        )
        
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        
        return AdminCompany(
            id=str(new_company.id),
            name=new_company.name,
            website=new_company.website,
            logo_url=new_company.logo_url,
            description=new_company.description,
            headquarters_country=new_company.headquarters_country,
            reviews_count=0,
            status="active"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create company: {str(e)}"
        )

@router.put("/companies/{company_id}", response_model=AdminCompany)
async def update_company(
    company_id: str,
    company_update: CompanyUpdateRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update company information (admin only)"""
    try:
        # Debug logging
        print(f"DEBUG: Updating company {company_id} with data: {company_update.dict()}")
        print(f"DEBUG: company_id type: {type(company_id)}, value: {company_id}")
        
        # Validate company_id format
        try:
            import uuid
            uuid.UUID(company_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company ID format"
            )
        
        # Check if database session is valid
        try:
            if not db.is_active:
                print(f"ERROR: Database session is not active")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session error"
                )
            
            # Test database connection with a simple query
            from sqlalchemy import text
            test_result = db.execute(text("SELECT 1")).scalar()
            print(f"DEBUG: Database connection test result: {test_result}")
            
            # Get company to update
            company = db.query(FreightForwarder).filter(FreightForwarder.id == company_id).first()
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            print(f"DEBUG: Found company in database: {company.name}")
        except Exception as db_query_error:
            print(f"ERROR: Database query failed: {str(db_query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query failed: {str(db_query_error)}"
            )
        
        # Update fields if provided
        if company_update.name is not None:
            # Check if name is already taken by another company
            existing_company = db.query(FreightForwarder).filter(
                FreightForwarder.name == company_update.name,
                FreightForwarder.id != company_id
            ).first()
            if existing_company:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company with this name already exists"
                )
            
            # Ensure name is a string and not empty
            name = str(company_update.name).strip() if company_update.name else None
            company.name = name if name else company.name
            print(f"DEBUG: Updated name to: {name}")
        
        if company_update.website is not None:
            # Ensure website is a string and not empty
            website = str(company_update.website).strip() if company_update.website else None
            company.website = website if website else None
            print(f"DEBUG: Updated website to: {website}")
        
        if company_update.logo_url is not None:
            # Ensure logo_url is a string and not empty
            logo_url = str(company_update.logo_url).strip() if company_update.logo_url else None
            company.logo_url = logo_url if logo_url else None
            print(f"DEBUG: Updated logo_url to: {logo_url}")
        
        if company_update.description is not None:
            # Ensure description is a string and not empty
            description = str(company_update.description).strip() if company_update.description else None
            company.description = description if description else None
            print(f"DEBUG: Updated description to: {description}")
        
        if company_update.headquarters_country is not None:
            # Ensure headquarters_country is a string and not empty
            headquarters_country = str(company_update.headquarters_country).strip() if company_update.headquarters_country else None
            company.headquarters_country = headquarters_country if headquarters_country else None
            print(f"DEBUG: Updated headquarters_country to: {headquarters_country}")
        
        print(f"DEBUG: About to commit changes to database")
        try:
            # Check if there are any pending changes
            if db.is_modified(company):
                print(f"DEBUG: Company object has pending changes, committing...")
                db.commit()
                print(f"DEBUG: Database commit successful")
            else:
                print(f"DEBUG: No changes detected, skipping commit")
            
            # Refresh the company object
            db.refresh(company)
            print(f"DEBUG: Company object refreshed successfully")
        except Exception as db_error:
            print(f"ERROR: Database commit failed: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database update failed: {str(db_error)}"
            )
        
        print(f"DEBUG: Converting company to AdminCompany model")
        try:
            # Count reviews for the updated company
            reviews_count = db.query(Review).filter(Review.freight_forwarder_id == company.id).count()
            
            result = AdminCompany(
                id=str(company.id),
                name=company.name,
                website=company.website,
                logo_url=company.logo_url,
                reviews_count=reviews_count,
                status="active"
            )
            print(f"DEBUG: Successfully converted to AdminCompany: {result.dict()}")
            return result
        except Exception as conversion_error:
            print(f"ERROR: Failed to convert company to AdminCompany: {str(conversion_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to convert company data: {str(conversion_error)}"
            )
        
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ERROR: Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to update company: {str(e)}")
        print(f"ERROR: Failed to update company: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update company: {str(e)}"
        )

@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a company (admin only)"""
    try:
        # Debug logging
        print(f"DEBUG: Deleting company {company_id}")
        print(f"DEBUG: company_id type: {type(company_id)}, value: {company_id}")
        
        # Validate company_id format
        try:
            import uuid
            uuid.UUID(company_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company ID format"
            )
        
        # Check if database session is valid
        try:
            if not db.is_active:
                print(f"ERROR: Database session is not active")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session error"
                )
            
            # Test database connection with a simple query
            from sqlalchemy import text
            test_result = db.execute(text("SELECT 1")).scalar()
            print(f"DEBUG: Database connection test result: {test_result}")
            
            # Get company to delete
            company = db.query(FreightForwarder).filter(FreightForwarder.id == company_id).first()
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            print(f"DEBUG: Found company in database: {company.name}")
        except Exception as db_query_error:
            print(f"ERROR: Database query failed: {str(db_query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query failed: {str(db_query_error)}"
            )
        
        # Check if company has any reviews
        reviews_count = db.query(Review).filter(Review.freight_forwarder_id == company.id).count()
        
        if reviews_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete company. It has {reviews_count} reviews. Please remove all reviews first."
            )
        
        print(f"DEBUG: About to delete company from database")
        try:
            db.delete(company)
            db.commit()
            print(f"DEBUG: Company deleted successfully")
        except Exception as db_error:
            print(f"ERROR: Database delete failed: {str(db_error)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database delete failed: {str(db_error)}"
            )
        
        return {"message": f"Company '{company.name}' deleted successfully"}
        
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ERROR: Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to delete company: {str(e)}")
        print(f"ERROR: Failed to delete company: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete company: {str(e)}"
        )

@router.get("/companies/{company_id}", response_model=AdminCompany)
async def get_company(
    company_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get company details by ID (admin only)"""
    try:
        # Debug logging
        print(f"DEBUG: Getting company {company_id}")
        print(f"DEBUG: company_id type: {type(company_id)}, value: {company_id}")
        
        # Validate company_id format
        try:
            import uuid
            uuid.UUID(company_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company ID format"
            )
        
        # Check if database session is valid
        try:
            if not db.is_active:
                print(f"ERROR: Database session is not active")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session error"
                )
            
            # Test database connection with a simple query
            from sqlalchemy import text
            test_result = db.execute(text("SELECT 1")).scalar()
            print(f"DEBUG: Database connection test result: {test_result}")
            
            # Get company by ID
            company = db.query(FreightForwarder).filter(FreightForwarder.id == company_id).first()
            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Company not found"
                )
            print(f"DEBUG: Found company in database: {company.name}")
        except Exception as db_query_error:
            print(f"ERROR: Database query failed: {str(db_query_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query failed: {str(db_query_error)}"
            )
        
        # Count reviews for the company
        reviews_count = db.query(Review).filter(Review.freight_forwarder_id == company.id).count()
        
        result = AdminCompany(
            id=str(company.id),
            name=company.name,
            website=company.website,
            logo_url=company.logo_url,
            reviews_count=reviews_count,
            status="active"
        )
        print(f"DEBUG: Successfully retrieved company: {result.dict()}")
        return result
        
    except HTTPException:
        raise
    except ValueError as ve:
        print(f"ERROR: Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to get company: {str(e)}")
        print(f"ERROR: Failed to get company: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get company: {str(e)}"
        ) 