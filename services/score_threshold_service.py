import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from database.models import (
    User, FreightForwarder, ScoreThresholdSubscription, 
    ScoreThresholdNotification, Review
)
from email_service import EmailService

logger = logging.getLogger(__name__)

class ScoreThresholdService:
    """Service for handling score threshold notifications and subscription management"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    async def cleanup_expired_subscriptions(self, db: Session) -> int:
        """Clean up expired score threshold subscriptions"""
        try:
            current_time = datetime.utcnow()
            
            # Find expired subscriptions
            expired_subscriptions = db.query(ScoreThresholdSubscription).filter(
                and_(
                    ScoreThresholdSubscription.is_active == True,
                    ScoreThresholdSubscription.expires_at < current_time
                )
            ).all()
            
            count = 0
            for subscription in expired_subscriptions:
                subscription.is_active = False
                subscription.updated_at = current_time
                count += 1
                
                logger.info(f"Deactivated expired score threshold subscription {subscription.id} for user {subscription.user_id}")
            
            if count > 0:
                db.commit()
                logger.info(f"Deactivated {count} expired score threshold subscriptions")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired subscriptions: {str(e)}")
            db.rollback()
            return 0
    
    async def check_score_thresholds(self, freight_forwarder_id: str, db: Session) -> bool:
        """Check if any score thresholds have been breached for a specific freight forwarder"""
        try:
            # Get current average score for the freight forwarder
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == freight_forwarder_id
            ).first()
            
            if not freight_forwarder:
                logger.warning(f"Freight forwarder {freight_forwarder_id} not found")
                return False
            
            # Calculate current average score
            current_score = self._calculate_average_score(freight_forwarder)
            
            # Get active subscriptions for this freight forwarder
            subscriptions = db.query(ScoreThresholdSubscription).filter(
                and_(
                    ScoreThresholdSubscription.freight_forwarder_id == freight_forwarder_id,
                    ScoreThresholdSubscription.is_active == True,
                    or_(
                        ScoreThresholdSubscription.expires_at.is_(None),
                        ScoreThresholdSubscription.expires_at > datetime.utcnow()
                    )
                )
            ).all()
            
            notifications_sent = 0
            for subscription in subscriptions:
                try:
                    # Check if threshold has been breached
                    if current_score < subscription.threshold_score:
                        # Check if we should send notification based on frequency
                        if self._should_send_notification(subscription):
                            await self._send_threshold_breach_notification(
                                subscription, current_score, db
                            )
                            notifications_sent += 1
                            
                except Exception as e:
                    logger.error(f"Failed to process subscription {subscription.id}: {str(e)}")
                    continue
            
            if notifications_sent > 0:
                logger.info(f"Sent {notifications_sent} score threshold notifications for freight forwarder {freight_forwarder_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check score thresholds for freight forwarder {freight_forwarder_id}: {str(e)}")
            return False
    
    def _calculate_average_score(self, freight_forwarder: FreightForwarder) -> float:
        """Calculate current average score for a freight forwarder"""
        try:
            if not freight_forwarder.reviews:
                return 0.0
            
            total_rating = sum(
                review.aggregate_rating or 0 
                for review in freight_forwarder.reviews 
                if review.aggregate_rating is not None
            )
            valid_reviews = sum(
                1 for review in freight_forwarder.reviews 
                if review.aggregate_rating is not None
            )
            
            if valid_reviews == 0:
                return 0.0
            
            return total_rating / valid_reviews
            
        except Exception as e:
            logger.error(f"Failed to calculate average score: {str(e)}")
            return 0.0
    
    def _should_send_notification(self, subscription: ScoreThresholdSubscription) -> bool:
        """Check if notification should be sent based on frequency and last sent time"""
        try:
            if subscription.notification_frequency == 'immediate':
                return True
            
            if not subscription.last_notification_sent:
                return True
            
            current_time = datetime.utcnow()
            time_since_last = current_time - subscription.last_notification_sent
            
            if subscription.notification_frequency == 'daily':
                return time_since_last >= timedelta(days=1)
            elif subscription.notification_frequency == 'weekly':
                return time_since_last >= timedelta(weeks=1)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check notification frequency: {str(e)}")
            return False
    
    async def _send_threshold_breach_notification(
        self, 
        subscription: ScoreThresholdSubscription, 
        current_score: float, 
        db: Session
    ) -> bool:
        """Send threshold breach notification to user"""
        try:
            # Get user details
            user = db.query(User).filter(User.id == subscription.user_id).first()
            if not user or not user.email:
                logger.warning(f"User {subscription.user_id} not found or has no email")
                return False
            
            # Get freight forwarder details
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == subscription.freight_forwarder_id
            ).first()
            
            if not freight_forwarder:
                logger.warning(f"Freight forwarder {subscription.freight_forwarder_id} not found")
                return False
            
            # Create notification record
            notification = ScoreThresholdNotification(
                user_id=subscription.user_id,
                freight_forwarder_id=subscription.freight_forwarder_id,
                subscription_id=subscription.id,
                previous_score=subscription.threshold_score,  # We don't track previous scores yet
                current_score=current_score,
                threshold_score=subscription.threshold_score,
                notification_type='score_threshold_breach'
            )
            db.add(notification)
            
            # Send email notification
            email_sent = await self.email_service.send_score_threshold_notification(
                to_email=user.email,
                user_name=user.full_name or user.username or "User",
                freight_forwarder_name=freight_forwarder.name,
                current_score=current_score,
                threshold_score=subscription.threshold_score,
                subscription_expires_at=subscription.expires_at
            )
            
            if email_sent:
                notification.is_sent = True
                notification.sent_at = datetime.utcnow()
                subscription.last_notification_sent = datetime.utcnow()
                db.commit()
                logger.info(f"Score threshold notification sent to {user.email}")
                return True
            else:
                logger.error(f"Failed to send score threshold notification to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send threshold breach notification: {str(e)}")
            db.rollback()
            return False
    
    async def process_all_score_thresholds(self, db: Session) -> Dict[str, int]:
        """Process score thresholds for all freight forwarders with active subscriptions"""
        try:
            # Get all freight forwarders that have active score threshold subscriptions
            freight_forwarders = db.query(FreightForwarder).join(
                ScoreThresholdSubscription
            ).filter(
                and_(
                    ScoreThresholdSubscription.is_active == True,
                    or_(
                        ScoreThresholdSubscription.expires_at.is_(None),
                        ScoreThresholdSubscription.expires_at > datetime.utcnow()
                    )
                )
            ).distinct().all()
            
            results = {
                'processed_forwarders': 0,
                'notifications_sent': 0,
                'errors': 0
            }
            
            for freight_forwarder in freight_forwarders:
                try:
                    success = await self.check_score_thresholds(str(freight_forwarder.id), db)
                    if success:
                        results['processed_forwarders'] += 1
                    else:
                        results['errors'] += 1
                except Exception as e:
                    logger.error(f"Error processing freight forwarder {freight_forwarder.id}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Processed score thresholds: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process all score thresholds: {str(e)}")
            return {'processed_forwarders': 0, 'notifications_sent': 0, 'errors': 1}

# Create singleton instance
score_threshold_service = ScoreThresholdService()
