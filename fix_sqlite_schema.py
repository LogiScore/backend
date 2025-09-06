#!/usr/bin/env python3
"""
Fix SQLite schema by adding missing shipment_reference column
"""
import sqlite3
import os

def fix_sqlite_schema():
    """Add shipment_reference column to SQLite database"""
    
    # Use the same database path as the app
    db_path = "test.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(reviews)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'shipment_reference' in columns:
            print("✅ shipment_reference column already exists")
            return True
        
        # Add the column
        print("🔄 Adding shipment_reference column to reviews table...")
        cursor.execute("ALTER TABLE reviews ADD COLUMN shipment_reference VARCHAR(255)")
        conn.commit()
        
        print("✅ Successfully added shipment_reference column to reviews table")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Fixing SQLite schema...")
    success = fix_sqlite_schema()
    
    if success:
        print("✅ Schema fix completed successfully")
    else:
        print("❌ Schema fix failed")
