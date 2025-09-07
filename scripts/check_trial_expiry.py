#!/usr/bin/env python3
"""
Trial Expiry Check Script

This script checks for trials ending soon and sends appropriate notifications.
It can be run as a cron job or scheduled task.

Usage:
    python check_trial_expiry.py [--hours-ahead HOURS] [--dry-run]

Environment Variables:
    BACKEND_API_URL: Base URL for the backend API (default: http://localhost:8000)
    ADMIN_API_TOKEN: Admin token for API authentication
"""

import os
import sys
import requests
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trial_expiry_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
ADMIN_TOKEN = os.getenv('ADMIN_API_TOKEN')

def get_plan_features(plan_tier: str) -> List[str]:
    """Get plan features based on tier"""
    features = {
        'monthly': [
            'Search for Forwarders and view aggregated scores',
            'Full numerical score display',
            'Single user subscription'
        ],
        'annual': [
            'Everything in Monthly plan',
            'Email notifications for new reviews',
            'Score trend analytics',
            'Save $38/year compared to monthly'
        ],
        'enterprise': [
            'Everything in Annual plan',
            'Up to three concurrent users',
            'Manage forwarder profile',
            'Branded ads on profile page',
            'Comment on reviews',
            'Best in location badge'
        ]
    }
    return features.get(plan_tier, [])

def get_plan_details(plan_tier: str) -> Dict[str, Any]:
    """Get plan details based on tier"""
    plan_details = {
        'monthly': {
            'plan_name': 'Subscription Monthly',
            'plan_price': 38,
            'billing_cycle': 'month'
        },
        'annual': {
            'plan_name': 'Subscription Annual',
            'plan_price': 418,
            'billing_cycle': 'year'
        },
        'enterprise': {
            'plan_name': 'Subscription Enterprise',
            'plan_price': 3450,
            'billing_cycle': 'year'
        }
    }
    
    return plan_details.get(plan_tier, {
        'plan_name': 'Subscription',
        'plan_price': 0,
        'billing_cycle': 'month'
    })

def check_trials_ending_soon(hours_ahead: int = 24, dry_run: bool = False) -> None:
    """Check for trials ending soon and send warnings"""
    try:
        logger.info(f"Checking for trials ending in next {hours_ahead} hours")
        
        if not ADMIN_TOKEN:
            logger.error("ADMIN_API_TOKEN environment variable not set")
            return
        
        # Get trials ending soon
        response = requests.get(
            f"{API_BASE_URL}/api/notifications/trials-ending-soon",
            params={'hours_ahead': hours_ahead},
            headers={'Authorization': f'Bearer {ADMIN_TOKEN}'},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get trials ending soon: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        trials = data.get('trials_ending', [])
        
        logger.info(f"Found {len(trials)} trials ending soon")
        
        if dry_run:
            logger.info("DRY RUN: Would send trial warnings to:")
            for trial in trials:
                logger.info(f"  - {trial['email']} ({trial['plan_name']}) - ends {trial['trial_end_date']}")
            return
        
        # Send trial warnings
        warnings_sent = 0
        for trial in trials:
            try:
                # Prepare trial data
                plan_details = get_plan_details(trial['subscription_tier'])
                warning_data = {
                    'trial_duration': 7,  # Default
                    'plan_name': plan_details['plan_name'],
                    'plan_price': plan_details['plan_price'],
                    'billing_cycle': plan_details['billing_cycle'],
                    'trial_end_date': trial['trial_end_date'],
                    'plan_features': get_plan_features(trial['subscription_tier']),
                    'plan_id': trial['subscription_tier']
                }
                
                # Send trial warning
                warning_response = requests.post(
                    f"{API_BASE_URL}/api/notifications/send-trial-warning",
                    headers={
                        'Authorization': f'Bearer {ADMIN_TOKEN}',
                        'Content-Type': 'application/json'
                    },
                    json={'user_id': trial['user_id'], **warning_data},
                    timeout=30
                )
                
                if warning_response.status_code == 200:
                    warnings_sent += 1
                    logger.info(f"Trial warning sent to {trial['email']}")
                else:
                    logger.error(f"Failed to send warning to {trial['email']}: {warning_response.status_code} - {warning_response.text}")
                    
            except Exception as e:
                logger.error(f"Error processing trial for {trial.get('email', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Trial warning process completed. Sent {warnings_sent} warnings out of {len(trials)} trials")
        
    except Exception as e:
        logger.error(f"Error in check_trials_ending_soon: {str(e)}")

def process_ended_trials(dry_run: bool = False) -> None:
    """Process trials that have ended and send notifications"""
    try:
        logger.info("Processing ended trials")
        
        if not ADMIN_TOKEN:
            logger.error("ADMIN_API_TOKEN environment variable not set")
            return
        
        # Get trials that ended in the last 24 hours
        response = requests.get(
            f"{API_BASE_URL}/api/notifications/trials-ending-soon",
            params={'hours_ahead': -24},  # Negative hours to get past trials
            headers={'Authorization': f'Bearer {ADMIN_TOKEN}'},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get ended trials: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        ended_trials = data.get('trials_ending', [])
        
        logger.info(f"Found {len(ended_trials)} trials that ended recently")
        
        if dry_run:
            logger.info("DRY RUN: Would send trial ended notifications to:")
            for trial in ended_trials:
                logger.info(f"  - {trial['email']} ({trial['plan_name']}) - ended {trial['trial_end_date']}")
            return
        
        # Send trial ended notifications
        notifications_sent = 0
        for trial in ended_trials:
            try:
                # Prepare trial data
                plan_details = get_plan_details(trial['subscription_tier'])
                trial_data = {
                    'trial_duration': 7,  # Default
                    'plan_name': plan_details['plan_name'],
                    'plan_price': plan_details['plan_price'],
                    'billing_cycle': plan_details['billing_cycle'],
                    'trial_end_date': trial['trial_end_date'],
                    'plan_id': trial['subscription_tier']
                }
                
                # Send trial ended notification
                ended_response = requests.post(
                    f"{API_BASE_URL}/api/notifications/send-trial-ended",
                    headers={
                        'Authorization': f'Bearer {ADMIN_TOKEN}',
                        'Content-Type': 'application/json'
                    },
                    json={'user_id': trial['user_id'], **trial_data},
                    timeout=30
                )
                
                if ended_response.status_code == 200:
                    notifications_sent += 1
                    logger.info(f"Trial ended notification sent to {trial['email']}")
                else:
                    logger.error(f"Failed to send ended notification to {trial['email']}: {ended_response.status_code} - {ended_response.text}")
                    
            except Exception as e:
                logger.error(f"Error processing ended trial for {trial.get('email', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Trial ended notification process completed. Sent {notifications_sent} notifications out of {len(ended_trials)} trials")
        
    except Exception as e:
        logger.error(f"Error in process_ended_trials: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Check trial expiry and send notifications')
    parser.add_argument('--hours-ahead', type=int, default=24, 
                       help='Number of hours ahead to check for trials ending (default: 24)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in dry-run mode (no actual emails sent)')
    parser.add_argument('--process-ended', action='store_true',
                       help='Process trials that have already ended')
    
    args = parser.parse_args()
    
    logger.info(f"Starting trial expiry check script (dry_run={args.dry_run})")
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"Admin Token: {'Set' if ADMIN_TOKEN else 'Not set'}")
    
    if args.process_ended:
        process_ended_trials(dry_run=args.dry_run)
    else:
        check_trials_ending_soon(hours_ahead=args.hours_ahead, dry_run=args.dry_run)
    
    logger.info("Trial expiry check script completed")

if __name__ == "__main__":
    main()
