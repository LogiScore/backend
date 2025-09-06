#!/usr/bin/env python3
"""
Admin Daily Summary Script

This script generates and sends a daily summary email to the admin at 6am.
It can be run manually or scheduled via cron.

Usage:
    python run_admin_daily_summary.py [--date YYYY-MM-DD]

If no date is provided, it will generate a summary for yesterday.
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from database.database import get_db
from services.admin_daily_summary_service import admin_daily_summary_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/admin_daily_summary.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the daily summary"""
    parser = argparse.ArgumentParser(description='Generate and send admin daily summary')
    parser.add_argument('--date', type=str, help='Date to generate summary for (YYYY-MM-DD). Defaults to yesterday.')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no email sent)')
    
    args = parser.parse_args()
    
    try:
        # Parse target date
        target_date = None
        if args.date:
            try:
                target_date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD format.")
                sys.exit(1)
        else:
            # Default to yesterday
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        
        logger.info(f"Starting admin daily summary for {target_date.date()}")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Generate summary data
            summary_data = await admin_daily_summary_service.generate_daily_summary(db, target_date)
            
            if args.test:
                logger.info("Test mode: Email not sent")
                logger.info(f"Summary data generated: {summary_data}")
                print("Test mode completed successfully")
            else:
                # Send email
                email_sent = await admin_daily_summary_service.send_daily_summary_email(summary_data)
                
                if email_sent:
                    logger.info("Daily summary email sent successfully")
                    print("Daily summary email sent successfully")
                else:
                    logger.error("Failed to send daily summary email")
                    print("Failed to send daily summary email")
                    sys.exit(1)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to run daily summary: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
