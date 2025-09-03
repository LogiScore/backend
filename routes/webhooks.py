from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import stripe
import os
import logging
from typing import Dict, Any
from database.database import get_db
from services.subscription_service import SubscriptionService
from email_service import EmailService

router = APIRouter()
logger = logging.getLogger(__name__)

# Get webhook secret from environment
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook signature verification disabled")

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle different event types
    try:
        if event['type'] == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event)
        elif event['type'] == 'invoice.payment_failed':
            await handle_payment_failed(event)
        elif event['type'] == 'customer.subscription.deleted':
            await handle_subscription_deleted(event)
        elif event['type'] == 'customer.subscription.updated':
            await handle_subscription_updated(event)
        elif event['type'] == 'customer.subscription.trial_will_end':
            await handle_trial_ending(event)
        elif event['type'] == 'customer.subscription.created':
            await handle_subscription_created(event)
        elif event['type'] == 'invoice.payment_action_required':
            await handle_payment_action_required(event)
        elif event['type'] == 'review.created':
            await handle_review_created(event)
        elif event['type'] == 'review.updated':
            await handle_review_updated(event)
        
        logger.info(f"Successfully processed webhook: {event['type']}")
        return {"status": "success", "event_type": event['type']}
        
    except Exception as e:
        # Log error but don't fail webhook
        logger.error(f"Error processing webhook {event['type']}: {str(e)}")
        return {"status": "error", "message": str(e)}

async def handle_payment_succeeded(event: Dict[str, Any]):
    """Handle successful payment"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            db = next(get_db())
            subscription_service = SubscriptionService()
            email_service = EmailService()
            
            # Update subscription status
            await subscription_service.update_payment_status(subscription_id, 'paid')
            
            # Send confirmation email
            await email_service.send_payment_confirmation(invoice)
            
            logger.info(f"Payment succeeded for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment succeeded: {str(e)}")

async def handle_payment_failed(event: Dict[str, Any]):
    """Handle failed payment"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            db = next(get_db())
            subscription_service = SubscriptionService()
            email_service = EmailService()
            
            # Update subscription status
            await subscription_service.update_payment_status(subscription_id, 'failed')
            
            # Send failure notification
            await email_service.send_payment_failed_notification(invoice)
            
            logger.info(f"Payment failed for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")

async def handle_subscription_deleted(event: Dict[str, Any]):
    """Handle subscription deletion"""
    try:
        subscription = event['data']['object']
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            db = next(get_db())
            subscription_service = SubscriptionService()
            email_service = EmailService()
            
            # Update user subscription status
            await subscription_service.mark_subscription_expired(user_id)
            
            # Send expiration email
            await email_service.send_subscription_expired_notification(user_id)
            
            logger.info(f"Subscription deleted for user: {user_id}")
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")

async def handle_subscription_updated(event: Dict[str, Any]):
    """Handle subscription updates"""
    try:
        subscription = event['data']['object']
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            db = next(get_db())
            subscription_service = SubscriptionService()
            
            # Get current subscription status
            current_status = subscription.status
            old_tier = subscription.metadata.get('old_tier', 'unknown')
            new_tier = subscription.metadata.get('new_tier', 'unknown')
            
            # Update subscription details in database
            await subscription_service.update_subscription_from_stripe(subscription)
            
            # Check if subscription was downgraded to free/basic tier
            if current_status in ['canceled', 'past_due', 'unpaid'] or new_tier in ['free', 'basic']:
                try:
                    # Trigger notification cleanup
                    await cleanup_user_notifications(user_id, old_tier, new_tier, db)
                except Exception as e:
                    logger.error(f"Failed to cleanup notifications for user {user_id}: {str(e)}")
            
            logger.info(f"Subscription updated for user: {user_id}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")

async def handle_trial_ending(event: Dict[str, Any]):
    """Handle trial ending (3 days before)"""
    try:
        subscription = event['data']['object']
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            email_service = EmailService()
            
            # Send trial ending warning
            await email_service.send_trial_ending_warning(user_id)
            
            logger.info(f"Trial ending warning sent for user: {user_id}")
    except Exception as e:
        logger.error(f"Error handling trial ending: {str(e)}")

async def handle_subscription_created(event: Dict[str, Any]):
    """Handle new subscription creation"""
    try:
        subscription = event['data']['object']
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            email_service = EmailService()
            
            # Send welcome email
            await email_service.send_subscription_welcome(user_id, subscription)
            
            logger.info(f"Subscription created for user: {user_id}")
    except Exception as e:
        logger.error(f"Error handling subscription created: {str(e)}")

async def handle_payment_action_required(event: Dict[str, Any]):
    """Handle payment action required (e.g., 3D Secure)"""
    try:
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        
        if subscription_id:
            email_service = EmailService()
            
            # Send payment action required notification
            await email_service.send_payment_action_required_notification(invoice)
            
            logger.info(f"Payment action required for subscription: {subscription_id}")
    except Exception as e:
        logger.error(f"Error handling payment action required: {str(e)}")

async def handle_review_created(event: Dict[str, Any]):
    """Handle new review creation"""
    try:
        review_data = event['data']['object']
        review_id = review_data.get('id')
        
        if review_id:
            db = next(get_db())
            from services.notification_service import notification_service
            
            # Process the new review for notifications
            await notification_service.process_new_review(review_id, db)
            
            logger.info(f"Processed new review webhook: {review_id}")
    except Exception as e:
        logger.error(f"Error handling review created: {str(e)}")

async def handle_review_updated(event: Dict[str, Any]):
    """Handle review updates"""
    try:
        review_data = event['data']['object']
        review_id = review_data.get('id')
        
        if review_id:
            db = next(get_db())
            from services.notification_service import notification_service
            
            # Process the updated review for notifications (if needed)
            # This could trigger notifications for users subscribed to review updates
            await notification_service.process_new_review(review_id, db)
            
            logger.info(f"Processed review update webhook: {review_id}")
    except Exception as e:
        logger.error(f"Error handling review updated: {str(e)}")

async def cleanup_user_notifications(user_id: str, old_tier: str, new_tier: str, db: Session):
    """
    Clean up notification subscriptions when user subscription is downgraded.
    This function calls the notification cleanup endpoint internally.
    """
    try:
        import httpx
        
        # Determine cleanup reason
        cleanup_reason = "downgrade"
        if new_tier in ['free', 'basic']:
            cleanup_reason = "downgrade"
        elif old_tier in ['free', 'basic']:
            cleanup_reason = "expiry"
        
        # Prepare cleanup data
        cleanup_data = {
            "user_id": user_id,
            "old_subscription_tier": old_tier,
            "new_subscription_tier": new_tier,
            "cleanup_reason": cleanup_reason
        }
        
        # Call the notification cleanup endpoint internally
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/notifications/cleanup-subscriptions",
                json=cleanup_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Notification cleanup completed for user {user_id}: {result.get('deleted_subscriptions', 0)} subscriptions removed")
            else:
                logger.error(f"Failed to cleanup notifications: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error cleaning up notifications for user {user_id}: {str(e)}")
        # Don't raise the exception - we don't want cleanup failures to break webhook processing

@router.get("/stripe/webhook/test")
async def test_webhook_endpoint():
    """Test endpoint to verify webhook router is accessible"""
    return {"message": "Stripe webhook endpoint is accessible", "status": "ready"}
