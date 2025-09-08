#!/usr/bin/env python3
"""
Subscription Expiration Service
Handles subscription expiration notifications and automatic tier reversion.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from email_service import EmailService

logger = logging.getLogger(__name__)

class SubscriptionExpirationService:
    """Service for managing subscription expiration and notifications"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def _get_subscription_price(self, tier: str) -> Dict[str, Any]:
        """Get subscription pricing information for a given tier"""
        pricing = {
            'shipper_monthly': {'amount': 29.99, 'currency': 'USD', 'period': 'month'},
            'shipper_annual': {'amount': 299.99, 'currency': 'USD', 'period': 'year'},
            'forwarder_monthly': {'amount': 99.99, 'currency': 'USD', 'period': 'month'},
            'forwarder_annual': {'amount': 999.99, 'currency': 'USD', 'period': 'year'},
            'forwarder_annual_plus': {'amount': 1999.99, 'currency': 'USD', 'period': 'year'},
            'monthly': {'amount': 29.99, 'currency': 'USD', 'period': 'month'},
            'annual': {'amount': 299.99, 'currency': 'USD', 'period': 'year'},
            'enterprise': {'amount': 999.99, 'currency': 'USD', 'period': 'year'}
        }
        
        return pricing.get(tier, {'amount': 0, 'currency': 'USD', 'period': 'month'})
    
    async def check_expiring_subscriptions(self, db: Session = None) -> Dict[str, Any]:
        """
        Check for subscriptions expiring within 7 days and send notifications.
        Returns summary of actions taken.
        """
        if not db:
            db = next(get_db())
        
        try:
            # Calculate dates
            now = datetime.utcnow()
            seven_days_from_now = now + timedelta(days=7)
            
            # Find users with subscriptions expiring within 7 days
            expiring_users = db.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= seven_days_from_now,
                User.subscription_end_date > now,
                User.subscription_status == 'active',
                User.subscription_tier != 'free'
            ).all()
            
            logger.info(f"Found {len(expiring_users)} users with expiring subscriptions")
            
            # Send 7-day notifications
            notification_results = []
            for user in expiring_users:
                days_until_expiry = (user.subscription_end_date - now).days
                if days_until_expiry <= 7 and days_until_expiry > 0:
                    result = await self._send_expiration_notification(user, days_until_expiry, db)
                    notification_results.append(result)
            
            # Check for expired subscriptions and revert to free
            expired_users = db.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= now,
                User.subscription_status == 'active',
                User.subscription_tier != 'free'
            ).all()
            
            logger.info(f"Found {len(expired_users)} users with expired subscriptions")
            
            # Revert expired subscriptions to free
            reversion_results = []
            for user in expired_users:
                result = await self._revert_to_free_tier(user, db)
                reversion_results.append(result)
            
            # Commit all changes
            db.commit()
            
            return {
                "notifications_sent": len(notification_results),
                "subscriptions_reverted": len(reversion_results),
                "notification_results": notification_results,
                "reversion_results": reversion_results,
                "checked_at": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking expiring subscriptions: {str(e)}")
            if db:
                db.rollback()
            raise
    
    async def _send_expiration_notification(self, user: User, days_until_expiry: int, db: Session) -> Dict[str, Any]:
        """Send expiration notification to user"""
        try:
            logger.info(f"Sending expiration notification to user {user.email} - {days_until_expiry} days remaining")
            
            # Get subscription pricing information
            subscription_price = self._get_subscription_price(user.subscription_tier)
            next_billing_date = user.subscription_end_date - timedelta(days=1) if user.subscription_end_date else None
            
            # Send email notification
            email_data = {
                'user_name': user.full_name or user.username or 'User',
                'subscription_tier': user.subscription_tier,
                'expiry_date': user.subscription_end_date.strftime('%B %d, %Y'),
                'days_remaining': days_until_expiry,
                'auto_renew_enabled': user.auto_renew_enabled or False,
                'next_billing_date': next_billing_date.strftime('%B %d, %Y') if next_billing_date else None,
                'subscription_price': subscription_price,
                'renewal_link': f"https://logiscore.com/renew?user_id={user.id}",
                'manage_subscription_link': f"https://logiscore.com/subscription?user_id={user.id}"
            }
            
            await self.email_service.send_subscription_expiration_warning(
                user_id=str(user.id),
                email_data=email_data
            )
            
            # Update user to mark notification sent
            user.subscription_status = 'expiring_soon'
            db.add(user)
            
            return {
                "user_id": str(user.id),
                "email": user.email,
                "days_until_expiry": days_until_expiry,
                "notification_sent": True,
                "status": "expiring_soon"
            }
            
        except Exception as e:
            logger.error(f"Failed to send expiration notification to user {user.id}: {str(e)}")
            return {
                "user_id": str(user.id),
                "email": user.email,
                "days_until_expiry": days_until_expiry,
                "notification_sent": False,
                "error": str(e)
            }
    
    async def _revert_to_free_tier(self, user: User, db: Session) -> Dict[str, Any]:
        """Revert expired subscription to free tier"""
        try:
            logger.info(f"Reverting user {user.email} from {user.subscription_tier} to free tier")
            
            # Store previous tier for audit
            previous_tier = user.subscription_tier
            
            # Update user subscription
            user.subscription_tier = 'free'
            user.subscription_status = 'expired'
            user.subscription_end_date = None
            user.auto_renew_enabled = False
            
            # Send expiration notification
            email_data = {
                'user_name': user.full_name or user.username or 'User',
                'previous_tier': previous_tier,
                'expiry_date': user.subscription_end_date.strftime('%B %d, %Y') if user.subscription_end_date else 'Unknown'
            }
            
            await self.email_service.send_subscription_expired_notification(
                user_id=str(user.id),
                email_data=email_data
            )
            
            db.add(user)
            
            return {
                "user_id": str(user.id),
                "email": user.email,
                "previous_tier": previous_tier,
                "new_tier": "free",
                "status": "expired",
                "reverted": True
            }
            
        except Exception as e:
            logger.error(f"Failed to revert user {user.id} to free tier: {str(e)}")
            return {
                "user_id": str(user.id),
                "email": user.email,
                "error": str(e),
                "reverted": False
            }
    
    async def get_expiring_subscriptions_summary(self, db: Session = None) -> Dict[str, Any]:
        """Get summary of expiring subscriptions for admin dashboard"""
        if not db:
            db = next(get_db())
        
        try:
            now = datetime.utcnow()
            
            # Subscriptions expiring in next 7 days
            expiring_7_days = db.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= now + timedelta(days=7),
                User.subscription_end_date > now,
                User.subscription_status == 'active'
            ).count()
            
            # Subscriptions expiring in next 30 days
            expiring_30_days = db.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= now + timedelta(days=30),
                User.subscription_end_date > now,
                User.subscription_status == 'active'
            ).count()
            
            # Recently expired subscriptions (last 7 days)
            recently_expired = db.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= now,
                User.subscription_end_date >= now - timedelta(days=7),
                User.subscription_status == 'expired'
            ).count()
            
            # Total active paid subscriptions
            total_paid = db.query(User).filter(
                User.subscription_tier != 'free',
                User.subscription_status == 'active'
            ).count()
            
            return {
                "expiring_7_days": expiring_7_days,
                "expiring_30_days": expiring_30_days,
                "recently_expired": recently_expired,
                "total_paid": total_paid,
                "checked_at": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting expiring subscriptions summary: {str(e)}")
            raise
    
    async def force_check_expiration(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Force check expiration for a specific user (admin function)"""
        if not db:
            db = next(get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            if user.subscription_end_date and user.subscription_end_date <= datetime.utcnow():
                # Subscription is expired, revert to free
                result = await self._revert_to_free_tier(user, db)
                db.commit()
                return result
            elif user.subscription_end_date and user.subscription_end_date <= datetime.utcnow() + timedelta(days=7):
                # Subscription is expiring soon, send notification
                days_until_expiry = (user.subscription_end_date - datetime.utcnow()).days
                result = await self._send_expiration_notification(user, days_until_expiry, db)
                db.commit()
                return result
            else:
                return {
                    "user_id": str(user.id),
                    "status": "active",
                    "message": "Subscription is active and not expiring soon"
                }
                
        except Exception as e:
            logger.error(f"Error force checking expiration for user {user_id}: {str(e)}")
            if db:
                db.rollback()
            raise
