#!/usr/bin/env python3
"""
Migration script to add shipment_reference column to reviews table in production
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from database.database import get_db
from sqlalchemy import text

def migrate_shipment_reference():
    """Add shipment_reference column to reviews table"""
    
    try:
        # Get database session using existing connection
        db = next(get_db())
        
        try:
            # Check if column already exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reviews' 
                AND column_name = 'shipment_reference'
            """)
            
            result = db.execute(check_column_query).fetchone()
            
            if result:
                print("✅ shipment_reference column already exists")
                return True
            
            # Add the column
            print("🔄 Adding shipment_reference column to reviews table...")
            alter_query = text("""
                ALTER TABLE reviews 
                ADD COLUMN shipment_reference VARCHAR(255)
            """)
            
            db.execute(alter_query)
            db.commit()
            
            print("✅ Successfully added shipment_reference column to reviews table")
            return True
            
        finally:
            db.close()
            
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
