from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from database.database import get_db
from database.models import User, ReviewSubscription, FreightForwarder
from auth.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ReviewSubscriptionCreate(BaseModel):
    freight_forwarder_id: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    review_type: Optional[str] = None
    notification_frequency: str = "immediate"

class ReviewSubscriptionUpdate(BaseModel):
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    review_type: Optional[str] = None
    notification_frequency: Optional[str] = None
    is_active: Optional[bool] = None

class ReviewSubscriptionResponse(BaseModel):
    id: str
    freight_forwarder_id: Optional[str] = None
    freight_forwarder_name: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    review_type: Optional[str] = None
    notification_frequency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=ReviewSubscriptionResponse)
async def create_review_subscription(
    subscription: ReviewSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new review subscription for the user"""
    try:
        # Validate that at least one filter is specified
        if not any([
            subscription.freight_forwarder_id,
            subscription.location_country,
            subscription.location_city,
            subscription.review_type
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one filter (freight_forwarder, location, or review_type) must be specified"
            )
        
        # Validate freight_forwarder_id if provided
        if subscription.freight_forwarder_id:
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == subscription.freight_forwarder_id
            ).first()
            if not freight_forwarder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Freight forwarder not found"
                )
        
        # Check if subscription already exists
        existing_subscription = db.query(ReviewSubscription).filter(
            ReviewSubscription.user_id == current_user.id,
            ReviewSubscription.freight_forwarder_id == subscription.freight_forwarder_id,
            ReviewSubscription.location_country == subscription.location_country,
            ReviewSubscription.location_city == subscription.location_city,
            ReviewSubscription.review_type == subscription.review_type
        ).first()
        
        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A subscription with these exact filters already exists"
            )
        
        # Create new subscription
        db_subscription = ReviewSubscription(
            user_id=current_user.id,
            freight_forwarder_id=subscription.freight_forwarder_id,
            location_country=subscription.location_country,
            location_city=subscription.location_city,
            review_type=subscription.review_type,
            notification_frequency=subscription.notification_frequency
        )
        
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        # Get freight forwarder name for response
        freight_forwarder_name = None
        if db_subscription.freight_forwarder_id:
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == db_subscription.freight_forwarder_id
            ).first()
            freight_forwarder_name = freight_forwarder.name if freight_forwarder else None
        
        return ReviewSubscriptionResponse(
            id=str(db_subscription.id),
            freight_forwarder_id=str(db_subscription.freight_forwarder_id) if db_subscription.freight_forwarder_id else None,
            freight_forwarder_name=freight_forwarder_name,
            location_country=db_subscription.location_country,
            location_city=db_subscription.location_city,
            review_type=db_subscription.review_type,
            notification_frequency=db_subscription.notification_frequency,
            is_active=db_subscription.is_active,
            created_at=db_subscription.created_at,
            updated_at=db_subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create review subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review subscription: {str(e)}"
        )

@router.get("/", response_model=List[ReviewSubscriptionResponse])
async def get_user_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all review subscriptions for the current user"""
    try:
        subscriptions = db.query(ReviewSubscription).filter(
            ReviewSubscription.user_id == current_user.id
        ).all()
        
        # Get freight forwarder names for response
        result = []
        for subscription in subscriptions:
            freight_forwarder_name = None
            if subscription.freight_forwarder_id:
                freight_forwarder = db.query(FreightForwarder).filter(
                    FreightForwarder.id == subscription.freight_forwarder_id
                ).first()
                freight_forwarder_name = freight_forwarder.name if freight_forwarder else None
            
            result.append(ReviewSubscriptionResponse(
                id=str(subscription.id),
                freight_forwarder_id=str(subscription.freight_forwarder_id) if subscription.freight_forwarder_id else None,
                freight_forwarder_name=freight_forwarder_name,
                location_country=subscription.location_country,
                location_city=subscription.location_city,
                review_type=subscription.review_type,
                notification_frequency=subscription.notification_frequency,
                is_active=subscription.is_active,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get user subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user subscriptions: {str(e)}"
        )

@router.get("/{subscription_id}", response_model=ReviewSubscriptionResponse)
async def get_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific review subscription by ID"""
    try:
        subscription = db.query(ReviewSubscription).filter(
            ReviewSubscription.id == subscription_id,
            ReviewSubscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Get freight forwarder name for response
        freight_forwarder_name = None
        if subscription.freight_forwarder_id:
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == subscription.freight_forwarder_id
            ).first()
            freight_forwarder_name = freight_forwarder.name if freight_forwarder else None
        
        return ReviewSubscriptionResponse(
            id=str(subscription.id),
            freight_forwarder_id=str(subscription.freight_forwarder_id) if subscription.freight_forwarder_id else None,
            freight_forwarder_name=freight_forwarder_name,
            location_country=subscription.location_country,
            location_city=subscription.location_city,
            review_type=subscription.review_type,
            notification_frequency=subscription.notification_frequency,
            is_active=subscription.is_active,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription: {str(e)}"
        )

@router.put("/{subscription_id}", response_model=ReviewSubscriptionResponse)
async def update_subscription(
    subscription_id: str,
    subscription_update: ReviewSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review subscription"""
    try:
        subscription = db.query(ReviewSubscription).filter(
            ReviewSubscription.id == subscription_id,
            ReviewSubscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Update fields if provided
        if subscription_update.location_country is not None:
            subscription.location_country = subscription_update.location_country
        if subscription_update.location_city is not None:
            subscription.location_city = subscription_update.location_city
        if subscription_update.review_type is not None:
            subscription.review_type = subscription_update.review_type
        if subscription_update.notification_frequency is not None:
            subscription.notification_frequency = subscription_update.notification_frequency
        if subscription_update.is_active is not None:
            subscription.is_active = subscription_update.is_active
        
        subscription.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(subscription)
        
        # Get freight forwarder name for response
        freight_forwarder_name = None
        if subscription.freight_forwarder_id:
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == subscription.freight_forwarder_id
            ).first()
            freight_forwarder_name = freight_forwarder.name if freight_forwarder else None
        
        return ReviewSubscriptionResponse(
            id=str(subscription.id),
            freight_forwarder_id=str(subscription.freight_forwarder_id) if subscription.freight_forwarder_id else None,
            freight_forwarder_name=freight_forwarder_name,
            location_country=subscription.location_country,
            location_city=subscription.location_city,
            review_type=subscription.review_type,
            notification_frequency=subscription.notification_frequency,
            is_active=subscription.is_active,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review subscription"""
    try:
        subscription = db.query(ReviewSubscription).filter(
            ReviewSubscription.id == subscription_id,
            ReviewSubscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # First, delete all related notifications
        from database.models import ReviewNotification
        notifications = db.query(ReviewNotification).filter(
            ReviewNotification.subscription_id == subscription_id
        ).all()
        
        for notification in notifications:
            db.delete(notification)
        
        # Then delete the subscription
        db.delete(subscription)
        db.commit()
        
        logger.info(f"Deleted review subscription {subscription_id} and {len(notifications)} related notifications for user {current_user.id}")
        
        return {"message": "Subscription deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscription: {str(e)}"
        )

@router.post("/{subscription_id}/toggle")
async def toggle_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle subscription active status"""
    try:
        subscription = db.query(ReviewSubscription).filter(
            ReviewSubscription.id == subscription_id,
            ReviewSubscription.user_id == current_user.id
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        subscription.is_active = not subscription.is_active
        subscription.updated_at = datetime.utcnow()
        db.commit()
        
        status_text = "activated" if subscription.is_active else "deactivated"
        return {"message": f"Subscription {status_text} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle subscription: {str(e)}"
        )
