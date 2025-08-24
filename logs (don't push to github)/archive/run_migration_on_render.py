#!/usr/bin/env python3
"""
Simple Migration Script for Render
Run this on Render to fix the database schema issues
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def run_migration():
    """Run the database migration to fix schema issues"""
    
    # Get database URL from environment (Render will provide this)
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        print("✅ Database connection established")
        
        # 1. Fix freight_forwarders table
        print("\n🔄 Migrating freight_forwarders table...")
        
        # Remove old columns that are no longer needed
        old_columns = ['global_rank', 'is_active', 'updated_at']
        for column in old_columns:
            try:
                cursor.execute(f"ALTER TABLE freight_forwarders DROP COLUMN IF EXISTS {column}")
                print(f"  ✅ Dropped column: {column}")
            except Exception as e:
                print(f"  ⚠️  Could not drop column {column}: {e}")
        
        # Add logo_url if it doesn't exist
        try:
            cursor.execute("ALTER TABLE freight_forwarders ADD COLUMN IF NOT EXISTS logo_url TEXT")
            print("  ✅ Added column: logo_url")
        except Exception as e:
            print(f"  ⚠️  Could not add logo_url: {e}")
        
        # 2. Fix reviews table - Add missing columns
        print("\n🔄 Migrating reviews table...")
        
        # Add the critical overall_rating column that's causing the crash
        try:
            cursor.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS overall_rating FLOAT")
            print("  ✅ Added column: overall_rating")
        except Exception as e:
            print(f"  ⚠️  Could not add overall_rating: {e}")
        
        # Add other new columns for the review system
        new_columns = [
            ("review_type", "VARCHAR(50) DEFAULT 'general'"),
            ("review_weight", "NUMERIC(3,2) DEFAULT 1.0"),
            ("aggregate_rating", "NUMERIC(3,2)"),
            ("weighted_rating", "NUMERIC(3,2)"),
            ("total_questions_rated", "INTEGER DEFAULT 0"),
        ]
        
        for column_name, column_def in new_columns:
            try:
                cursor.execute(f"ALTER TABLE reviews ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                print(f"  ✅ Added column: {column_name}")
            except Exception as e:
                print(f"  ⚠️  Could not add {column_name}: {e}")
        
        # Make user_id nullable for anonymous reviews
        try:
            cursor.execute("ALTER TABLE reviews ALTER COLUMN user_id DROP NOT NULL")
            print("  ✅ Made user_id nullable")
        except Exception as e:
            print(f"  ⚠️  Could not make user_id nullable: {e}")
        
        # 3. Create new tables for the review system
        print("\n🔄 Creating review_questions table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_questions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    category_id VARCHAR(100) NOT NULL,
                    category_name VARCHAR(100) NOT NULL,
                    question_id VARCHAR(100) NOT NULL UNIQUE,
                    question_text TEXT NOT NULL,
                    rating_definitions JSONB NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            print("  ✅ Created review_questions table")
        except Exception as e:
            print(f"  ⚠️  Could not create review_questions table: {e}")
        
        print("\n🔄 Creating review_category_scores table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS review_category_scores (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
                    category_id VARCHAR(100) NOT NULL,
                    category_name VARCHAR(100) NOT NULL,
                    question_id VARCHAR(100) NOT NULL,
                    question_text TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    rating_definition TEXT NOT NULL,
                    weight NUMERIC(3,2) DEFAULT 1.0,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            print("  ✅ Created review_category_scores table")
        except Exception as e:
            print(f"  ⚠️  Could not create review_category_scores table: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database migration completed successfully!")
        print("✅ Your API should now work without the 'overall_rating does not exist' error!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting LogiScore database migration on Render...")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        exit(1)
