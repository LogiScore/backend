#!/usr/bin/env python3
"""
Database migration script to create promotion system tables
Run this script to add the promotion_config and user_rewards tables to the database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_promotion_tables():
    """Create promotion system tables"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("Error: DATABASE_URL not found in environment variables")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create promotion_config table
        promotion_config_sql = """
        CREATE TABLE IF NOT EXISTS promotion_config (
            id SERIAL PRIMARY KEY,
            is_active BOOLEAN DEFAULT true,
            max_rewards_per_user INTEGER DEFAULT 3,
            reward_months INTEGER DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create user_rewards table
        user_rewards_sql = """
        CREATE TABLE IF NOT EXISTS user_rewards (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id),
            review_id UUID REFERENCES reviews(id),
            months_awarded INTEGER NOT NULL,
            awarded_at TIMESTAMP DEFAULT NOW(),
            awarded_by UUID REFERENCES users(id),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute SQL commands
        print("Creating promotion_config table...")
        session.execute(text(promotion_config_sql))
        
        print("Creating user_rewards table...")
        session.execute(text(user_rewards_sql))
        
        # Insert default promotion configuration
        insert_default_config_sql = """
        INSERT INTO promotion_config (is_active, max_rewards_per_user, reward_months, description)
        VALUES (true, 3, 1, 'Get 1 month free subscription for each review submitted (max 3 months)')
        ON CONFLICT (id) DO NOTHING;
        """
        
        print("Inserting default promotion configuration...")
        session.execute(text(insert_default_config_sql))
        
        # Commit changes
        session.commit()
        print("✅ Promotion tables created successfully!")
        
        # Verify tables were created
        verify_sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name IN ('promotion_config', 'user_rewards');
        """
        
        result = session.execute(text(verify_sql))
        tables = [row[0] for row in result.fetchall()]
        
        if 'promotion_config' in tables and 'user_rewards' in tables:
            print("✅ Tables verified successfully!")
            print(f"Created tables: {', '.join(tables)}")
        else:
            print("❌ Table verification failed!")
            return False
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating promotion tables: {str(e)}")
        if 'session' in locals():
            session.rollback()
            session.close()
        return False

if __name__ == "__main__":
    print("🚀 Starting promotion tables creation...")
    success = create_promotion_tables()
    
    if success:
        print("🎉 Promotion system setup completed successfully!")
        print("\nNext steps:")
        print("1. The promotion API endpoints are now available at /api/promotions/")
        print("2. Users will automatically receive rewards when they submit reviews")
        print("3. Admins can manage promotion settings via the API")
    else:
        print("💥 Promotion system setup failed!")
        sys.exit(1)
