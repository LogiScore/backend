#!/usr/bin/env python3
"""
Migration script to add review subscription tables to the database.
This script safely adds the new tables without affecting existing data.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    return database_url

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {e}")
        return False

def create_review_subscriptions_table(engine):
    """Create the review_subscriptions table"""
    try:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS review_subscriptions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            freight_forwarder_id UUID REFERENCES freight_forwarders(id) ON DELETE CASCADE,
            location_country VARCHAR(100),
            location_city VARCHAR(100),
            review_type VARCHAR(50),
            notification_frequency VARCHAR(20) DEFAULT 'immediate',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        logger.info("✅ review_subscriptions table created successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to create review_subscriptions table: {e}")
        return False

def create_review_notifications_table(engine):
    """Create the review_notifications table"""
    try:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS review_notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
            subscription_id UUID NOT NULL REFERENCES review_subscriptions(id) ON DELETE CASCADE,
            notification_type VARCHAR(50) DEFAULT 'new_review',
            is_sent BOOLEAN DEFAULT FALSE,
            sent_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        
        logger.info("✅ review_notifications table created successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to create review_notifications table: {e}")
        return False

def create_indexes(engine):
    """Create indexes for better performance"""
    try:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_user_id ON review_subscriptions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_freight_forwarder_id ON review_subscriptions(freight_forwarder_id);",
            "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_location ON review_subscriptions(location_country, location_city);",
            "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_review_type ON review_subscriptions(review_type);",
            "CREATE INDEX IF NOT EXISTS idx_review_subscriptions_active ON review_subscriptions(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_review_notifications_user_id ON review_notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_review_notifications_review_id ON review_notifications(review_id);",
            "CREATE INDEX IF NOT EXISTS idx_review_notifications_subscription_id ON review_notifications(subscription_id);",
            "CREATE INDEX IF NOT EXISTS idx_review_notifications_sent ON review_notifications(is_sent, sent_at);"
        ]
        
        with engine.connect() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
            conn.commit()
        
        logger.info("✅ Indexes created successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        return False

def add_foreign_key_constraints(engine):
    """Add foreign key constraints if they don't exist"""
    try:
        # Check if constraints already exist
        inspector = inspect(engine)
        table_info = inspector.get_table_names()
        
        if 'review_subscriptions' not in table_info or 'review_notifications' not in table_info:
            logger.warning("Tables don't exist yet, skipping foreign key constraints")
            return True
        
        # Add foreign key constraints
        constraints = [
            """
            ALTER TABLE review_subscriptions 
            ADD CONSTRAINT IF NOT EXISTS fk_review_subscriptions_user 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE review_subscriptions 
            ADD CONSTRAINT IF NOT EXISTS fk_review_subscriptions_freight_forwarder 
            FOREIGN KEY (freight_forwarder_id) REFERENCES freight_forwarders(id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE review_notifications 
            ADD CONSTRAINT IF NOT EXISTS fk_review_notifications_user 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE review_notifications 
            ADD CONSTRAINT IF NOT EXISTS fk_review_notifications_review 
            FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE;
            """,
            """
            ALTER TABLE review_notifications 
            ADD CONSTRAINT IF NOT EXISTS fk_review_notifications_subscription 
            FOREIGN KEY (subscription_id) REFERENCES review_subscriptions(id) ON DELETE CASCADE;
            """
        ]
        
        with engine.connect() as conn:
            for constraint_sql in constraints:
                conn.execute(text(constraint_sql))
            conn.commit()
        
        logger.info("✅ Foreign key constraints added successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Failed to add foreign key constraints: {e}")
        return False

def verify_migration(engine):
    """Verify that all tables and constraints were created correctly"""
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        required_tables = ['review_subscriptions', 'review_notifications']
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check table structures
        for table_name in required_tables:
            columns = inspector.get_columns(table_name)
            logger.info(f"📋 Table {table_name} has {len(columns)} columns")
            
            # Log column names for verification
            column_names = [col['name'] for col in columns]
            logger.info(f"   Columns: {', '.join(column_names)}")
        
        logger.info("✅ Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False

def run_migration():
    """Run the complete migration"""
    logger.info("🚀 Starting review subscription tables migration...")
    
    try:
        # Get database connection
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        # Create tables
        if not create_review_subscriptions_table(engine):
            logger.error("❌ Failed to create review_subscriptions table")
            return False
        
        if not create_review_notifications_table(engine):
            logger.error("❌ Failed to create review_notifications table")
            return False
        
        # Create indexes
        if not create_indexes(engine):
            logger.error("❌ Failed to create indexes")
            return False
        
        # Add foreign key constraints
        if not add_foreign_key_constraints(engine):
            logger.error("❌ Failed to add foreign key constraints")
            return False
        
        # Verify migration
        if not verify_migration(engine):
            logger.error("❌ Migration verification failed")
            return False
        
        logger.info("🎉 Review subscription tables migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
