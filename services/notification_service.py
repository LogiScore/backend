import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.models import ReviewSubscription, Review, User, FreightForwarder, ReviewNotification
from email_service import email_service

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling review notifications and subscription management"""
    
    def __init__(self):
        self.email_service = email_service
    
    async def process_new_review(self, review_id: str, db: Session) -> bool:
        """Process a new review and send notifications to matching subscribers"""
        try:
            # Get the review with freight forwarder details
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                logger.error(f"Review {review_id} not found")
                return False
            
            # Get freight forwarder details
            freight_forwarder = db.query(FreightForwarder).filter(
                FreightForwarder.id == review.freight_forwarder_id
            ).first()
            
            if not freight_forwarder:
                logger.error(f"Freight forwarder {review.freight_forwarder_id} not found")
                return False
            
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(review, db)
            
            if not matching_subscriptions:
                logger.info(f"No matching subscriptions found for review {review_id}")
                return True
            
            # Send notifications
            success_count = 0
            for subscription in matching_subscriptions:
                try:
                    # Get user details
                    user = db.query(User).filter(User.id == subscription.user_id).first()
                    if not user or not user.is_active:
                        continue
                    
                    # Create notification record
                    notification = ReviewNotification(
                        user_id=user.id,
                        review_id=review.id,
                        subscription_id=subscription.id,
                        notification_type='new_review'
                    )
                    db.add(notification)
                    
                    # Send immediate notification if frequency is immediate
                    if subscription.notification_frequency == 'immediate':
                        await self._send_immediate_notification(user, review, freight_forwarder)
                        notification.is_sent = True
                        notification.sent_at = datetime.utcnow()
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process notification for subscription {subscription.id}: {str(e)}")
                    continue
            
            db.commit()
            logger.info(f"Processed {success_count} notifications for review {review_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process new review {review_id}: {str(e)}")
            db.rollback()
            return False
    
    def _find_matching_subscriptions(self, review: Review, db: Session) -> List[ReviewSubscription]:
        """Find subscriptions that match the review criteria"""
        try:
            # Build query for matching subscriptions
            query = db.query(ReviewSubscription).filter(
                ReviewSubscription.is_active == True
            )
            
            # Add filters based on review attributes
            filters = []
            
            # Freight forwarder filter
            if review.freight_forwarder_id:
                filters.append(ReviewSubscription.freight_forwarder_id == review.freight_forwarder_id)
            
            # Location filters
            if review.city:
                filters.append(ReviewSubscription.location_city == review.city)
            if review.country:
                filters.append(ReviewSubscription.location_country == review.country)
            
            # Review type filter
            if review.review_type:
                filters.append(ReviewSubscription.review_type == review.review_type)
            
            # Apply filters
            if filters:
                query = query.filter(*filters)
            
            # Also include subscriptions with no specific filters (general subscriptions)
            general_subscriptions = db.query(ReviewSubscription).filter(
                ReviewSubscription.is_active == True,
                ReviewSubscription.freight_forwarder_id.is_(None),
                ReviewSubscription.location_country.is_(None),
                ReviewSubscription.location_city.is_(None),
                ReviewSubscription.review_type.is_(None)
            )
            
            # Combine results
            specific_subscriptions = query.all()
            general_subscriptions = general_subscriptions.all()
            
            # Remove duplicates
            all_subscriptions = specific_subscriptions + general_subscriptions
            unique_subscriptions = list({sub.id: sub for sub in all_subscriptions}.values())
            
            return unique_subscriptions
            
        except Exception as e:
            logger.error(f"Failed to find matching subscriptions: {str(e)}")
            return []
    
    async def _send_immediate_notification(self, user: User, review: Review, freight_forwarder: FreightForwarder) -> bool:
        """Send immediate notification email to user"""
        try:
            review_data = {
                'review_id': str(review.id),
                'freight_forwarder_name': freight_forwarder.name,
                'aggregate_rating': float(review.aggregate_rating) if review.aggregate_rating else 0,
                'city': review.city,
                'country': review.country,
                'review_type': review.review_type,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M UTC') if review.created_at else 'N/A'
            }
            
            user_name = user.full_name or user.username or user.email.split('@')[0]
            
            return await self.email_service.send_review_notification(
                user_email=user.email,
                user_name=user_name,
                review_data=review_data
            )
            
        except Exception as e:
            logger.error(f"Failed to send immediate notification to {user.email}: {str(e)}")
            return False
    
    async def send_daily_summaries(self, db: Session) -> bool:
        """Send daily summary emails to subscribers"""
        try:
            # Get all active subscriptions with daily frequency
            daily_subscriptions = db.query(ReviewSubscription).filter(
                ReviewSubscription.is_active == True,
                ReviewSubscription.notification_frequency == 'daily'
            ).all()
            
            success_count = 0
            for subscription in daily_subscriptions:
                try:
                    # Get user details
                    user = db.query(User).filter(User.id == subscription.user_id).first()
                    if not user or not user.is_active:
                        continue
                    
                    # Get reviews from the last 24 hours that match subscription criteria
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    matching_reviews = self._get_matching_reviews_for_period(
                        subscription, yesterday, datetime.utcnow(), db
                    )
                    
                    if matching_reviews:
                        await self._send_summary_email(user, matching_reviews, 'daily')
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send daily summary to user {subscription.user_id}: {str(e)}")
                    continue
            
            logger.info(f"Sent {success_count} daily summary emails")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily summaries: {str(e)}")
            return False
    
    async def send_weekly_summaries(self, db: Session) -> bool:
        """Send weekly summary emails to subscribers"""
        try:
            # Get all active subscriptions with weekly frequency
            weekly_subscriptions = db.query(ReviewSubscription).filter(
                ReviewSubscription.is_active == True,
                ReviewSubscription.notification_frequency == 'weekly'
            ).all()
            
            success_count = 0
            for subscription in weekly_subscriptions:
                try:
                    # Get user details
                    user = db.query(User).filter(User.id == subscription.user_id).first()
                    if not user or not user.is_active:
                        continue
                    
                    # Get reviews from the last 7 days that match subscription criteria
                    week_ago = datetime.utcnow() - timedelta(days=7)
                    matching_reviews = self._get_matching_reviews_for_period(
                        subscription, week_ago, datetime.utcnow(), db
                    )
                    
                    if matching_reviews:
                        await self._send_summary_email(user, matching_reviews, 'weekly')
                        success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send weekly summary to user {subscription.user_id}: {str(e)}")
                    continue
            
            logger.info(f"Sent {success_count} weekly summary emails")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send weekly summaries: {str(e)}")
            return False
    
    def _get_matching_reviews_for_period(self, subscription: ReviewSubscription, start_date: datetime, end_date: datetime, db: Session) -> List[Dict[str, Any]]:
        """Get reviews matching subscription criteria within a time period"""
        try:
            # Build query for matching reviews
            query = db.query(Review).filter(
                Review.created_at >= start_date,
                Review.created_at <= end_date
            )
            
            # Add filters based on subscription criteria
            if subscription.freight_forwarder_id:
                query = query.filter(Review.freight_forwarder_id == subscription.freight_forwarder_id)
            
            if subscription.location_city:
                query = query.filter(Review.city == subscription.location_city)
            
            if subscription.location_country:
                query = query.filter(Review.country == subscription.location_country)
            
            if subscription.review_type:
                query = query.filter(Review.review_type == subscription.review_type)
            
            reviews = query.all()
            
            # Format reviews for email
            formatted_reviews = []
            for review in reviews:
                freight_forwarder = db.query(FreightForwarder).filter(
                    FreightForwarder.id == review.freight_forwarder_id
                ).first()
                
                formatted_reviews.append({
                    'freight_forwarder_name': freight_forwarder.name if freight_forwarder else 'Unknown',
                    'aggregate_rating': float(review.aggregate_rating) if review.aggregate_rating else 0,
                    'city': review.city,
                    'country': review.country,
                    'review_type': review.review_type,
                    'created_at': review.created_at.strftime('%Y-%m-%d %H:%M UTC') if review.created_at else 'N/A'
                })
            
            return formatted_reviews
            
        except Exception as e:
            logger.error(f"Failed to get matching reviews for period: {str(e)}")
            return []
    
    async def _send_summary_email(self, user: User, reviews: List[Dict[str, Any]], frequency: str) -> bool:
        """Send summary email to user"""
        try:
            summary_data = {
                'frequency': frequency,
                'total_reviews': len(reviews),
                'reviews': reviews
            }
            
            user_name = user.full_name or user.username or user.email.split('@')[0]
            
            return await self.email_service.send_subscription_summary(
                user_email=user.email,
                user_name=user_name,
                summary_data=summary_data
            )
            
        except Exception as e:
            logger.error(f"Failed to send summary email to {user.email}: {str(e)}")
            return False
    
    async def cleanup_old_notifications(self, db: Session, days_to_keep: int = 30) -> bool:
        """Clean up old notification records"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old notifications
            deleted_count = db.query(ReviewNotification).filter(
                ReviewNotification.created_at < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted_count} old notification records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup old notifications: {str(e)}")
            db.rollback()
            return False

# Create singleton instance
notification_service = NotificationService()
