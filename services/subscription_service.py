from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from services.stripe_service import StripeService
from email_service import EmailService
import logging

def utc_now():
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)

def calculate_next_billing_date(subscription_end_date: Optional[datetime]) -> Optional[datetime]:
    """Calculate next billing date as one day before subscription end date"""
    if subscription_end_date:
        return subscription_end_date - timedelta(days=1)
    return None

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
                # First verify the payment method exists
                try:
                    payment_method_info = await self.stripe_service.verify_payment_method(payment_method_id)
                    logger.info(f"Payment method verified: {payment_method_info['type']}")
                except Exception as e:
                    logger.error(f"Payment method verification failed: {str(e)}")
                    raise Exception(f"Payment method validation failed: {str(e)}")
                
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
                    'start_date': utc_now(),
                    'end_date': utc_now() + timedelta(days=trial_days) if trial_days > 0 else None,
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
            # Temporarily commented out until migration
            # if not user or not user.stripe_subscription_id:
            #     raise Exception("No active subscription found")
            if not user:
                raise Exception("User not found")
            
            # Update database directly
            logger.info(f"Before update - User {user_id}: status={user.subscription_status}, tier={user.subscription_tier}, auto_renew={user.auto_renew_enabled}, end_date={user.subscription_end_date}")
            
            user.subscription_status = 'canceled'
            user.subscription_tier = 'free'  # Downgrade to free tier when canceled
            user.auto_renew_enabled = False
            user.subscription_start_date = None  # Clear start date when canceled
            user.subscription_end_date = None    # Clear end date when canceled
            
            logger.info(f"After update - User {user_id}: status={user.subscription_status}, tier={user.subscription_tier}, auto_renew={user.auto_renew_enabled}, end_date={user.subscription_end_date}")
            
            db.commit()
            logger.info(f"Database commit successful for user {user_id}")
            
            # Verify the update
            db.refresh(user)
            logger.info(f"After refresh - User {user_id}: status={user.subscription_status}, tier={user.subscription_tier}, auto_renew={user.auto_renew_enabled}, end_date={user.subscription_end_date}")
            
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
            # Temporarily commented out until migration
            # if not user or not user.stripe_subscription_id:
            #     raise Exception("No subscription found")
            if not user:
                raise Exception("User not found")
            
            # Update database directly
            user.subscription_status = 'active'
            user.auto_renew_enabled = True
            user.subscription_start_date = utc_now()
            user.subscription_end_date = None
            db.commit()
            
            logger.info(f"Subscription reactivated for user {user_id}: status=active, start_date={user.subscription_start_date}")
            
            return {"message": "Subscription reactivated successfully"}
            
        except Exception as e:
            logger.error(f"Failed to reactivate subscription: {str(e)}")
            raise Exception(f"Failed to reactivate subscription: {str(e)}")
    
    async def update_subscription_plan(self, user_id: str, new_tier: str, duration: Optional[int] = None, comment: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
        """Update subscription to different plan"""
        try:
            if not db:
                db = next(get_db())
            
            # Validate inputs
            if not user_id:
                raise Exception("User ID is required")
            if not new_tier:
                raise Exception("New tier is required")
            
            # Validate tier value
            valid_tiers = ['free', 'monthly', 'annual', 'enterprise', 'Shipper Monthly', 'Shipper Annual', 'Forwarder Monthly', 'Forwarder Annual', 'Forwarder Annual Plus']
            if new_tier not in valid_tiers:
                raise Exception(f"Invalid tier: {new_tier}. Must be one of: {', '.join(valid_tiers)}")
            
            # Validate duration if provided
            if duration is not None and duration <= 0:
                raise Exception(f"Duration must be a positive number, got: {duration}")
            
            logger.info(f"Updating subscription plan for user {user_id} to tier {new_tier}")
            logger.info(f"Database session active: {db.is_active if db else 'No session'}")
            logger.info(f"Database session type: {type(db) if db else 'No session'}")
            
            try:
                logger.info(f"Executing database query for user {user_id}")
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise Exception("User not found")
                logger.info(f"Found user: {user.email}, current tier: {user.subscription_tier}")
            except Exception as query_error:
                logger.error(f"Database query failed: {str(query_error)}")
                logger.error(f"Query error type: {type(query_error)}")
                import traceback
                logger.error(f"Query error traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to query user: {str(query_error)}")
            
            # Temporarily commented out until migration
            # if not user or not user.stripe_subscription_id:
            #     raise Exception("No active subscription found")
            
            # Get new price ID
            try:
                new_price_id = await self.stripe_service.get_price_id_for_tier(new_tier, user.user_type)
                if not new_price_id:
                    # Log available tiers for debugging
                    logger.warning(f"No Stripe price found for tier: {new_tier}, user_type: {user.user_type}")
                    logger.warning(f"Available tiers: {list(self.stripe_service.STRIPE_PRICE_IDS.keys())}")
                    # For now, allow the update without Stripe integration (as per commented code)
                    logger.info(f"Proceeding with database update only for tier: {new_tier}")
                else:
                    logger.info(f"Found Stripe price ID: {new_price_id} for tier: {new_tier}")
            except Exception as stripe_error:
                logger.error(f"Stripe service error: {str(stripe_error)}")
                # Continue with database update only
                logger.info(f"Proceeding with database update only due to Stripe error")
            
            # Update in Stripe - temporarily commented out until migration
            # stripe_subscription = await self.stripe_service.update_subscription_plan(
            #     user.stripe_subscription_id, 
            #     new_price_id
            # )
            
            # Update database
            try:
                logger.info(f"Updating user {user_id} subscription tier from {user.subscription_tier} to {new_tier}")
                logger.info(f"User object before update: {user.__dict__}")
                
                # Update subscription tier
                user.subscription_tier = new_tier
                
                # Update subscription end date if duration is provided
                if duration is not None:
                    try:
                        user.subscription_end_date = utc_now() + timedelta(days=duration * 30)  # Approximate months to days
                        user.subscription_start_date = utc_now()
                        user.subscription_status = 'active'
                        user.auto_renew_enabled = True  # Enable auto-renewal by default for paid subscriptions
                        # Calculate next billing date (one day before subscription end date)
                        user.next_billing_date = calculate_next_billing_date(user.subscription_end_date)
                        logger.info(f"Set subscription start date to: {user.subscription_start_date}")
                        logger.info(f"Set subscription end date to: {user.subscription_end_date}")
                        logger.info(f"Set next billing date to: {user.next_billing_date}")
                        logger.info(f"Set auto_renew_enabled to: {user.auto_renew_enabled}")
                    except Exception as date_error:
                        logger.warning(f"Could not set subscription dates: {str(date_error)}")
                        # Continue without setting the dates
                
                # Log comment if provided
                if comment:
                    logger.info(f"Admin comment: {comment}")
                
                logger.info(f"User object after update: {user.__dict__}")
                db.commit()
                logger.info(f"Successfully updated user {user_id} subscription tier to {new_tier}")
            except Exception as db_error:
                logger.error(f"Database update failed: {str(db_error)}")
                logger.error(f"Database error type: {type(db_error)}")
                import traceback
                logger.error(f"Database error traceback: {traceback.format_exc()}")
                try:
                    db.rollback()
                    logger.info("Database rollback successful")
                except Exception as rollback_error:
                    logger.error(f"Database rollback failed: {str(rollback_error)}")
                raise Exception(f"Database update failed: {str(db_error)}")
            
            result = {
                "message": "Subscription plan updated successfully", 
                "tier": new_tier,
                "duration": duration,
                "comment": comment
            }
            logger.info(f"Subscription update completed successfully: {result}")
            logger.info(f"Returning result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update subscription plan for user {user_id}: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            # Log the full exception details for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
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
            days_remaining = 0
            if user.subscription_end_date:
                days_remaining = max(0, (user.subscription_end_date - utc_now()).days)
            
            # Calculate next billing date (one day before subscription end date)
            next_billing_date = calculate_next_billing_date(user.subscription_end_date)
            
            return {
                'id': str(user.id),
                'user_id': str(user.id),
                'tier': user.subscription_tier,
                'status': user.subscription_status or 'active',
                'start_date': user.subscription_start_date.isoformat() if user.subscription_start_date else None,
                'end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'auto_renew': user.auto_renew_enabled or False,
                'stripe_subscription_id': user.stripe_subscription_id,
                'days_remaining': days_remaining,
                'last_billing_date': user.last_billing_date.isoformat() if user.last_billing_date else None,
                'next_billing_date': next_billing_date.isoformat() if next_billing_date else None
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
            # Set subscription end date to current time when expired
            user.subscription_end_date = utc_now()
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
            
            target_date = utc_now() + timedelta(days=days_ahead)
            
            # Temporarily commented out until migration
            # expiring_users = db.query(User).filter(
            #     User.subscription_end_date <= target_date,
            #     User.subscription_status == 'active'
            # ).all()
            expiring_users = []  # Empty list until migration
            
            return [
                {
                    'user_id': str(user.id),
                    'email': user.email,
                    'tier': user.subscription_tier,
                    'end_date': None,  # user.subscription_end_date,
                    'days_remaining': 0  # max(0, (user.subscription_end_date - utc_now()).days)
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
            
            # Temporarily commented out until migration
            # expired_users = db.query(User).filter(
            #     User.subscription_end_date < utc_now(),
            #     User.subscription_status == 'active'
            # ).all()
            expired_users = []  # Empty list until migration
            
            return [
                {
                    'user_id': str(user.id),
                    'email': user.email,
                    'tier': user.subscription_tier,
                    'end_date': None  # user.subscription_end_date
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
        user.subscription_start_date = utc_now()
        
        if stripe_subscription:
            user.stripe_subscription_id = stripe_subscription.id
            user.subscription_status = 'active'
            user.auto_renew_enabled = True  # Enable auto-renewal by default for paid subscriptions
            
            if stripe_subscription.get('current_period_end'):
                user.subscription_end_date = datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                # Calculate next billing date (one day before subscription end date)
                user.next_billing_date = calculate_next_billing_date(user.subscription_end_date)
            elif trial_days > 0:
                user.subscription_end_date = utc_now() + timedelta(days=trial_days)
                user.subscription_status = 'trial'
                # Calculate next billing date (one day before trial end date)
                user.next_billing_date = calculate_next_billing_date(user.subscription_end_date)
        else:
            # Free tier
            user.subscription_status = 'active'
            user.subscription_end_date = None
            user.next_billing_date = None
            user.auto_renew_enabled = False  # Disable auto-renewal for free tier
        
        db.commit()
