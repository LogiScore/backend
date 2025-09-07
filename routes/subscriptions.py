from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import stripe

from database.database import get_db
from database.models import User
from auth.auth import get_current_user
from services.subscription_service import SubscriptionService
from services.stripe_service import StripeService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services lazily to avoid import-time errors
subscription_service = None
stripe_service = None

def get_subscription_service():
    global subscription_service
    if subscription_service is None:
        subscription_service = SubscriptionService()
    return subscription_service

def get_stripe_service():
    global stripe_service
    if stripe_service is None:
        stripe_service = StripeService()
    return stripe_service

class SubscriptionRequest(BaseModel):
    plan_id: str
    plan_name: str
    user_type: str
    payment_method_id: Optional[str] = None
    trial_days: int = 0

class SubscriptionResponse(BaseModel):
    subscription_id: str
    client_secret: Optional[str] = None
    checkout_url: Optional[str] = None
    message: str
    tier: str
    status: str

class SubscriptionCancelRequest(BaseModel):
    reason: Optional[str] = None

class AutoRenewalToggleRequest(BaseModel):
    auto_renew_enabled: bool

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_request: SubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription for the user"""
    try:
        # Validate user type matches plan type
        if current_user.user_type != subscription_request.user_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This plan is only available for {subscription_request.user_type}s"
            )
        
        # Extract tier from plan name
        tier = subscription_request.plan_name.lower().replace(' ', '_')
        
        # Create subscription using the service
        subscription_service = get_subscription_service()
        subscription_result = await subscription_service.create_subscription(
            user_id=str(current_user.id),
            tier=tier,
            user_type=current_user.user_type,
            payment_method_id=subscription_request.payment_method_id,
            trial_days=subscription_request.trial_days,
            is_paid=subscription_request.payment_method_id is not None,
            db=db
        )
        
        return SubscriptionResponse(
            subscription_id=subscription_result['subscription_id'],
            message=f"Successfully upgraded to {subscription_request.plan_name}!",
            tier=subscription_result['tier'],
            status=subscription_result['status']
        )
        
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.post("/cancel")
async def cancel_subscription(
    cancel_request: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    try:
        subscription_service = get_subscription_service()
        result = await subscription_service.cancel_subscription(
            user_id=str(current_user.id),
            db=db
        )
        
        return {"message": "Subscription canceled successfully"}
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.post("/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reactivate canceled subscription"""
    try:
        subscription_service = get_subscription_service()
        result = await subscription_service.reactivate_subscription(
            user_id=str(current_user.id),
            db=db
        )
        
        return {"message": "Subscription reactivated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to reactivate subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate subscription: {str(e)}"
        )

@router.put("/upgrade")
async def upgrade_subscription(
    new_tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade subscription to different plan"""
    try:
        subscription_service = get_subscription_service()
        result = await subscription_service.update_subscription_plan(
            user_id=str(current_user.id),
            new_tier=new_tier,
            db=db
        )
        
        return {"message": "Subscription plan updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}"
        )

@router.get("/plans")
async def get_subscription_plans(
    current_user: User = Depends(get_current_user)
):
    """Get available subscription plans for the user's type"""
    try:
        # Define plans based on user type - Updated to match actual Stripe products
        plans = {
            "shipper": [
                {
                    "id": "shipper_monthly",
                    "name": "Shipper Monthly Subscription",
                    "description": "Monthly subscription to LogiScore.net for shippers",
                    "price": 0,  # Will be updated with actual price from Stripe
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "stripe_price_id": stripe_service.STRIPE_PRICE_IDS.get('shipper_monthly'),
                    "stripe_product_id": "prod_StYy4QPzGhoMQU",
                    "features": [
                        "Access to freight forwarder reviews",
                        "Advanced search and filtering",
                        "Contact information for forwarders",
                        "Analytics and reporting",
                        "Email support"
                    ]
                },
                {
                    "id": "shipper_annual",
                    "name": "Shipper Annual Subscription",
                    "description": "Annual subscription to LogiScore.net for shippers",
                    "price": 0,  # Will be updated with actual price from Stripe
                    "currency": "USD",
                    "billing_cycle": "yearly",
                    "is_popular": True,
                    "stripe_price_id": stripe_service.STRIPE_PRICE_IDS.get('shipper_annual'),
                    "stripe_product_id": "prod_StZ0qjHzGSSZZ9",
                    "features": [
                        "All Monthly features",
                        "2 months free (annual billing)",
                        "Priority customer support",
                        "Advanced analytics dashboard",
                        "API access for integrations"
                    ]
                }
            ],
            "forwarder": [
                {
                    "id": "forwarder_monthly",
                    "name": "Forwarder Monthly Subscription",
                    "description": "Monthly subscription to LogiScore.net for forwarders",
                    "price": 0,  # Will be updated with actual price from Stripe
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "stripe_price_id": stripe_service.STRIPE_PRICE_IDS.get('forwarder_monthly'),
                    "stripe_product_id": "prod_StZ1HjEEPrZ8oo",
                    "features": [
                        "Company profile listing",
                        "Review management",
                        "Customer inquiry responses",
                        "Basic analytics",
                        "Email support"
                    ]
                },
                {
                    "id": "forwarder_annual",
                    "name": "Forwarder Annual Subscription",
                    "description": "Annual subscription to LogiScore.net for forwarders",
                    "price": 0,  # Will be updated with actual price from Stripe
                    "currency": "USD",
                    "billing_cycle": "yearly",
                    "stripe_price_id": stripe_service.STRIPE_PRICE_IDS.get('forwarder_annual'),
                    "stripe_product_id": "prod_StZ2pVrOSMVZIn",
                    "features": [
                        "All Monthly features",
                        "2 months free (annual billing)",
                        "Advanced analytics dashboard",
                        "Priority listing placement",
                        "Marketing tools and insights"
                    ]
                },
                {
                    "id": "forwarder_annual_plus",
                    "name": "Forwarder Annual Subscription Plus",
                    "description": "Annual Plus subscription to LogiScore.net for forwarders",
                    "price": 0,  # Will be updated with actual price from Stripe
                    "currency": "USD",
                    "billing_cycle": "yearly",
                    "is_popular": True,
                    "stripe_price_id": stripe_service.STRIPE_PRICE_IDS.get('forwarder_annual_plus'),
                    "stripe_product_id": "prod_StZ3890Xh8lQCZ",
                    "features": [
                        "All Annual features",
                        "Premium listing placement",
                        "Advanced API access",
                        "Custom branding options",
                        "Priority support",
                        "Multi-location management"
                    ]
                }
            ]
        }
        
        user_plans = plans.get(current_user.user_type, [])
        
        # Add Stripe price IDs if available
        stripe_service = get_stripe_service()
        for plan in user_plans:
            plan['stripe_price_id'] = stripe_service.STRIPE_PRICE_IDS.get(plan['id'])
        
        return {"plans": user_plans}
        
    except Exception as e:
        logger.error(f"Failed to get subscription plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )

@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the user's current subscription details"""
    try:
        subscription_service = get_subscription_service()
        subscription = await subscription_service.get_user_subscription(
            user_id=str(current_user.id),
            db=db
        )
        
        return subscription
        
    except Exception as e:
        logger.error(f"Failed to get current subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current subscription: {str(e)}"
        )

@router.get("/billing-portal")
async def get_billing_portal_url(
    current_user: User = Depends(get_current_user)
):
    """Get Stripe billing portal URL for customer"""
    try:
        if not current_user.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found"
            )
        
        # Create billing portal session
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url="https://logiscore.com/account"
        )
        
        return {"url": session.url}
        
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create billing portal session: {str(e)}"
        )

@router.post("/toggle-auto-renewal")
async def toggle_auto_renewal(
    auto_renew_data: AutoRenewalToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle auto-renewal setting for the user's subscription"""
    try:
        # Check if user has an active subscription
        if not current_user.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Update Stripe subscription auto-renewal setting
        stripe_service = get_stripe_service()
        stripe_subscription = await stripe_service.update_subscription_auto_renewal(
            subscription_id=current_user.stripe_subscription_id,
            auto_renew=auto_renew_data.auto_renew_enabled
        )
        
        # Update database
        current_user.auto_renew_enabled = auto_renew_data.auto_renew_enabled
        db.commit()
        
        # Return confirmation
        status_message = "enabled" if auto_renew_data.auto_renew_enabled else "disabled"
        return {
            "message": f"Auto-renewal {status_message} successfully",
            "auto_renew_enabled": auto_renew_data.auto_renew_enabled,
            "subscription_id": current_user.stripe_subscription_id,
            "cancel_at_period_end": stripe_subscription.get('cancel_at_period_end', False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle auto-renewal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle auto-renewal: {str(e)}"
        ) 