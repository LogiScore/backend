#!/usr/bin/env python3
"""
Migration script to add shipment_reference column to reviews table in production
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def migrate_shipment_reference():
    """Add shipment_reference column to reviews table"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if column already exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reviews' 
                AND column_name = 'shipment_reference'
            """)
            
            result = conn.execute(check_column_query).fetchone()
            
            if result:
                print("✅ shipment_reference column already exists")
                return True
            
            # Add the column
            print("🔄 Adding shipment_reference column to reviews table...")
            alter_query = text("""
                ALTER TABLE reviews 
                ADD COLUMN shipment_reference VARCHAR(255)
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            print("✅ Successfully added shipment_reference column to reviews table")
            return True
            
    except OperationalError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting shipment_reference migration...")
    success = migrate_shipment_reference()
    
    if success:
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print("❌ Migration failed")
        sys.exit(1)
