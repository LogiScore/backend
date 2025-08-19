from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from services.stripe_service import StripeService
from email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self):
        self.stripe_service = StripeService()
        self.email_service = EmailService()
    
    async def create_subscription(
        self, 
        user_id: str, 
        tier: str,
        user_type: str,
        payment_method_id: Optional[str] = None,
        trial_days: int = 0,
        is_paid: bool = True,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create subscription for user"""
        try:
            if not db:
                db = next(get_db())
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Get or create Stripe customer
            customer_id = await self._get_or_create_stripe_customer(user, db)
            
            # Get Stripe price ID for tier
            price_id = await self.stripe_service.get_price_id_for_tier(tier, user_type)
            if not price_id and is_paid:
                raise Exception(f"No Stripe price configured for tier: {tier}")
            
            if is_paid and payment_method_id:
                # Attach payment method
                await self.stripe_service.attach_payment_method(payment_method_id, customer_id)
                
                # Create paid subscription
                stripe_subscription = await self.stripe_service.create_subscription(
                    customer_id=customer_id,
                    price_id=price_id,
                    trial_days=trial_days,
                    metadata={'user_id': str(user_id)}
                )
            else:
                # Create free trial subscription
                if price_id:
                    stripe_subscription = await self.stripe_service.create_subscription(
                        customer_id=customer_id,
                        price_id=price_id,
                        trial_days=trial_days,
                        metadata={'user_id': str(user_id)}
                    )
                else:
                    # Free tier - no Stripe subscription needed
                    stripe_subscription = None
            
            # Update database
            await self._update_user_subscription_db(
                user_id, 
                tier, 
                stripe_subscription, 
                trial_days, 
                db
            )
            
            # Send confirmation email
            if stripe_subscription:
                await self.email_service.send_subscription_confirmation(user_id, {
                    'tier': tier,
                    'start_date': datetime.utcnow(),
                    'end_date': datetime.utcnow() + timedelta(days=trial_days) if trial_days > 0 else None,
                    'status': 'active'
                })
            
            return {
                'subscription_id': stripe_subscription.id if stripe_subscription else 'free_tier',
                'tier': tier,
                'status': 'active',
                'trial_days': trial_days,
                'stripe_subscription_id': stripe_subscription.id if stripe_subscription else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Cancel user subscription"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.stripe_subscription_id:
                raise Exception("No active subscription found")
            
            # Cancel in Stripe
            stripe_subscription = await self.stripe_service.cancel_subscription(user.stripe_subscription_id)
            
            # Update database
            user.subscription_status = 'canceled'
            user.auto_renew_enabled = False
            db.commit()
            
            # Send cancellation email
            await self.email_service.send_subscription_cancellation_notification(user_id)
            
            return {"message": "Subscription canceled successfully"}
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    async def reactivate_subscription(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Reactivate canceled subscription"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.stripe_subscription_id:
                raise Exception("No subscription found")
            
            # Reactivate in Stripe
            stripe_subscription = await self.stripe_service.reactivate_subscription(user.stripe_subscription_id)
            
            # Update database
            user.subscription_status = 'active'
            user.auto_renew_enabled = True
            db.commit()
            
            return {"message": "Subscription reactivated successfully"}
            
        except Exception as e:
            logger.error(f"Failed to reactivate subscription: {str(e)}")
            raise Exception(f"Failed to reactivate subscription: {str(e)}")
    
    async def update_subscription_plan(self, user_id: str, new_tier: str, db: Session = None) -> Dict[str, Any]:
        """Update subscription to different plan"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.stripe_subscription_id:
                raise Exception("No active subscription found")
            
            # Get new price ID
            new_price_id = await self.stripe_service.get_price_id_for_tier(new_tier, user.user_type)
            if not new_price_id:
                raise Exception(f"No Stripe price configured for tier: {new_tier}")
            
            # Update in Stripe
            stripe_subscription = await self.stripe_service.update_subscription_plan(
                user.stripe_subscription_id, 
                new_price_id
            )
            
            # Update database
            user.subscription_tier = new_tier
            db.commit()
            
            return {"message": "Subscription plan updated successfully"}
            
        except Exception as e:
            logger.error(f"Failed to update subscription plan: {str(e)}")
            raise Exception(f"Failed to update subscription plan: {str(e)}")
    
    async def get_user_subscription(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Get user subscription details"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Calculate days remaining
            days_remaining = None
            if user.subscription_end_date:
                days_remaining = max(0, (user.subscription_end_date - datetime.utcnow()).days)
            
            return {
                'id': str(user.id),
                'user_id': str(user.id),
                'tier': user.subscription_tier,
                'status': user.subscription_status,
                'start_date': user.subscription_start_date,
                'end_date': user.subscription_end_date,
                'auto_renew': user.auto_renew_enabled,
                'stripe_subscription_id': user.stripe_subscription_id,
                'days_remaining': days_remaining,
                'last_billing_date': user.last_billing_date,
                'next_billing_date': user.next_billing_date
            }
            
        except Exception as e:
            logger.error(f"Failed to get user subscription: {str(e)}")
            raise Exception(f"Failed to get user subscription: {str(e)}")
    
    async def mark_subscription_expired(self, user_id: str, db: Session = None) -> bool:
        """Mark subscription as expired"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.subscription_status = 'expired'
            user.subscription_tier = 'free'
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark subscription expired: {str(e)}")
            return False
    
    async def downgrade_to_free_tier(self, user_id: str, db: Session = None) -> bool:
        """Downgrade user to free tier"""
        try:
            if not db:
                db = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.subscription_tier = 'free'
            user.subscription_status = 'expired'
            user.auto_renew_enabled = False
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to downgrade to free tier: {str(e)}")
            return False
    
    async def get_expiring_subscriptions(self, days_ahead: int = 3, db: Session = None) -> List[Dict[str, Any]]:
        """Get subscriptions expiring within specified days"""
        try:
            if not db:
                db = next(get_db())
            
            target_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            expiring_users = db.query(User).filter(
                User.subscription_end_date <= target_date,
                User.subscription_status == 'active'
            ).all()
            
            return [
                {
                    'user_id': str(user.id),
                    'email': user.email,
                    'tier': user.subscription_tier,
                    'end_date': user.subscription_end_date,
                    'days_remaining': max(0, (user.subscription_end_date - datetime.utcnow()).days)
                }
                for user in expiring_users
            ]
            
        except Exception as e:
            logger.error(f"Failed to get expiring subscriptions: {str(e)}")
            return []
    
    async def get_expired_subscriptions(self, db: Session = None) -> List[Dict[str, Any]]:
        """Get expired subscriptions"""
        try:
            if not db:
                db = next(get_db())
            
            expired_users = db.query(User).filter(
                User.subscription_end_date < datetime.utcnow(),
                User.subscription_status == 'active'
            ).all()
            
            return [
                {
                    'user_id': str(user.id),
                    'email': user.email,
                    'tier': user.subscription_tier,
                    'end_date': user.subscription_end_date
                }
                for user in expired_users
            ]
            
        except Exception as e:
            logger.error(f"Failed to get expired subscriptions: {str(e)}")
            return []
    
    async def _get_or_create_stripe_customer(self, user: User, db: Session) -> str:
        """Get existing Stripe customer or create new one"""
        if user.stripe_customer_id:
            try:
                # Verify customer exists in Stripe
                await self.stripe_service.get_customer(user.stripe_customer_id)
                return user.stripe_customer_id
            except:
                # Customer doesn't exist, create new one
                pass
        
        # Create new Stripe customer
        customer_id = await self.stripe_service.create_customer(user)
        
        # Update user record
        user.stripe_customer_id = customer_id
        db.commit()
        
        return customer_id
    
    async def _update_user_subscription_db(
        self, 
        user_id: str, 
        tier: str, 
        stripe_subscription: Optional[Dict[str, Any]], 
        trial_days: int,
        db: Session
    ):
        """Update user subscription details in database"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")
        
        user.subscription_tier = tier
        user.subscription_start_date = datetime.utcnow()
        
        if stripe_subscription:
            user.stripe_subscription_id = stripe_subscription.id
            user.subscription_status = 'active'
            
            if stripe_subscription.get('current_period_end'):
                user.subscription_end_date = datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
            elif trial_days > 0:
                user.subscription_end_date = datetime.utcnow() + timedelta(days=trial_days)
                user.subscription_status = 'trial'
        else:
            # Free tier
            user.subscription_status = 'active'
            user.subscription_end_date = None
        
        db.commit()
