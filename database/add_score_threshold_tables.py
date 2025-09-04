#!/usr/bin/env python3
"""
Database migration script to add score threshold notification tables.
This script adds the necessary tables for shippers to subscribe to score threshold notifications.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add score threshold tables"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
        
        # Check if we're using PostgreSQL or SQLite
        is_postgres = database_url.startswith('postgres')
        
        # Ensure PostgreSQL dialect is specified
        if is_postgres:
            if not database_url.startswith('postgresql://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                if is_postgres:
                    # PostgreSQL version
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS score_threshold_subscriptions (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            freight_forwarder_id UUID NOT NULL REFERENCES freight_forwarders(id) ON DELETE CASCADE,
                            threshold_score NUMERIC(3,2) NOT NULL CHECK (threshold_score >= 0 AND threshold_score <= 5),
                            notification_frequency VARCHAR(20) DEFAULT 'immediate' CHECK (notification_frequency IN ('immediate', 'daily', 'weekly')),
                            is_active BOOLEAN DEFAULT TRUE,
                            expires_at TIMESTAMP WITH TIME ZONE,
                            last_notification_sent TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            UNIQUE(user_id, freight_forwarder_id)
                        );
                    """))
                    
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS score_threshold_notifications (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            freight_forwarder_id UUID NOT NULL REFERENCES freight_forwarders(id) ON DELETE CASCADE,
                            subscription_id UUID NOT NULL REFERENCES score_threshold_subscriptions(id) ON DELETE CASCADE,
                            previous_score NUMERIC(3,2) NOT NULL,
                            current_score NUMERIC(3,2) NOT NULL,
                            threshold_score NUMERIC(3,2) NOT NULL,
                            notification_type VARCHAR(50) DEFAULT 'score_threshold_breach' CHECK (notification_type IN ('score_threshold_breach', 'score_recovery')),
                            is_sent BOOLEAN DEFAULT FALSE,
                            sent_at TIMESTAMP WITH TIME ZONE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """))
                else:
                    # SQLite version
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS score_threshold_subscriptions (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            freight_forwarder_id TEXT NOT NULL,
                            threshold_score REAL NOT NULL CHECK (threshold_score >= 0 AND threshold_score <= 5),
                            notification_frequency TEXT DEFAULT 'immediate' CHECK (notification_frequency IN ('immediate', 'daily', 'weekly')),
                            is_active BOOLEAN DEFAULT 1,
                            expires_at DATETIME,
                            last_notification_sent DATETIME,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, freight_forwarder_id),
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY (freight_forwarder_id) REFERENCES freight_forwarders(id) ON DELETE CASCADE
                        );
                    """))
                    
                    connection.execute(text("""
                        CREATE TABLE IF NOT EXISTS score_threshold_notifications (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            freight_forwarder_id TEXT NOT NULL,
                            subscription_id TEXT NOT NULL,
                            previous_score REAL NOT NULL,
                            current_score REAL NOT NULL,
                            threshold_score REAL NOT NULL,
                            notification_type TEXT DEFAULT 'score_threshold_breach' CHECK (notification_type IN ('score_threshold_breach', 'score_recovery')),
                            is_sent BOOLEAN DEFAULT 0,
                            sent_at DATETIME,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY (freight_forwarder_id) REFERENCES freight_forwarders(id) ON DELETE CASCADE,
                            FOREIGN KEY (subscription_id) REFERENCES score_threshold_subscriptions(id) ON DELETE CASCADE
                        );
                    """))
                
                # Create indexes for better performance
                if is_postgres:
                    # PostgreSQL indexes
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_user_id 
                        ON score_threshold_subscriptions(user_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_freight_forwarder_id 
                        ON score_threshold_subscriptions(freight_forwarder_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_active 
                        ON score_threshold_subscriptions(is_active) WHERE is_active = TRUE;
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_user_id 
                        ON score_threshold_notifications(user_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_freight_forwarder_id 
                        ON score_threshold_notifications(freight_forwarder_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_created_at 
                        ON score_threshold_notifications(created_at);
                    """))
                else:
                    # SQLite indexes
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_user_id 
                        ON score_threshold_subscriptions(user_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_freight_forwarder_id 
                        ON score_threshold_subscriptions(freight_forwarder_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_subscriptions_active 
                        ON score_threshold_subscriptions(is_active);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_user_id 
                        ON score_threshold_notifications(user_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_freight_forwarder_id 
                        ON score_threshold_notifications(freight_forwarder_id);
                    """))
                    
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_score_threshold_notifications_created_at 
                        ON score_threshold_notifications(created_at);
                    """))
                
                # Commit transaction
                trans.commit()
                print("✅ Successfully created score threshold notification tables")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Error creating tables: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting score threshold tables migration...")
    run_migration()
    print("✅ Migration completed successfully!")
