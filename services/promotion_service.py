from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database.models import PromotionConfig, UserReward, User, Review
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PromotionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_promotion_config(self) -> Optional[PromotionConfig]:
        """Get current promotion configuration"""
        try:
            config = self.db.query(PromotionConfig).first()
            if not config:
                # Create default config if none exists
                config = PromotionConfig(
                    is_active=True,
                    max_rewards_per_user=3,
                    reward_months=1,
                    description="Get 1 month free subscription for each review submitted (max 3 months)"
                )
                self.db.add(config)
                self.db.commit()
                self.db.refresh(config)
            return config
        except Exception as e:
            logger.error(f"Error getting promotion config: {e}")
            return None
    
    def update_promotion_config(self, config_data: Dict) -> Optional[PromotionConfig]:
        """Update promotion configuration"""
        try:
            config = self.get_promotion_config()
            if not config:
                return None
            
            config.is_active = config_data.get('isActive', config.is_active)
            config.max_rewards_per_user = config_data.get('maxRewardsPerUser', config.max_rewards_per_user)
            config.reward_months = config_data.get('rewardMonths', config.reward_months)
            config.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(config)
            return config
        except Exception as e:
            logger.error(f"Error updating promotion config: {e}")
            self.db.rollback()
            return None
    
    def get_user_rewards(self) -> List[Dict]:
        """Get all user rewards for admin dashboard"""
        try:
            rewards = self.db.query(
                UserReward,
                User.full_name,
                User.email
            ).join(
                User, UserReward.user_id == User.id
            ).order_by(UserReward.awarded_at.desc()).all()
            
            result = []
            for reward, user_name, user_email in rewards:
                result.append({
                    "user_id": str(reward.user_id),
                    "user_name": user_name or "Unknown",
                    "user_email": user_email,
                    "review_id": str(reward.review_id),
                    "months_awarded": reward.months_awarded,
                    "awarded_at": reward.awarded_at.isoformat() if reward.awarded_at else None
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting user rewards: {e}")
            return []
    
    def award_user_reward(self, user_id: str, review_id: str, months: int, awarded_by: str = None) -> bool:
        """Award a reward to a user and extend their subscription"""
        try:
            logger.info(f"🔍 Starting award process for user {user_id}, review {review_id}")
            
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"❌ User {user_id} not found")
                return False
            logger.info(f"✅ User found: {user.email}")
            
            # Check if review exists
            review = self.db.query(Review).filter(Review.id == review_id).first()
            if not review:
                logger.error(f"❌ Review {review_id} not found")
                return False
            logger.info(f"✅ Review found: {review.id}")
            
            # Extend user's subscription
            from datetime import datetime, timedelta
            
            logger.info(f"📅 Current subscription end date: {user.subscription_end_date}")
            
            # Calculate new end date
            from datetime import timezone
            current_end_date = user.subscription_end_date
            now_utc = datetime.now(timezone.utc)
            
            if current_end_date and current_end_date > now_utc:
                # User has active subscription, extend from current end date
                new_end_date = current_end_date + timedelta(days=months * 30)
                logger.info(f"📅 Extending from current end date: {new_end_date}")
            else:
                # User has no active subscription, start from now
                new_end_date = now_utc + timedelta(days=months * 30)
                logger.info(f"📅 Starting new subscription from now: {new_end_date}")
            
            # Update user's subscription
            user.subscription_end_date = new_end_date
            user.subscription_status = 'active'  # Ensure status is active
            logger.info(f"✅ Updated user subscription to {new_end_date}")
            
            # Create reward record
            reward = UserReward(
                user_id=user_id,
                review_id=review_id,
                months_awarded=months,
                awarded_by=awarded_by
            )
            logger.info(f"🎁 Creating reward record: {months} months")
            
            self.db.add(reward)
            logger.info(f"💾 Added reward to database session")
            
            self.db.commit()
            logger.info(f"✅ Committed to database")
            
            logger.info(f"🎉 Reward awarded: {months} months to user {user_id} for review {review_id}")
            logger.info(f"📅 User {user_id} subscription extended to {new_end_date}")
            return True
        except Exception as e:
            logger.error(f"Error awarding user reward: {e}")
            self.db.rollback()
            return False
    
    def get_promotion_stats(self) -> Dict:
        """Get promotion statistics"""
        try:
            total_rewards = self.db.query(func.count(UserReward.id)).scalar() or 0
            total_months = self.db.query(func.sum(UserReward.months_awarded)).scalar() or 0
            active_users = self.db.query(func.count(func.distinct(UserReward.user_id))).scalar() or 0
            
            return {
                "totalRewardsGiven": total_rewards,
                "activeUsers": active_users,
                "totalMonthsAwarded": total_months
            }
        except Exception as e:
            logger.error(f"Error getting promotion stats: {e}")
            return {
                "totalRewardsGiven": 0,
                "activeUsers": 0,
                "totalMonthsAwarded": 0
            }
    
    def check_user_eligibility(self, user_id: str) -> Dict:
        """Check if user is eligible for rewards"""
        try:
            config = self.get_promotion_config()
            if not config or not config.is_active:
                return {
                    "eligible": False,
                    "currentRewards": 0,
                    "maxRewards": 0,
                    "message": "Promotion is not active"
                }
            
            # Count current rewards for user
            current_rewards = self.db.query(func.count(UserReward.id)).filter(
                UserReward.user_id == user_id
            ).scalar() or 0
            
            eligible = current_rewards < config.max_rewards_per_user
            remaining = config.max_rewards_per_user - current_rewards
            
            return {
                "eligible": eligible,
                "currentRewards": current_rewards,
                "maxRewards": config.max_rewards_per_user,
                "message": f"User is eligible for {remaining} more reward(s)" if eligible else "User has reached maximum rewards"
            }
        except Exception as e:
            logger.error(f"Error checking user eligibility: {e}")
            return {
                "eligible": False,
                "currentRewards": 0,
                "maxRewards": 0,
                "message": "Error checking eligibility"
            }
    
    def check_and_award_promotion_reward(self, user_id: str, review_id: str) -> bool:
        """Check if user is eligible and award promotion reward"""
        try:
            # Check eligibility
            eligibility = self.check_user_eligibility(user_id)
            if not eligibility['eligible']:
                logger.info(f"User {user_id} not eligible for promotion reward")
                return False
            
            # Get config for reward months
            config = self.get_promotion_config()
            if not config:
                return False
            
            # Award the reward
            success = self.award_user_reward(
                user_id=user_id,
                review_id=review_id,
                months=config.reward_months
            )
            
            if success:
                logger.info(f"Promotion reward awarded to user {user_id} for review {review_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error in check_and_award_promotion_reward: {e}")
            return False
