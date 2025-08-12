#!/usr/bin/env python3
"""
LogiScore Database Migration Script
This script migrates the existing database schema to match the new models.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseMigration:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.conn.autocommit = True  # Enable autocommit for DDL operations
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ Database connection closed")
    
    def check_current_schema(self):
        """Check what columns currently exist in the freight_forwarders table"""
        try:
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'freight_forwarders' 
                ORDER BY ordinal_position
            """)
            
            columns = self.cursor.fetchall()
            print("Current freight_forwarders table columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            return columns
        except Exception as e:
            print(f"❌ Failed to check schema: {e}")
            return []
    
    def migrate_freight_forwarders_table(self):
        """Migrate freight_forwarders table to new schema"""
        try:
            print("🔄 Migrating freight_forwarders table...")
            
            # Remove old columns that no longer exist in the new model
            old_columns = ['description', 'headquarters_country', 'global_rank', 'is_active', 'updated_at']
            
            for column in old_columns:
                try:
                    self.cursor.execute(f"ALTER TABLE freight_forwarders DROP COLUMN IF EXISTS {column}")
                    print(f"  ✅ Dropped column: {column}")
                except Exception as e:
                    print(f"  ⚠️  Could not drop column {column}: {e}")
            
            # Add new columns if they don't exist
            new_columns = [
                ("logo_url", "TEXT"),
            ]
            
            for column_name, data_type in new_columns:
                try:
                    self.cursor.execute(f"ALTER TABLE freight_forwarders ADD COLUMN IF NOT EXISTS {column_name} {data_type}")
                    print(f"  ✅ Added column: {column_name}")
                except Exception as e:
                    print(f"  ⚠️  Could not add column {column_name}: {e}")
            
            print("✅ Freight forwarders table migration completed")
            
        except Exception as e:
            print(f"❌ Failed to migrate freight_forwarders table: {e}")
            raise
    
    def migrate_reviews_table(self):
        """Migrate reviews table to new schema"""
        try:
            print("🔄 Migrating reviews table...")
            
            # Add new columns for the comprehensive review system
            new_columns = [
                ("review_type", "VARCHAR(50) DEFAULT 'general'"),
                ("review_weight", "NUMERIC(3,2) DEFAULT 1.0"),
                ("aggregate_rating", "NUMERIC(3,2)"),
                ("weighted_rating", "NUMERIC(3,2)"),
                ("total_questions_rated", "INTEGER DEFAULT 0"),
            ]
            
            for column_name, column_def in new_columns:
                try:
                    self.cursor.execute(f"ALTER TABLE reviews ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                    print(f"  ✅ Added column: {column_name}")
                except Exception as e:
                    print(f"  ⚠️  Could not add column {column_name}: {e}")
            
            # Make user_id nullable for anonymous reviews
            try:
                self.cursor.execute("ALTER TABLE reviews ALTER COLUMN user_id DROP NOT NULL")
                print("  ✅ Made user_id nullable")
            except Exception as e:
                print(f"  ⚠️  Could not make user_id nullable: {e}")
            
            # Make overall_rating nullable (will be calculated from new system)
            try:
                self.cursor.execute("ALTER TABLE reviews ALTER COLUMN overall_rating DROP NOT NULL")
                print("  ✅ Made overall_rating nullable")
            except Exception as e:
                print(f"  ⚠️  Could not make overall_rating nullable: {e}")
            
            print("✅ Reviews table migration completed")
            
        except Exception as e:
            print(f"❌ Failed to migrate reviews table: {e}")
            raise
    
    def create_review_questions_table(self):
        """Create the new review_questions table"""
        try:
            print("🔄 Creating review_questions table...")
            
            self.cursor.execute("""
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
            
            # Add indexes
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_questions_category_id ON review_questions(category_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_questions_question_id ON review_questions(question_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_questions_active ON review_questions(is_active)")
            
            print("✅ Review questions table created")
            
        except Exception as e:
            print(f"❌ Failed to create review_questions table: {e}")
            raise
    
    def create_review_category_scores_table(self):
        """Create the new review_category_scores table"""
        try:
            print("🔄 Creating review_category_scores table...")
            
            self.cursor.execute("""
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
            
            # Add indexes
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_category_scores_review_id ON review_category_scores(review_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_category_scores_category_id ON review_category_scores(category_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_category_scores_question_id ON review_category_scores(question_id)")
            
            print("✅ Review category scores table created")
            
        except Exception as e:
            print(f"❌ Failed to create review_category_scores table: {e}")
            raise
    
    def run_migration(self):
        """Run the complete migration"""
        try:
            print("🚀 Starting LogiScore database migration...")
            
            self.connect()
            
            # Check current schema
            self.check_current_schema()
            
            # Run migrations
            self.migrate_freight_forwarders_table()
            self.migrate_reviews_table()
            self.create_review_questions_table()
            self.create_review_category_scores_table()
            
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            self.disconnect()

if __name__ == "__main__":
    migration = DatabaseMigration()
    migration.run_migration()
