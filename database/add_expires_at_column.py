#!/usr/bin/env python3
"""
Database migration script to add expires_at column to score_threshold_subscriptions table.
This script adds the missing expires_at column that was not created in the initial migration.
"""

import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add expires_at column"""
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
                # Check if expires_at column already exists
                if is_postgres:
                    check_column_query = """
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'score_threshold_subscriptions' 
                        AND column_name = 'expires_at'
                    """
                else:
                    check_column_query = """
                        SELECT name 
                        FROM pragma_table_info('score_threshold_subscriptions') 
                        WHERE name = 'expires_at'
                    """
                
                result = connection.execute(text(check_column_query))
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    # Add expires_at column
                    if is_postgres:
                        connection.execute(text("""
                            ALTER TABLE score_threshold_subscriptions 
                            ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE;
                        """))
                    else:
                        connection.execute(text("""
                            ALTER TABLE score_threshold_subscriptions 
                            ADD COLUMN expires_at DATETIME;
                        """))
                    
                    print("✅ Successfully added expires_at column to score_threshold_subscriptions table")
                else:
                    print("ℹ️  expires_at column already exists in score_threshold_subscriptions table")
                
                # Commit transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Error adding column: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting expires_at column migration...")
    run_migration()
    print("✅ Migration completed successfully!")
