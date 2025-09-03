#!/usr/bin/env python3
"""
Add database indexes for notification system performance optimization.
This script adds the required indexes for the review subscription and notification system.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    # Try different environment variable names
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Try constructing from individual components
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'logiscore')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        if db_password:
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            database_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    return database_url

def add_notification_indexes():
    """Add indexes for notification system performance"""
    try:
        database_url = get_database_url()
        if not database_url:
            logger.error("No database URL found in environment variables")
            return False
        
        logger.info(f"Connecting to database...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Indexes for review_subscriptions table
                indexes_to_create = [
                    {
                        "name": "idx_review_subscriptions_user_id",
                        "table": "review_subscriptions",
                        "columns": "user_id",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_user_id ON review_subscriptions(user_id);"
                    },
                    {
                        "name": "idx_review_subscriptions_forwarder",
                        "table": "review_subscriptions", 
                        "columns": "freight_forwarder_id",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_forwarder ON review_subscriptions(freight_forwarder_id);"
                    },
                    {
                        "name": "idx_review_subscriptions_location",
                        "table": "review_subscriptions",
                        "columns": "location_country, location_city",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_location ON review_subscriptions(location_country, location_city);"
                    },
                    {
                        "name": "idx_review_subscriptions_active",
                        "table": "review_subscriptions",
                        "columns": "is_active",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_active ON review_subscriptions(is_active);"
                    },
                    {
                        "name": "idx_review_subscriptions_composite",
                        "table": "review_subscriptions",
                        "columns": "is_active, freight_forwarder_id, location_country, location_city",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_composite ON review_subscriptions(is_active, freight_forwarder_id, location_country, location_city);"
                    },
                    # Indexes for review_notifications table
                    {
                        "name": "idx_review_notifications_user_id",
                        "table": "review_notifications",
                        "columns": "user_id",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_notifications_user_id ON review_notifications(user_id);"
                    },
                    {
                        "name": "idx_review_notifications_sent",
                        "table": "review_notifications",
                        "columns": "is_sent, sent_at",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_notifications_sent ON review_notifications(is_sent, sent_at);"
                    },
                    {
                        "name": "idx_review_notifications_review_id",
                        "table": "review_notifications",
                        "columns": "review_id",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_notifications_review_id ON review_notifications(review_id);"
                    },
                    {
                        "name": "idx_review_notifications_subscription_id",
                        "table": "review_notifications",
                        "columns": "subscription_id",
                        "sql": "CREATE INDEX IF NOT EXISTS idx_review_notifications_subscription_id ON review_notifications(subscription_id);"
                    }
                ]
                
                # Create each index
                for index_info in indexes_to_create:
                    try:
                        logger.info(f"Creating index: {index_info['name']} on {index_info['table']}({index_info['columns']})")
                        conn.execute(text(index_info['sql']))
                        logger.info(f"✓ Index {index_info['name']} created successfully")
                    except SQLAlchemyError as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"✓ Index {index_info['name']} already exists")
                        else:
                            logger.error(f"✗ Failed to create index {index_info['name']}: {str(e)}")
                            raise
                
                # Commit the transaction
                trans.commit()
                logger.info("✓ All notification indexes created successfully")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                logger.error(f"✗ Error creating indexes: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database connection error: {str(e)}")
        return False

def check_existing_indexes():
    """Check which indexes already exist"""
    try:
        database_url = get_database_url()
        if not database_url:
            logger.error("No database URL found in environment variables")
            return
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Query to check existing indexes
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE tablename IN ('review_subscriptions', 'review_notifications')
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname;
            """)
            
            result = conn.execute(query)
            indexes = result.fetchall()
            
            if indexes:
                logger.info("Existing notification-related indexes:")
                for index in indexes:
                    logger.info(f"  - {index.indexname} on {index.tablename}")
            else:
                logger.info("No existing notification-related indexes found")
                
    except Exception as e:
        logger.error(f"Error checking existing indexes: {str(e)}")

def main():
    """Main function"""
    logger.info("=== LogiScore Notification Index Creation ===")
    
    # Check existing indexes first
    logger.info("Checking existing indexes...")
    check_existing_indexes()
    
    # Add new indexes
    logger.info("\nAdding notification system indexes...")
    success = add_notification_indexes()
    
    if success:
        logger.info("\n✓ Notification index creation completed successfully!")
        logger.info("The notification system should now have optimal database performance.")
    else:
        logger.error("\n✗ Notification index creation failed!")
        logger.error("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
