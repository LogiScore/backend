from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from auth.auth import get_current_user
from database.models import User, UserReward, Review
from services.promotion_service import PromotionService
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class PromotionConfigResponse(BaseModel):
    isActive: bool
    maxRewardsPerUser: int
    rewardMonths: int
    description: str

class PromotionConfigUpdate(BaseModel):
    isActive: bool
    maxRewardsPerUser: int
    rewardMonths: int

class UserRewardResponse(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    review_id: str
    months_awarded: int
    awarded_at: str

class AwardRewardRequest(BaseModel):
    user_id: str
    review_id: str
    months: int

class AwardRewardResponse(BaseModel):
    success: bool
    message: str

class PromotionStatsResponse(BaseModel):
    totalRewardsGiven: int
    activeUsers: int
    totalMonthsAwarded: int

class EligibilityResponse(BaseModel):
    eligible: bool
    currentRewards: int
    maxRewards: int
    message: str

class RewardNotificationRequest(BaseModel):
    user_email: str
    user_name: str
    months_awarded: int
    total_rewards: int
    max_rewards: int

# Helper function to check admin access
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/config", response_model=PromotionConfigResponse)
async def get_promotion_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get current promotion settings"""
    try:
        promotion_service = PromotionService(db)
        config = promotion_service.get_promotion_config()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve promotion configuration"
            )
        
        return PromotionConfigResponse(
            isActive=config.is_active,
            maxRewardsPerUser=config.max_rewards_per_user,
            rewardMonths=config.reward_months,
            description=config.description or ""
        )
    except Exception as e:
        logger.error(f"Error getting promotion config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve promotion configuration"
        )

@router.put("/config", response_model=PromotionConfigResponse)
async def update_promotion_config(
    config_data: PromotionConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update promotion settings"""
    try:
        promotion_service = PromotionService(db)
        config = promotion_service.update_promotion_config(config_data.dict())
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update promotion configuration"
            )
        
        return PromotionConfigResponse(
            isActive=config.is_active,
            maxRewardsPerUser=config.max_rewards_per_user,
            rewardMonths=config.reward_months,
            description=config.description or ""
        )
    except Exception as e:
        logger.error(f"Error updating promotion config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update promotion configuration"
        )

@router.get("/rewards", response_model=List[UserRewardResponse])
async def get_user_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all user rewards for admin dashboard"""
    try:
        promotion_service = PromotionService(db)
        rewards = promotion_service.get_user_rewards()
        
        return [UserRewardResponse(**reward) for reward in rewards]
    except Exception as e:
        logger.error(f"Error getting user rewards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user rewards"
        )

@router.post("/award", response_model=AwardRewardResponse)
async def award_reward(
    award_data: AwardRewardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually award a reward to a user"""
    try:
        promotion_service = PromotionService(db)
        success = promotion_service.award_user_reward(
            user_id=award_data.user_id,
            review_id=award_data.review_id,
            months=award_data.months,
            awarded_by=str(current_user.id)
        )
        
        if success:
            return AwardRewardResponse(
                success=True,
                message="Reward awarded successfully"
            )
        else:
            return AwardRewardResponse(
                success=False,
                message="Failed to award reward"
            )
    except Exception as e:
        logger.error(f"Error awarding reward: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to award reward"
        )

@router.get("/stats", response_model=PromotionStatsResponse)
async def get_promotion_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get promotion statistics for admin dashboard"""
    try:
        promotion_service = PromotionService(db)
        stats = promotion_service.get_promotion_stats()
        
        return PromotionStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting promotion stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve promotion statistics"
        )

@router.get("/eligibility/{user_id}", response_model=EligibilityResponse)
async def check_user_eligibility(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Check if user is eligible for rewards"""
    try:
        promotion_service = PromotionService(db)
        eligibility = promotion_service.check_user_eligibility(user_id)
        
        return EligibilityResponse(**eligibility)
    except Exception as e:
        logger.error(f"Error checking user eligibility: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check user eligibility"
        )

@router.post("/reward-notification")
async def send_reward_notification(
    notification_data: RewardNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Send reward notification email to user"""
    try:
        # Import email service
        from email_service import send_reward_notification_email
        
        success = await send_reward_notification_email(
            user_email=notification_data.user_email,
            user_name=notification_data.user_name,
            months_awarded=notification_data.months_awarded,
            total_rewards=notification_data.total_rewards,
            max_rewards=notification_data.max_rewards
        )
        
        if success:
            return {"success": True, "message": "Reward notification sent successfully"}
        else:
            return {"success": False, "message": "Failed to send reward notification"}
    except Exception as e:
        logger.error(f"Error sending reward notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reward notification"
        )

@router.get("/debug/user/{user_id}")
async def debug_user_promotion_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Debug endpoint to check user's promotion status"""
    try:
        promotion_service = PromotionService(db)
        
        # Get user details
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Check eligibility
        eligibility = promotion_service.check_user_eligibility(user_id)
        
        # Get user's rewards
        user_rewards = db.query(UserReward).filter(UserReward.user_id == user_id).all()
        
        # Get user's reviews
        user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
        
        return {
            "user_id": user_id,
            "user_email": user.email,
            "user_name": user.full_name,
            "subscription_status": user.subscription_status,
            "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            "eligibility": eligibility,
            "user_rewards": [
                {
                    "id": reward.id,
                    "review_id": str(reward.review_id),
                    "months_awarded": reward.months_awarded,
                    "awarded_at": reward.awarded_at.isoformat() if reward.awarded_at else None
                }
                for reward in user_rewards
            ],
            "user_reviews": [
                {
                    "id": str(review.id),
                    "freight_forwarder_id": str(review.freight_forwarder_id),
                    "created_at": review.created_at.isoformat() if review.created_at else None,
                    "is_anonymous": review.is_anonymous
                }
                for review in user_reviews
            ],
            "promotion_config": {
                "is_active": promotion_service.get_promotion_config().is_active,
                "max_rewards_per_user": promotion_service.get_promotion_config().max_rewards_per_user,
                "reward_months": promotion_service.get_promotion_config().reward_months
            }
        }
    except Exception as e:
        logger.error(f"Error debugging user promotion status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug failed: {str(e)}"
        )

@router.get("/debug/public/user/{user_id}")
async def debug_user_promotion_status_public(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Public debug endpoint to check user's promotion status (no auth required)"""
    try:
        promotion_service = PromotionService(db)
        
        # Get user details
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Check eligibility
        eligibility = promotion_service.check_user_eligibility(user_id)
        
        # Get user's rewards
        user_rewards = db.query(UserReward).filter(UserReward.user_id == user_id).all()
        
        # Get user's reviews
        user_reviews = db.query(Review).filter(Review.user_id == user_id).all()
        
        # Get promotion config
        config = promotion_service.get_promotion_config()
        
        return {
            "user_id": user_id,
            "user_email": user.email,
            "user_name": user.full_name,
            "subscription_status": user.subscription_status,
            "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            "eligibility": eligibility,
            "user_rewards_count": len(user_rewards),
            "user_rewards": [
                {
                    "id": reward.id,
                    "review_id": str(reward.review_id),
                    "months_awarded": reward.months_awarded,
                    "awarded_at": reward.awarded_at.isoformat() if reward.awarded_at else None
                }
                for reward in user_rewards
            ],
            "user_reviews_count": len(user_reviews),
            "user_reviews": [
                {
                    "id": str(review.id),
                    "freight_forwarder_id": str(review.freight_forwarder_id),
                    "created_at": review.created_at.isoformat() if review.created_at else None,
                    "is_anonymous": review.is_anonymous
                }
                for review in user_reviews
            ],
            "promotion_config": {
                "is_active": config.is_active if config else False,
                "max_rewards_per_user": config.max_rewards_per_user if config else 0,
                "reward_months": config.reward_months if config else 0
            }
        }
    except Exception as e:
        logger.error(f"Error debugging user promotion status: {e}")
        return {"error": f"Debug failed: {str(e)}"}

@router.post("/test-award/{user_id}/{review_id}")
async def test_award_reward(
    user_id: str,
    review_id: str,
    db: Session = Depends(get_db)
):
    """Test endpoint to manually award a reward (no auth required)"""
    try:
        promotion_service = PromotionService(db)
        
        # Check eligibility first
        eligibility = promotion_service.check_user_eligibility(user_id)
        print(f"Eligibility check: {eligibility}")
        
        # Try to award the reward
        try:
            success = promotion_service.award_user_reward(
                user_id=user_id,
                review_id=review_id,
                months=1
            )
            
            return {
                "success": success,
                "eligibility": eligibility,
                "message": "Reward awarded successfully" if success else "Failed to award reward",
                "debug_info": {
                    "user_id": user_id,
                    "review_id": review_id,
                    "months": 1
                }
            }
        except Exception as e:
            logger.error(f"Error in test award: {e}")
            import traceback
            error_details = traceback.format_exc()
            return {
                "success": False,
                "eligibility": eligibility,
                "error": str(e),
                "error_details": error_details,
                "message": f"Error occurred: {str(e)}"
            }
    except Exception as e:
        logger.error(f"Error testing award: {e}")
        return {"error": f"Test failed: {str(e)}"}

@router.get("/test-db/{user_id}/{review_id}")
async def test_database_operations(
    user_id: str,
    review_id: str,
    db: Session = Depends(get_db)
):
    """Test database operations directly (no auth required)"""
    try:
        # Test 1: Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        user_exists = user is not None
        
        # Test 2: Check if review exists
        review = db.query(Review).filter(Review.id == review_id).first()
        review_exists = review is not None
        
        # Test 3: Check if reward already exists
        existing_reward = db.query(UserReward).filter(
            UserReward.user_id == user_id,
            UserReward.review_id == review_id
        ).first()
        reward_exists = existing_reward is not None
        
        # Test 4: Try to create a test reward (without committing)
        test_reward = None
        try:
            test_reward = UserReward(
                user_id=user_id,
                review_id=review_id,
                months_awarded=1,
                awarded_by=None
            )
            db.add(test_reward)
            db.flush()  # Test without committing
            db.rollback()  # Rollback the test
            reward_creation_ok = True
        except Exception as e:
            reward_creation_ok = False
            reward_error = str(e)
        
        return {
            "user_exists": user_exists,
            "user_email": user.email if user else None,
            "review_exists": review_exists,
            "review_created_at": review.created_at.isoformat() if review else None,
            "review_is_anonymous": review.is_anonymous if review else None,
            "reward_already_exists": reward_exists,
            "reward_creation_test": reward_creation_ok,
            "reward_error": reward_error if not reward_creation_ok else None,
            "user_subscription_status": user.subscription_status if user else None,
            "user_subscription_end_date": user.subscription_end_date.isoformat() if user and user.subscription_end_date else None
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/test-direct-award/{user_id}/{review_id}")
async def test_direct_award(
    user_id: str,
    review_id: str,
    db: Session = Depends(get_db)
):
    """Test direct award without eligibility check (no auth required)"""
    try:
        promotion_service = PromotionService(db)
        
        # Bypass eligibility check and award directly
        success = promotion_service.award_user_reward(
            user_id=user_id,
            review_id=review_id,
            months=1
        )
        
        # Check if reward was actually created
        reward = db.query(UserReward).filter(
            UserReward.user_id == user_id,
            UserReward.review_id == review_id
        ).first()
        
        # Get updated user info
        user = db.query(User).filter(User.id == user_id).first()
        
        return {
            "success": success,
            "reward_created": reward is not None,
            "reward_id": reward.id if reward else None,
            "user_subscription_end_date": user.subscription_end_date.isoformat() if user and user.subscription_end_date else None,
            "user_subscription_status": user.subscription_status if user else None,
            "message": "Direct award successful" if success and reward else "Direct award failed"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/test-manual-award/{user_id}/{review_id}")
async def test_manual_award(
    user_id: str,
    review_id: str,
    db: Session = Depends(get_db)
):
    """Test manual award using direct database operations (no auth required)"""
    try:
        from datetime import datetime, timedelta
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get review
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return {"error": "Review not found"}
        
        # Check if reward already exists
        existing_reward = db.query(UserReward).filter(
            UserReward.user_id == user_id,
            UserReward.review_id == review_id
        ).first()
        if existing_reward:
            return {"error": "Reward already exists", "reward_id": existing_reward.id}
        
        # Create reward manually
        reward = UserReward(
            user_id=user_id,
            review_id=review_id,
            months_awarded=1,
            awarded_by=None
        )
        db.add(reward)
        
        # Extend subscription manually
        from datetime import timezone
        current_end_date = user.subscription_end_date
        now_utc = datetime.now(timezone.utc)
        
        if current_end_date and current_end_date > now_utc:
            new_end_date = current_end_date + timedelta(days=30)
        else:
            new_end_date = now_utc + timedelta(days=30)
        
        user.subscription_end_date = new_end_date
        user.subscription_status = 'active'
        
        # Commit everything
        db.commit()
        
        # Verify reward was created
        created_reward = db.query(UserReward).filter(
            UserReward.user_id == user_id,
            UserReward.review_id == review_id
        ).first()
        
        return {
            "success": True,
            "reward_created": created_reward is not None,
            "reward_id": created_reward.id if created_reward else None,
            "user_subscription_end_date": user.subscription_end_date.isoformat(),
            "user_subscription_status": user.subscription_status,
            "message": "Manual award successful"
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
