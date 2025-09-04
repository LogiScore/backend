from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import uuid

from database.database import get_db
from database.models import User, Review, ReviewSubscription, ReviewNotification, FreightForwarder
from auth.auth import get_current_user, get_current_user_optional
from email_service import EmailService
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize email service
email_service = EmailService()

# Pydantic models for request/response
class ReviewNotificationTrigger(BaseModel):
    review_id: str
    freight_forwarder_id: str
    freight_forwarder_name: str
    country: str
    city: str
    reviewer_name: str
    rating: float
    review_text: str
    created_at: datetime
    category_scores: Optional[List[dict]] = []

class SubscriptionCleanupRequest(BaseModel):
    user_id: str
    old_subscription_tier: str
    new_subscription_tier: str
    cleanup_reason: str  # downgrade, expiry, cancellation

class NotificationStatusResponse(BaseModel):
    user_id: str
    total_subscriptions: int
    active_subscriptions: int
    last_notification_sent: Optional[datetime]
    notifications_sent_today: int
    subscription_types: dict

class NotificationTriggerResponse(BaseModel):
    message: str
    notifications_sent: int
    subscriptions_matched: List[str]

class CleanupResponse(BaseModel):
    message: str
    deleted_subscriptions: int
    deleted_subscription_ids: List[str]

@router.post("/trigger-review-notification", response_model=NotificationTriggerResponse)
async def trigger_review_notification(
    notification_data: ReviewNotificationTrigger,
    db: Session = Depends(get_db)
):
    """
    Trigger email notifications for a new review submission.
    This endpoint is called internally when a new review is created.
    """
    try:
        logger.info(f"Triggering review notifications for review {notification_data.review_id}")
        
        # Find all active subscriptions that match the review criteria
        matching_subscriptions = db.query(ReviewSubscription).filter(
            and_(
                ReviewSubscription.is_active == True,
                or_(
                    # Company-specific subscription
                    ReviewSubscription.freight_forwarder_id == notification_data.freight_forwarder_id,
                    # Country-specific subscription (no city specified)
                    and_(
                        ReviewSubscription.location_country == notification_data.country,
                        ReviewSubscription.location_city.is_(None)
                    ),
                    # City-specific subscription
                    and_(
                        ReviewSubscription.location_country == notification_data.country,
                        ReviewSubscription.location_city == notification_data.city
                    )
                )
            )
        ).all()
        
        logger.info(f"Found {len(matching_subscriptions)} matching subscriptions")
        
        notifications_sent = 0
        subscription_ids = []
        
        # Send email notifications to each matching subscriber
        for subscription in matching_subscriptions:
            try:
                # Get user details
                user = db.query(User).filter(User.id == subscription.user_id).first()
                if not user or not user.email:
                    logger.warning(f"User {subscription.user_id} not found or has no email")
                    continue
                
                # Create notification log entry
                notification_log = ReviewNotification(
                    user_id=subscription.user_id,
                    review_id=notification_data.review_id,
                    subscription_id=subscription.id,
                    notification_type='new_review',
                    is_sent=False
                )
                db.add(notification_log)
                
                # Send email notification
                email_sent = await email_service.send_review_notification(
                    to_email=user.email,
                    user_name=user.full_name or user.username or "User",
                    review_data={
                        'freight_forwarder_name': notification_data.freight_forwarder_name,
                        'country': notification_data.country,
                        'city': notification_data.city,
                        'reviewer_name': notification_data.reviewer_name,
                        'rating': notification_data.rating,
                        'review_text': notification_data.review_text,
                        'created_at': notification_data.created_at,
                        'category_scores': notification_data.category_scores
                    },
                    subscription_type=_get_subscription_type(subscription)
                )
                
                if email_sent:
                    notification_log.is_sent = True
                    notification_log.sent_at = datetime.utcnow()
                    notifications_sent += 1
                    subscription_ids.append(str(subscription.id))
                    logger.info(f"Notification sent to {user.email}")
                else:
                    logger.error(f"Failed to send notification to {user.email}")
                
            except Exception as e:
                logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
                continue
        
        # Commit all notification logs
        db.commit()
        
        logger.info(f"Review notification process completed. Sent {notifications_sent} notifications")
        
        return NotificationTriggerResponse(
            message="Notifications sent successfully",
            notifications_sent=notifications_sent,
            subscriptions_matched=subscription_ids
        )
        
    except Exception as e:
        logger.error(f"Error in trigger_review_notification: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger notifications: {str(e)}"
        )

@router.post("/cleanup-subscriptions", response_model=CleanupResponse)
async def cleanup_subscriptions(
    cleanup_data: SubscriptionCleanupRequest,
    db: Session = Depends(get_db)
):
    """
    Remove all notification subscriptions when a user's subscription is downgraded.
    This endpoint is called from Stripe webhook handlers.
    """
    try:
        logger.info(f"Cleaning up subscriptions for user {cleanup_data.user_id}")
        
        # Find all review subscriptions for the user
        user_subscriptions = db.query(ReviewSubscription).filter(
            ReviewSubscription.user_id == cleanup_data.user_id
        ).all()
        
        deleted_count = len(user_subscriptions)
        deleted_ids = [str(sub.id) for sub in user_subscriptions]
        
        # Delete all subscriptions
        for subscription in user_subscriptions:
            db.delete(subscription)
        
        # Get user details for confirmation email
        user = db.query(User).filter(User.id == cleanup_data.user_id).first()
        
        # Commit the deletions
        db.commit()
        
        # Send confirmation email if user exists
        if user and user.email:
            try:
                await email_service.send_subscription_cleanup_notice(
                    to_email=user.email,
                    user_name=user.full_name or user.username or "User",
                    cleanup_reason=cleanup_data.cleanup_reason,
                    old_tier=cleanup_data.old_subscription_tier,
                    new_tier=cleanup_data.new_subscription_tier
                )
                logger.info(f"Cleanup confirmation email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send cleanup confirmation email: {str(e)}")
        
        logger.info(f"Cleaned up {deleted_count} subscriptions for user {cleanup_data.user_id}")
        
        return CleanupResponse(
            message="Subscriptions cleaned up successfully",
            deleted_subscriptions=deleted_count,
            deleted_subscription_ids=deleted_ids
        )
        
    except Exception as e:
        logger.error(f"Error in cleanup_subscriptions: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup subscriptions: {str(e)}"
        )

@router.get("/status/{user_id}", response_model=NotificationStatusResponse)
async def get_notification_status(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification delivery status for a user.
    Users can only view their own notification status.
    """
    try:
        # Validate user access
        if str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own notification status"
            )
        
        # Get user's subscriptions
        subscriptions = db.query(ReviewSubscription).filter(
            ReviewSubscription.user_id == user_id
        ).all()
        
        total_subscriptions = len(subscriptions)
        active_subscriptions = len([s for s in subscriptions if s.is_active])
        
        # Get notification statistics
        today = datetime.utcnow().date()
        notifications_today = db.query(ReviewNotification).filter(
            and_(
                ReviewNotification.user_id == user_id,
                ReviewNotification.is_sent == True,
                ReviewNotification.sent_at >= today
            )
        ).count()
        
        # Get last notification sent
        last_notification = db.query(ReviewNotification).filter(
            and_(
                ReviewNotification.user_id == user_id,
                ReviewNotification.is_sent == True
            )
        ).order_by(ReviewNotification.sent_at.desc()).first()
        
        # Count subscription types
        subscription_types = {
            'company': len([s for s in subscriptions if s.freight_forwarder_id]),
            'country': len([s for s in subscriptions if s.location_country and not s.location_city]),
            'city': len([s for s in subscriptions if s.location_city])
        }
        
        return NotificationStatusResponse(
            user_id=user_id,
            total_subscriptions=total_subscriptions,
            active_subscriptions=active_subscriptions,
            last_notification_sent=last_notification.sent_at if last_notification else None,
            notifications_sent_today=notifications_today,
            subscription_types=subscription_types
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_notification_status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification status: {str(e)}"
        )

def _get_subscription_type(subscription: ReviewSubscription) -> str:
    """Helper function to determine subscription type for email template"""
    if subscription.freight_forwarder_id:
        return "company"
    elif subscription.location_city:
        return "city"
    elif subscription.location_country:
        return "country"
    else:
        return "general"
