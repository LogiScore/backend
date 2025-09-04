#!/usr/bin/env python3
"""
Remove Branches Table Migration Script
This script removes the branches table and related data from the Supabase database.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def remove_branches_table():
    """Remove the branches table from the database"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    conn = None
    cursor = None
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Connected to database")
        
        # Check if branches table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'branches'
            );
        """)
        
        table_exists = cursor.fetchone()['exists']
        
        if not table_exists:
            print("ℹ️ Branches table does not exist - nothing to remove")
            return
        
        print("🔍 Branches table found - proceeding with removal...")
        
        # Drop foreign key constraints first (if any exist)
        cursor.execute("""
            SELECT constraint_name, table_name
            FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND (table_name = 'branches' OR constraint_name LIKE '%branch%')
        """)
        
        constraints = cursor.fetchall()
        for constraint in constraints:
            try:
                cursor.execute(f"ALTER TABLE {constraint['table_name']} DROP CONSTRAINT IF EXISTS {constraint['constraint_name']}")
                print(f"✅ Dropped constraint: {constraint['constraint_name']}")
            except Exception as e:
                print(f"⚠️ Could not drop constraint {constraint['constraint_name']}: {e}")
        
        # Drop indexes on branches table
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'branches'
        """)
        
        indexes = cursor.fetchall()
        for index in indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index['indexname']}")
                print(f"✅ Dropped index: {index['indexname']}")
            except Exception as e:
                print(f"⚠️ Could not drop index {index['indexname']}: {e}")
        
        # Drop the branches table
        cursor.execute("DROP TABLE IF EXISTS branches CASCADE")
        print("✅ Dropped branches table")
        
        # Commit changes
        conn.commit()
        print("✅ Successfully removed branches table and related objects")
        
        # Verify removal
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'branches'
            );
        """)
        
        table_still_exists = cursor.fetchone()['exists']
        
        if not table_still_exists:
            print("✅ Verification: Branches table successfully removed")
        else:
            print("❌ Verification failed: Branches table still exists")
            
    except Exception as e:
        print(f"❌ Error removing branches table: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("✅ Database connection closed")

if __name__ == "__main__":
    print("🚀 Starting branches table removal...")
    remove_branches_table()
    print("🎉 Branches table removal completed!")
