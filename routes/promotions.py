from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from auth.auth import get_current_user
from database.models import User
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
