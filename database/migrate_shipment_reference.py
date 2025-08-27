#!/usr/bin/env python3
"""
LogiScore Database Migration Script - Add shipment_reference to reviews table
This script adds the missing shipment_reference column to the reviews table.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ShipmentReferenceMigration:
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
    
    def check_current_reviews_schema(self):
        """Check what columns currently exist in the reviews table"""
        try:
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'reviews' 
                ORDER BY ordinal_position
            """)
            
            columns = self.cursor.fetchall()
            print("Current reviews table columns:")
            for col in columns:
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ''
                print(f"  - {col['column_name']}: {col['data_type']} ({nullable}){default}")
            
            return columns
        except Exception as e:
            print(f"❌ Failed to check schema: {e}")
            return []
    
    def add_shipment_reference_column(self):
        """Add shipment_reference column to reviews table"""
        try:
            print("🔄 Adding shipment_reference column to reviews table...")
            
            # Check if column already exists
            self.cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reviews' AND column_name = 'shipment_reference'
            """)
            
            if self.cursor.fetchone():
                print("  ✅ shipment_reference column already exists")
                return
            
            # Add the shipment_reference column
            self.cursor.execute("""
                ALTER TABLE reviews 
                ADD COLUMN shipment_reference VARCHAR(255) NULL
            """)
            
            print("  ✅ Added shipment_reference column")
            
            # Add an index for better query performance
            try:
                self.cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_reviews_shipment_reference 
                    ON reviews(shipment_reference)
                """)
                print("  ✅ Added index on shipment_reference column")
            except Exception as e:
                print(f"  ⚠️  Could not create index: {e}")
            
            print("✅ shipment_reference column migration completed")
            
        except Exception as e:
            print(f"❌ Failed to add shipment_reference column: {e}")
            raise
    
    def verify_migration(self):
        """Verify that the migration was successful"""
        try:
            print("🔍 Verifying migration...")
            
            # Check if column exists
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'reviews' AND column_name = 'shipment_reference'
            """)
            
            column_info = self.cursor.fetchone()
            if column_info:
                print(f"  ✅ shipment_reference column verified:")
                print(f"     - Data type: {column_info['data_type']}")
                print(f"     - Nullable: {column_info['is_nullable']}")
                return True
            else:
                print("  ❌ shipment_reference column not found")
                return False
                
        except Exception as e:
            print(f"❌ Failed to verify migration: {e}")
            return False
    
    def run_migration(self):
        """Run the complete migration process"""
        try:
            print("🚀 Starting shipment_reference migration...")
            
            # Connect to database
            self.connect()
            
            # Check current schema
            self.check_current_reviews_schema()
            
            # Add shipment_reference column
            self.add_shipment_reference_column()
            
            # Verify migration
            if self.verify_migration():
                print("🎉 Migration completed successfully!")
            else:
                print("❌ Migration verification failed!")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Main function to run the migration"""
    print("=" * 60)
    print("LogiScore Database Migration - Add shipment_reference")
    print("=" * 60)
    
    try:
        migration = ShipmentReferenceMigration()
        success = migration.run_migration()
        
        if success:
            print("\n✅ Migration completed successfully!")
            print("The reviews table now includes the shipment_reference column.")
            print("You can now update the backend models and API to handle this field.")
        else:
            print("\n❌ Migration failed!")
            print("Please check the error messages above and try again.")
            
    except Exception as e:
        print(f"\n❌ Migration script failed to run: {e}")
        print("Please ensure your DATABASE_URL environment variable is set correctly.")

if __name__ == "__main__":
    main()
