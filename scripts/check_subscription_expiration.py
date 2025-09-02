#!/usr/bin/env python3
"""
Subscription Expiration Check Script
This script can be run as a scheduled task (cron job) to automatically check for expiring subscriptions
and send notifications to users.

Usage:
    python3 scripts/check_subscription_expiration.py

Recommended cron schedule:
    # Check every day at 9:00 AM
    0 9 * * * cd /path/to/logiscore/backend && python3 scripts/check_subscription_expiration.py
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.subscription_expiration_service import SubscriptionExpirationService
from database.database import get_db

# Configure logging
import os

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/subscription_expiration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main function to check subscription expiration"""
    try:
        logger.info("Starting scheduled subscription expiration check")
        
        # Get database session
        db = next(get_db())
        
        # Create expiration service
        expiration_service = SubscriptionExpirationService()
        
        # Check for expiring subscriptions
        result = await expiration_service.check_expiring_subscriptions(db=db)
        
        # Log results
        logger.info(f"Subscription expiration check completed successfully")
        logger.info(f"Notifications sent: {result.get('notifications_sent', 0)}")
        logger.info(f"Subscriptions reverted: {result.get('subscriptions_reverted', 0)}")
        logger.info(f"Checked at: {result.get('checked_at', 'unknown')}")
        
        # Log detailed results if any
        if result.get('notification_results'):
            logger.info("Notification results:")
            for notification in result['notification_results']:
                logger.info(f"  - User {notification.get('user_id')}: {notification.get('days_until_expiry')} days remaining")
        
        if result.get('reversion_results'):
            logger.info("Reversion results:")
            for reversion in result['reversion_results']:
                logger.info(f"  - User {reversion.get('user_id')}: {reversion.get('previous_tier')} -> {reversion.get('new_tier')}")
        
        logger.info("Scheduled subscription expiration check completed successfully")
        
    except Exception as e:
        logger.error(f"Error during scheduled subscription expiration check: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
