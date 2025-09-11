from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import json
import stripe

from database.database import get_db
from database.models import User
from auth.auth import get_current_user
from services.subscription_service import SubscriptionService
from services.stripe_service import StripeService
from email_service import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services lazily to avoid import-time errors
subscription_service = None
stripe_service = None
email_service = None

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

def get_email_service():
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service

class SubscriptionRequest(BaseModel):
    plan_id: int
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

# Plan ID mapping - maps numeric IDs from frontend to display-friendly plan names
PLAN_ID_MAPPING = {
    1: "Free Shipper",           # Free shipper plan
    2: "Shipper Monthly",        # Shipper monthly
    3: "Shipper Annual",         # Shipper annual
    4: "Free Forwarder",         # Free forwarder plan
    5: "Forwarder Monthly",      # Forwarder monthly
    6: "Forwarder Annual",       # Forwarder annual
    7: "Forwarder Annual Plus"   # Forwarder annual plus
}

# Stripe tier mapping - maps numeric IDs to Stripe-compatible tier names
STRIPE_TIER_MAPPING = {
    1: "free",                   # Free shipper plan
    2: "shipper_monthly",        # Shipper monthly
    3: "shipper_annual",         # Shipper annual
    4: "free",                   # Free forwarder plan
    5: "forwarder_monthly",      # Forwarder monthly
    6: "forwarder_annual",       # Forwarder annual
    7: "forwarder_annual_plus"   # Forwarder annual plus
}

class AutoRenewalToggleRequest(BaseModel):
    auto_renew_enabled: bool

class PaymentIntentRequest(BaseModel):
    amount: int
    currency: str = 'usd'
    metadata: Optional[Dict[str, str]] = None

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str

@router.get("/stripe-config")
async def get_stripe_config():
    """Get Stripe configuration for frontend"""
    try:
        import os
        return {
            "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
            "stripe_enabled": bool(os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_PUBLISHABLE_KEY"))
        }
    except Exception as e:
        logger.error(f"Failed to get Stripe config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Stripe config: {str(e)}"
        )

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_request: PaymentIntentRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a payment intent for one-time payments"""
    try:
        stripe_service = get_stripe_service()
        
        # Create payment intent
        payment_intent = await stripe_service.create_payment_intent(
            amount=payment_request.amount,
            currency=payment_request.currency,
            customer_id=current_user.stripe_customer_id,
            metadata=payment_request.metadata
        )
        
        return PaymentIntentResponse(
            client_secret=payment_intent['client_secret'],
            payment_intent_id=payment_intent['id']
        )
        
    except Exception as e:
        logger.error(f"Failed to create payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription for the user"""
    try:
        # Handle both regular JSON and stringified JSON from frontend
        try:
            # Try to get JSON data directly
            body = await request.json()
        except Exception:
            # If that fails, try to parse as stringified JSON
            body_text = await request.body()
            try:
                body = json.loads(body_text.decode('utf-8'))
            except json.JSONDecodeError:
                # If it's already a string, try to parse it as JSON
                body_text_str = body_text.decode('utf-8')
                if body_text_str.startswith('"') and body_text_str.endswith('"'):
                    # Remove outer quotes and parse
                    body = json.loads(body_text_str[1:-1])
                else:
                    body = json.loads(body_text_str)
        
        # Create SubscriptionRequest from parsed data
        subscription_request = SubscriptionRequest(**body)
        
        # Map numeric plan_id to string-based plan identifier
        if subscription_request.plan_id not in PLAN_ID_MAPPING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan ID: {subscription_request.plan_id}"
            )
        
        # Get display name for database storage
        display_name = PLAN_ID_MAPPING[subscription_request.plan_id]
        
        # Get Stripe-compatible tier name for subscription creation
        stripe_tier = STRIPE_TIER_MAPPING[subscription_request.plan_id]
        
        # Validate user type matches plan type
        if current_user.user_type != subscription_request.user_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This plan is only available for {subscription_request.user_type}s"
            )
        
        # Use the Stripe-compatible tier for subscription creation
        tier = stripe_tier
        
        # Create subscription using the service
        subscription_service = get_subscription_service()
        subscription_result = await subscription_service.create_subscription(
            user_id=str(current_user.id),
            tier=tier,  # Stripe-compatible tier for subscription creation
            user_type=current_user.user_type,
            payment_method_id=subscription_request.payment_method_id,
            trial_days=subscription_request.trial_days,
            is_paid=subscription_request.payment_method_id is not None,
            db=db
        )
        
        # Update the database with the display name after subscription creation
        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            user.subscription_tier = display_name  # Store display name in database
            db.commit()
        
        return SubscriptionResponse(
            subscription_id=subscription_result['subscription_id'],
            message=f"Successfully upgraded to {subscription_request.plan_name}!",
            tier=subscription_result['tier'],
            status=subscription_result['status']
        )
        
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        
        # Provide more specific error messages for common issues
        error_message = str(e)
        if "Payment method not found" in error_message or "No such PaymentMethod" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment method not found. Please try creating a new payment method or check that you're using the correct Stripe account."
            )
        elif "Payment method validation failed" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method. Please ensure the payment method exists and try again."
            )
        elif "No Stripe price configured" in error_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Subscription pricing not configured. Please contact support."
            )
        else:
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
        # Check if user has an active subscription (check subscription tier and status)
        if not current_user.subscription_tier or current_user.subscription_tier == 'free':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Check if subscription is active or trial
        if current_user.subscription_status not in ['active', 'trial']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Update Stripe subscription auto-renewal setting if Stripe subscription exists
        stripe_subscription = None
        if current_user.stripe_subscription_id:
            try:
                stripe_service = get_stripe_service()
                stripe_subscription = await stripe_service.update_subscription_auto_renewal(
                    subscription_id=current_user.stripe_subscription_id,
                    auto_renew=auto_renew_data.auto_renew_enabled
                )
            except Exception as stripe_error:
                logger.warning(f"Failed to update Stripe subscription auto-renewal: {str(stripe_error)}")
                # Continue with database update even if Stripe update fails
        
        # Update database
        current_user.auto_renew_enabled = auto_renew_data.auto_renew_enabled
        db.commit()
        
        # Send email notification
        try:
            email_service = get_email_service()
            await email_service.send_auto_renewal_toggle_notification(
                to_email=current_user.email,
                user_name=current_user.full_name or current_user.username,
                auto_renew_enabled=auto_renew_data.auto_renew_enabled,
                subscription_tier=current_user.subscription_tier
            )
        except Exception as email_error:
            logger.warning(f"Failed to send auto-renewal toggle notification email: {str(email_error)}")
            # Continue with the response even if email fails
        
        # Return confirmation
        status_message = "enabled" if auto_renew_data.auto_renew_enabled else "disabled"
        return {
            "message": f"Auto-renewal {status_message} successfully",
            "auto_renew_enabled": auto_renew_data.auto_renew_enabled,
            "subscription_tier": current_user.subscription_tier,
            "subscription_status": current_user.subscription_status,
            "stripe_subscription_id": current_user.stripe_subscription_id,
            "cancel_at_period_end": stripe_subscription.get('cancel_at_period_end', False) if stripe_subscription else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle auto-renewal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle auto-renewal: {str(e)}"
        ) 