import stripe
import os
from typing import Optional, Dict, Any
from database.models import User
from database.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        self.stripe = stripe
        # Ensure Stripe is configured
        if not os.getenv('STRIPE_SECRET_KEY'):
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Stripe price IDs (configure these in Stripe dashboard)
        # Updated to match actual Stripe products
        self.STRIPE_PRICE_IDS = {
            'free': None,
            'shipper_monthly': os.getenv('STRIPE_SHIPPER_MONTHLY_PRICE_ID'),
            'shipper_annual': os.getenv('STRIPE_SHIPPER_ANNUAL_PRICE_ID'),
            'forwarder_monthly': os.getenv('STRIPE_FORWARDER_MONTHLY_PRICE_ID'),
            'forwarder_annual': os.getenv('STRIPE_FORWARDER_ANNUAL_PRICE_ID'),
            'forwarder_annual_plus': os.getenv('STRIPE_FORWARDER_ANNUAL_PLUS_PRICE_ID')
        }
    
    async def create_customer(self, user: User) -> str:
        """Create Stripe customer and return customer ID"""
        try:
            customer = self.stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.username,
                metadata={
                    'user_id': str(user.id),
                    'user_type': user.user_type
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve existing Stripe customer"""
        try:
            return self.stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve Stripe customer: {str(e)}")
            raise Exception(f"Failed to retrieve Stripe customer: {str(e)}")
    
    async def update_customer(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Update Stripe customer details"""
        try:
            return self.stripe.Customer.modify(customer_id, **kwargs)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe customer: {str(e)}")
            raise Exception(f"Failed to update Stripe customer: {str(e)}")
    
    async def delete_customer(self, customer_id: str) -> bool:
        """Delete Stripe customer"""
        try:
            self.stripe.Customer.delete(customer_id)
            return True
        except stripe.error.StripeError as e:
            logger.error(f"Failed to delete Stripe customer: {str(e)}")
            raise Exception(f"Failed to delete Stripe customer: {str(e)}")
    
    async def create_subscription(
        self, 
        customer_id: str, 
        price_id: str,
        trial_days: int = 0,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create Stripe subscription"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'metadata': metadata or {}
            }
            
            if trial_days > 0:
                subscription_data['trial_period_days'] = trial_days
            
            subscription = self.stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel Stripe subscription"""
        try:
            return self.stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    async def reactivate_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Reactivate canceled subscription"""
        try:
            return self.stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=False
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to reactivate subscription: {str(e)}")
            raise Exception(f"Failed to reactivate subscription: {str(e)}")
    
    async def update_subscription_plan(self, subscription_id: str, new_price_id: str) -> Dict[str, Any]:
        """Update subscription to different plan"""
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            self.stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='create_prorations',
            )
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            raise Exception(f"Failed to update subscription: {str(e)}")
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Retrieve subscription details"""
        try:
            return self.stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription: {str(e)}")
            raise Exception(f"Failed to retrieve subscription: {str(e)}")
    
    async def create_payment_intent(
        self, 
        amount: int, 
        currency: str = 'usd',
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create payment intent for one-time payments"""
        try:
            intent_data = {
                'amount': amount,
                'currency': currency,
                'metadata': metadata or {}
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            return self.stripe.PaymentIntent.create(**intent_data)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {str(e)}")
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    async def attach_payment_method(self, payment_method_id: str, customer_id: str) -> Dict[str, Any]:
        """Attach payment method to customer"""
        try:
            return self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to attach payment method: {str(e)}")
            raise Exception(f"Failed to attach payment method: {str(e)}")
    
    async def get_price_id_for_tier(self, tier: str, user_type: str) -> Optional[str]:
        """Get Stripe price ID for subscription tier"""
        # First try the tier directly
        if tier in self.STRIPE_PRICE_IDS:
            return self.STRIPE_PRICE_IDS.get(tier)
        
        # Then try constructing the key with user_type
        tier_key = f"{user_type}_{tier}"
        return self.STRIPE_PRICE_IDS.get(tier_key)
    
    async def verify_webhook_signature(self, payload: bytes, sig_header: str, webhook_secret: str) -> Dict[str, Any]:
        """Verify Stripe webhook signature"""
        try:
            return self.stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise stripe.error.SignatureVerificationError("Invalid signature", sig_header)
