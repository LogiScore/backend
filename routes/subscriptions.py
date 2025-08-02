from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import stripe
import os
from datetime import datetime, timedelta

from database.database import get_db
from database.models import User
from auth.auth import get_current_user

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class SubscriptionRequest(BaseModel):
    plan_id: str
    plan_name: str
    user_type: str

class SubscriptionResponse(BaseModel):
    subscription_id: str
    client_secret: Optional[str] = None
    checkout_url: Optional[str] = None
    message: str

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
        
        # For now, we'll simulate the subscription creation
        # In a real implementation, you would integrate with Stripe here
        
        # Update user subscription in database
        current_user.subscription_tier = subscription_request.plan_name.lower().replace(' ', '_')
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return SubscriptionResponse(
            subscription_id="simulated_subscription_id",
            message=f"Successfully upgraded to {subscription_request.plan_name}!"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/plans")
async def get_subscription_plans(
    current_user: User = Depends(get_current_user)
):
    """Get available subscription plans for the user's type"""
    try:
        # Define plans based on user type
        plans = {
            "shipper": [
                {
                    "id": "shipper-basic",
                    "name": "Shipper Basic",
                    "description": "Essential features for small to medium shippers",
                    "price": 29,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "features": [
                        "Access to freight forwarder reviews",
                        "Basic search and filtering",
                        "Contact information for forwarders",
                        "Email support"
                    ]
                },
                {
                    "id": "shipper-premium",
                    "name": "Shipper Premium",
                    "description": "Advanced features for growing businesses",
                    "price": 79,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "is_popular": True,
                    "features": [
                        "All Basic features",
                        "Priority customer support",
                        "Advanced analytics and reporting",
                        "Custom alerts and notifications",
                        "API access for integrations",
                        "Dedicated account manager"
                    ]
                },
                {
                    "id": "shipper-enterprise",
                    "name": "Shipper Enterprise",
                    "description": "Full-featured solution for large enterprises",
                    "price": 199,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "features": [
                        "All Premium features",
                        "White-label solutions",
                        "Custom integrations",
                        "24/7 phone support",
                        "Advanced security features",
                        "Multi-user management"
                    ]
                }
            ],
            "forwarder": [
                {
                    "id": "forwarder-basic",
                    "name": "Forwarder Basic",
                    "description": "Essential features for freight forwarders",
                    "price": 49,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "features": [
                        "Company profile listing",
                        "Basic review management",
                        "Customer inquiry responses",
                        "Email support"
                    ]
                },
                {
                    "id": "forwarder-premium",
                    "name": "Forwarder Premium",
                    "description": "Advanced features for established forwarders",
                    "price": 99,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "is_popular": True,
                    "features": [
                        "All Basic features",
                        "Advanced analytics dashboard",
                        "Review response automation",
                        "Priority listing placement",
                        "Marketing tools and insights",
                        "Dedicated account manager"
                    ]
                },
                {
                    "id": "forwarder-enterprise",
                    "name": "Forwarder Enterprise",
                    "description": "Complete solution for large forwarders",
                    "price": 299,
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "features": [
                        "All Premium features",
                        "Custom branding options",
                        "Advanced API access",
                        "24/7 phone support",
                        "Multi-location management",
                        "Advanced dispute resolution tools"
                    ]
                }
            ]
        }
        
        user_plans = plans.get(current_user.user_type, [])
        return {"plans": user_plans}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription plans: {str(e)}"
        )

@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get the user's current subscription details"""
    try:
        return {
            "subscription_tier": current_user.subscription_tier,
            "user_type": current_user.user_type,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current subscription: {str(e)}"
        ) 