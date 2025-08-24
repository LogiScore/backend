#!/usr/bin/env python3
"""
LogiScore Migration: Add city and country fields to reviews table
This script adds city and country fields from branches table to reviews table for easier querying.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CityCountryMigration:
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
    
    def add_city_country_columns(self):
        """Add city and country columns to reviews table"""
        try:
            print("🔄 Adding city and country columns to reviews table...")
            
            # Add new columns
            self.cursor.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS city VARCHAR(100)")
            print("  ✅ Added city column")
            
            self.cursor.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS country VARCHAR(100)")
            print("  ✅ Added country column")
            
            print("✅ City and country columns added successfully")
            
        except Exception as e:
            print(f"❌ Failed to add columns: {e}")
            raise
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            print("🔄 Creating indexes for city and country fields...")
            
            # Create individual indexes
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_city ON reviews(city)")
            print("  ✅ Created index on city")
            
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_country ON reviews(country)")
            print("  ✅ Created index on country")
            
            # Create composite index
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_city_country ON reviews(city, country)")
            print("  ✅ Created composite index on city, country")
            
            print("✅ Indexes created successfully")
            
        except Exception as e:
            print(f"❌ Failed to create indexes: {e}")
            raise
    
    def update_existing_reviews(self):
        """Update existing reviews with city and country data from branches"""
        try:
            print("🔄 Updating existing reviews with city and country data...")
            
            # Update existing reviews with data from branches table
            self.cursor.execute("""
                UPDATE reviews 
                SET 
                    city = branches.city,
                    country = branches.country
                FROM branches 
                WHERE reviews.branch_id = branches.id 
                  AND reviews.city IS NULL 
                  AND reviews.country IS NULL
            """)
            
            updated_count = self.cursor.rowcount
            print(f"  ✅ Updated {updated_count} reviews with city and country data")
            
        except Exception as e:
            print(f"❌ Failed to update existing reviews: {e}")
            raise
    
    def add_column_comments(self):
        """Add comments to document the new fields"""
        try:
            print("🔄 Adding column comments...")
            
            self.cursor.execute("COMMENT ON COLUMN reviews.city IS 'City from the associated branch for easier querying and filtering'")
            self.cursor.execute("COMMENT ON COLUMN reviews.country IS 'Country from the associated branch for easier querying and filtering'")
            
            print("  ✅ Added column comments")
            
        except Exception as e:
            print(f"❌ Failed to add column comments: {e}")
            raise
    
    def verify_migration(self):
        """Verify the migration was successful"""
        try:
            print("🔄 Verifying migration...")
            
            # Check if columns exist
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'reviews' 
                  AND column_name IN ('city', 'country')
                ORDER BY column_name
            """)
            
            columns = self.cursor.fetchall()
            print("  ✅ New columns in reviews table:")
            for col in columns:
                print(f"    - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # Check data population
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_reviews,
                    COUNT(city) as reviews_with_city,
                    COUNT(country) as reviews_with_country
                FROM reviews
            """)
            
            stats = self.cursor.fetchone()
            print(f"  ✅ Migration statistics:")
            print(f"    - Total reviews: {stats['total_reviews']}")
            print(f"    - Reviews with city: {stats['reviews_with_city']}")
            print(f"    - Reviews with country: {stats['reviews_with_country']}")
            
        except Exception as e:
            print(f"❌ Failed to verify migration: {e}")
            raise
    
    def run_migration(self):
        """Run the complete migration"""
        try:
            print("🚀 Starting city and country migration for reviews table...")
            
            self.connect()
            
            # Run migration steps
            self.add_city_country_columns()
            self.create_indexes()
            self.update_existing_reviews()
            self.add_column_comments()
            self.verify_migration()
            
            print("✅ City and country migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            self.disconnect()

if __name__ == "__main__":
    migration = CityCountryMigration()
    migration.run_migration()
