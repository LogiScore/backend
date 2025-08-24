#!/usr/bin/env python3
"""
Script to remove database constraints from reviews table
This will allow reviews to be created without branch_id constraints
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def get_database_url():
    """Get database URL from environment variable"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    return database_url

def remove_constraints():
    """Remove constraints from reviews table"""
    try:
        # Create database connection
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("🔍 Checking current constraints...")
            
            # 1. Find foreign key constraints on branch_id
            constraint_query = text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'reviews' 
                AND constraint_type = 'FOREIGN KEY' 
                AND constraint_name LIKE '%branch%'
            """)
            
            result = conn.execute(constraint_query)
            constraints = result.fetchall()
            
            if constraints:
                print(f"Found {len(constraints)} foreign key constraints:")
                for constraint in constraints:
                    print(f"  - {constraint[0]}")
                
                # Remove foreign key constraints
                for constraint in constraints:
                    constraint_name = constraint[0]
                    print(f"🗑️  Removing constraint: {constraint_name}")
                    
                    drop_query = text(f"ALTER TABLE reviews DROP CONSTRAINT IF EXISTS {constraint_name}")
                    conn.execute(drop_query)
                    print(f"✅ Removed constraint: {constraint_name}")
            else:
                print("✅ No foreign key constraints found on branch_id")
            
            # 2. Make branch_id nullable
            print("🔧 Making branch_id nullable...")
            alter_query = text("ALTER TABLE reviews ALTER COLUMN branch_id DROP NOT NULL")
            conn.execute(alter_query)
            print("✅ Made branch_id nullable")
            
            # 3. Commit changes
            conn.commit()
            print("💾 Changes committed to database")
            
            # 4. Verify changes
            print("🔍 Verifying changes...")
            verify_query = text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'reviews' 
                AND column_name = 'branch_id'
            """)
            
            result = conn.execute(verify_query)
            column_info = result.fetchone()
            
            if column_info:
                print(f"✅ branch_id column info:")
                print(f"  - Name: {column_info[0]}")
                print(f"  - Type: {column_info[1]}")
                print(f"  - Nullable: {column_info[2]}")
                print(f"  - Default: {column_info[3]}")
            else:
                print("❌ Could not verify branch_id column")
            
            # 5. Check remaining constraints
            print("🔍 Checking remaining constraints...")
            remaining_query = text("""
                SELECT 
                    constraint_name, 
                    constraint_type, 
                    column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu 
                ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_name = 'reviews'
            """)
            
            result = conn.execute(remaining_query)
            remaining_constraints = result.fetchall()
            
            if remaining_constraints:
                print(f"Remaining constraints: {len(remaining_constraints)}")
                for constraint in remaining_constraints:
                    print(f"  - {constraint[0]} ({constraint[1]}) on {constraint[2]}")
            else:
                print("✅ No constraints remaining")
                
        print("\n🎉 Database constraints removed successfully!")
        print("Reviews can now be created without branch_id constraints.")
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting database constraint removal...")
    remove_constraints()
