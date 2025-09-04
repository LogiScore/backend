#!/usr/bin/env python3
"""
Scheduled task to check score thresholds and clean up expired subscriptions.
This script should be run periodically (e.g., every hour) to monitor score changes
and send notifications when thresholds are breached.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from services.score_threshold_service import score_threshold_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/score_threshold_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run score threshold checks"""
    try:
        logger.info("🚀 Starting score threshold check process...")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Step 1: Clean up expired subscriptions
            logger.info("🧹 Cleaning up expired subscriptions...")
            expired_count = await score_threshold_service.cleanup_expired_subscriptions(db)
            logger.info(f"✅ Cleaned up {expired_count} expired subscriptions")
            
            # Step 2: Process all score thresholds
            logger.info("📊 Processing score thresholds for all freight forwarders...")
            results = await score_threshold_service.process_all_score_thresholds(db)
            
            logger.info(f"✅ Score threshold check completed:")
            logger.info(f"   - Processed forwarders: {results['processed_forwarders']}")
            logger.info(f"   - Notifications sent: {results['notifications_sent']}")
            logger.info(f"   - Errors: {results['errors']}")
            
        finally:
            db.close()
            
        logger.info("✅ Score threshold check process completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Score threshold check process failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
