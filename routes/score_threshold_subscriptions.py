from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
import logging
from datetime import datetime

from database.database import get_db
from database.models import User, FreightForwarder, ScoreThresholdSubscription, ScoreThresholdNotification
from auth.auth import get_current_user

router = APIRouter(tags=["score-threshold-subscriptions"])
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ScoreThresholdSubscriptionRequest(BaseModel):
    freight_forwarder_id: UUID
    threshold_score: Optional[float] = Field(None, ge=0.0, le=5.0, description="Score threshold between 0 and 5")
    threshold_value: Optional[float] = Field(None, ge=0.0, le=5.0, description="Score threshold value (alternative to threshold_score)")
    threshold_type: Optional[str] = Field(None, description="Threshold type (for frontend compatibility)")
    freight_forwarder_name: Optional[str] = Field(None, description="Freight forwarder name (for frontend compatibility)")
    notification_frequency: str = Field(default="immediate", description="Notification frequency: immediate, daily, or weekly")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Use threshold_value if threshold_score is not provided (frontend compatibility)
        if self.threshold_score is None and self.threshold_value is not None:
            self.threshold_score = self.threshold_value
        elif self.threshold_score is None:
            raise ValueError("Either threshold_score or threshold_value must be provided")

class ScoreThresholdSubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    freight_forwarder_id: UUID
    freight_forwarder_name: str
    threshold_score: float
    notification_frequency: str
    is_active: bool
    expires_at: Optional[datetime]
    last_notification_sent: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScoreThresholdSubscriptionUpdate(BaseModel):
    threshold_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    notification_frequency: Optional[str] = Field(None, description="immediate, daily, or weekly")
    is_active: Optional[bool] = None

class ScoreThresholdSubscriptionListResponse(BaseModel):
    subscriptions: List[ScoreThresholdSubscriptionResponse]
    total_count: int

@router.post("/", response_model=ScoreThresholdSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_score_threshold_subscription(
    subscription_request: ScoreThresholdSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new score threshold subscription for a shipper with annual subscription"""
    try:
        # Check if user has annual subscription
        if current_user.subscription_tier != 'annual' or current_user.subscription_status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Score threshold notifications are only available for users with active annual subscriptions"
            )
        
        # Set expiry date to match user's subscription end date
        expires_at = current_user.subscription_end_date
        
        # Validate freight forwarder exists
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == subscription_request.freight_forwarder_id
        ).first()
        
        if not freight_forwarder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Freight forwarder not found"
            )
        
        # Check if user already has a subscription for this freight forwarder
        existing_subscription = db.query(ScoreThresholdSubscription).filter(
            and_(
                ScoreThresholdSubscription.user_id == current_user.id,
                ScoreThresholdSubscription.freight_forwarder_id == subscription_request.freight_forwarder_id
            )
        ).first()
        
        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a score threshold subscription for this freight forwarder"
            )
        
        # Validate notification frequency
        valid_frequencies = ['immediate', 'daily', 'weekly']
        if subscription_request.notification_frequency not in valid_frequencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification frequency. Must be one of: {', '.join(valid_frequencies)}"
            )
        
        # Ensure threshold_score is set (from either threshold_score or threshold_value)
        if subscription_request.threshold_score is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either threshold_score or threshold_value must be provided"
            )
        
        # Create the subscription
        subscription = ScoreThresholdSubscription(
            user_id=current_user.id,
            freight_forwarder_id=subscription_request.freight_forwarder_id,
            threshold_score=subscription_request.threshold_score,
            notification_frequency=subscription_request.notification_frequency,
            is_active=True,
            expires_at=expires_at
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Created score threshold subscription for user {current_user.id} and forwarder {subscription_request.freight_forwarder_id}")
        
        return ScoreThresholdSubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            freight_forwarder_id=subscription.freight_forwarder_id,
            freight_forwarder_name=freight_forwarder.name,
            threshold_score=float(subscription.threshold_score),
            notification_frequency=subscription.notification_frequency,
            is_active=subscription.is_active,
            expires_at=subscription.expires_at,
            last_notification_sent=subscription.last_notification_sent,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create score threshold subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/", response_model=ScoreThresholdSubscriptionListResponse)
async def get_user_score_threshold_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all score threshold subscriptions for the current user"""
    try:
        from datetime import datetime
        
        subscriptions = db.query(ScoreThresholdSubscription).filter(
            ScoreThresholdSubscription.user_id == current_user.id
        ).all()
        
        subscription_responses = []
        current_time = datetime.utcnow()
        
        for subscription in subscriptions:
            # Check if subscription is expired
            is_expired = subscription.expires_at and subscription.expires_at < current_time
            
            # If expired, deactivate it
            if is_expired and subscription.is_active:
                subscription.is_active = False
                subscription.updated_at = current_time
                db.commit()
            
            # Get freight forwarder name
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == subscription.freight_forwarder_id
            ).first()
            
            subscription_responses.append(ScoreThresholdSubscriptionResponse(
                id=subscription.id,
                user_id=subscription.user_id,
                freight_forwarder_id=subscription.freight_forwarder_id,
                freight_forwarder_name=freight_forwarder.name if freight_forwarder else "Unknown",
                threshold_score=float(subscription.threshold_score),
                notification_frequency=subscription.notification_frequency,
                is_active=subscription.is_active and not is_expired,
                expires_at=subscription.expires_at,
                last_notification_sent=subscription.last_notification_sent,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            ))
        
        return ScoreThresholdSubscriptionListResponse(
            subscriptions=subscription_responses,
            total_count=len(subscription_responses)
        )
        
    except Exception as e:
        logger.error(f"Failed to get score threshold subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscriptions: {str(e)}"
        )

@router.put("/{subscription_id}", response_model=ScoreThresholdSubscriptionResponse)
async def update_score_threshold_subscription(
    subscription_id: UUID,
    update_request: ScoreThresholdSubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a score threshold subscription"""
    try:
        # Get the subscription
        subscription = db.query(ScoreThresholdSubscription).filter(
            and_(
                ScoreThresholdSubscription.id == subscription_id,
                ScoreThresholdSubscription.user_id == current_user.id
            )
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Score threshold subscription not found"
            )
        
        # Update fields if provided
        if update_request.threshold_score is not None:
            subscription.threshold_score = update_request.threshold_score
        
        if update_request.notification_frequency is not None:
            valid_frequencies = ['immediate', 'daily', 'weekly']
            if update_request.notification_frequency not in valid_frequencies:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid notification frequency. Must be one of: {', '.join(valid_frequencies)}"
                )
            subscription.notification_frequency = update_request.notification_frequency
        
        if update_request.is_active is not None:
            subscription.is_active = update_request.is_active
        
        subscription.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subscription)
        
        # Get freight forwarder name for response
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == subscription.freight_forwarder_id
        ).first()
        
        return ScoreThresholdSubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            freight_forwarder_id=subscription.freight_forwarder_id,
            freight_forwarder_name=freight_forwarder.name if freight_forwarder else "Unknown",
            threshold_score=float(subscription.threshold_score),
            notification_frequency=subscription.notification_frequency,
            is_active=subscription.is_active,
            expires_at=subscription.expires_at,
            last_notification_sent=subscription.last_notification_sent,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update score threshold subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.delete("/{subscription_id}")
async def delete_score_threshold_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a score threshold subscription"""
    try:
        # Get the subscription
        subscription = db.query(ScoreThresholdSubscription).filter(
            and_(
                ScoreThresholdSubscription.id == subscription_id,
                ScoreThresholdSubscription.user_id == current_user.id
            )
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Score threshold subscription not found"
            )
        
        # Delete the subscription
        db.delete(subscription)
        db.commit()
        
        logger.info(f"Deleted score threshold subscription {subscription_id} for user {current_user.id}")
        
        return {"message": "Score threshold subscription deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete score threshold subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subscription: {str(e)}"
        )

@router.get("/notifications", response_model=List[dict])
async def get_score_threshold_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get recent score threshold notifications for the current user"""
    try:
        notifications = db.query(ScoreThresholdNotification).filter(
            ScoreThresholdNotification.user_id == current_user.id
        ).order_by(ScoreThresholdNotification.created_at.desc()).limit(limit).all()
        
        notification_responses = []
        for notification in notifications:
            # Get freight forwarder name
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == notification.freight_forwarder_id
            ).first()
            
            notification_responses.append({
                "id": str(notification.id),
                "freight_forwarder_name": freight_forwarder.name if freight_forwarder else "Unknown",
                "previous_score": float(notification.previous_score),
                "current_score": float(notification.current_score),
                "threshold_score": float(notification.threshold_score),
                "notification_type": notification.notification_type,
                "is_sent": notification.is_sent,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "created_at": notification.created_at.isoformat()
            })
        
        return notification_responses
        
    except Exception as e:
        logger.error(f"Failed to get score threshold notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve notifications: {str(e)}"
        )

@router.get("/available-forwarders", response_model=List[dict])
async def get_available_freight_forwarders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = None
):
    """Get list of freight forwarders that can be monitored (have reviews)"""
    try:
        # Query freight forwarders that have reviews
        query = db.query(FreightForwarder).filter(
            FreightForwarder.id.in_(
                db.query(FreightForwarder.id).join(
                    FreightForwarder.reviews
                ).distinct()
            )
        )
        
        if search:
            query = query.filter(FreightForwarder.name.ilike(f"%{search}%"))
        
        freight_forwarders = query.limit(100).all()
        
        # Get current average scores for each forwarder
        forwarder_list = []
        for ff in freight_forwarders:
            # Calculate current average score
            total_rating = sum(review.aggregate_rating or 0 for review in ff.reviews if review.aggregate_rating is not None)
            valid_reviews = sum(1 for review in ff.reviews if review.aggregate_rating is not None)
            current_score = total_rating / valid_reviews if valid_reviews > 0 else 0.0
            
            forwarder_list.append({
                "id": str(ff.id),
                "name": ff.name,
                "current_average_score": round(current_score, 2),
                "total_reviews": len(ff.reviews),
                "website": ff.website,
                "headquarters_country": ff.headquarters_country
            })
        
        return forwarder_list
        
    except Exception as e:
        logger.error(f"Failed to get available freight forwarders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve freight forwarders: {str(e)}"
        )

@router.post("/{subscription_id}/toggle", response_model=ScoreThresholdSubscriptionResponse)
async def toggle_score_threshold_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle the active status of a score threshold subscription"""
    try:
        # Get the subscription
        subscription = db.query(ScoreThresholdSubscription).filter(
            and_(
                ScoreThresholdSubscription.id == subscription_id,
                ScoreThresholdSubscription.user_id == current_user.id
            )
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Score threshold subscription not found"
            )
        
        # Check if subscription is expired
        current_time = datetime.utcnow()
        is_expired = subscription.expires_at and subscription.expires_at < current_time
        
        if is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot toggle expired subscription. Please renew your subscription to reactivate."
            )
        
        # Toggle the active status
        subscription.is_active = not subscription.is_active
        subscription.updated_at = current_time
        
        db.commit()
        db.refresh(subscription)
        
        # Get freight forwarder name for response
        freight_forwarder = db.query(FreightForwarder).filter(
            FreightForwarder.id == subscription.freight_forwarder_id
        ).first()
        
        logger.info(f"Toggled score threshold subscription {subscription_id} to {'active' if subscription.is_active else 'inactive'} for user {current_user.id}")
        
        return ScoreThresholdSubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            freight_forwarder_id=subscription.freight_forwarder_id,
            freight_forwarder_name=freight_forwarder.name if freight_forwarder else "Unknown",
            threshold_score=float(subscription.threshold_score),
            notification_frequency=subscription.notification_frequency,
            is_active=subscription.is_active,
            expires_at=subscription.expires_at,
            last_notification_sent=subscription.last_notification_sent,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle score threshold subscription: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle subscription: {str(e)}"
        )
