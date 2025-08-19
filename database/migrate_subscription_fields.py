"""
Migration script to add subscription fields to users table
Run this script to update your database schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    # Check for Render environment
    if os.getenv('RENDER'):
        return os.getenv('DATABASE_URL')
    
    # Check for local environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to local SQLite
        database_url = "sqlite:///./test.db"
    
    return database_url

def migrate_subscription_fields():
    """Add subscription fields to users table"""
    try:
        # Create database connection
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("Starting subscription fields migration...")
        
        # Check if fields already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN (
                'subscription_start_date', 
                'subscription_end_date', 
                'auto_renew_enabled', 
                'payment_method_id', 
                'stripe_subscription_id', 
                'last_billing_date', 
                'next_billing_date', 
                'subscription_status'
            )
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        
        # Add missing fields
        fields_to_add = [
            ('subscription_start_date', 'TIMESTAMP'),
            ('subscription_end_date', 'TIMESTAMP'),
            ('auto_renew_enabled', 'BOOLEAN DEFAULT FALSE'),
            ('payment_method_id', 'VARCHAR(255)'),
            ('stripe_subscription_id', 'VARCHAR(255)'),
            ('last_billing_date', 'TIMESTAMP'),
            ('next_billing_date', 'TIMESTAMP'),
            ('subscription_status', 'VARCHAR(20) DEFAULT \'active\'')
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                try:
                    if 'postgresql' in database_url.lower():
                        # PostgreSQL syntax
                        sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                    else:
                        # SQLite syntax
                        sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                    
                    db.execute(text(sql))
                    print(f"✓ Added column: {field_name}")
                except Exception as e:
                    print(f"⚠ Warning adding {field_name}: {str(e)}")
            else:
                print(f"✓ Column already exists: {field_name}")
        
        # Create indexes for performance
        indexes_to_create = [
            ('idx_subscription_end_date', 'subscription_end_date'),
            ('idx_subscription_status', 'subscription_status'),
            ('idx_stripe_customer_id', 'stripe_customer_id')
        ]
        
        for index_name, column_name in indexes_to_create:
            try:
                # Check if index already exists
                if 'postgresql' in database_url.lower():
                    result = db.execute(text(f"""
                        SELECT indexname FROM pg_indexes 
                        WHERE tablename = 'users' AND indexname = '{index_name}'
                    """))
                else:
                    # SQLite doesn't support checking existing indexes easily
                    result = None
                
                if not result or not result.fetchone():
                    if 'postgresql' in database_url.lower():
                        sql = f"CREATE INDEX {index_name} ON users({column_name})"
                    else:
                        sql = f"CREATE INDEX {index_name} ON users({column_name})"
                    
                    db.execute(text(sql))
                    print(f"✓ Created index: {index_name}")
                else:
                    print(f"✓ Index already exists: {index_name}")
            except Exception as e:
                print(f"⚠ Warning creating index {index_name}: {str(e)}")
        
        # Commit changes
        db.commit()
        print("✓ Migration completed successfully!")
        
        # Verify migration
        print("\nVerifying migration...")
        result = db.execute(text("SELECT * FROM users LIMIT 1"))
        columns = result.keys()
        
        subscription_columns = [
            'subscription_start_date', 'subscription_end_date', 'auto_renew_enabled',
            'payment_method_id', 'stripe_subscription_id', 'last_billing_date',
            'next_billing_date', 'subscription_status'
        ]
        
        for col in subscription_columns:
            if col in columns:
                print(f"✓ {col}: Present")
            else:
                print(f"✗ {col}: Missing")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        sys.exit(1)

def safe_migrate_essential_fields():
    """Add only essential subscription fields needed for auth to work"""
    try:
        # Create database connection
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("Starting essential fields migration...")
        
        # Only add the essential fields that the auth endpoint needs
        essential_fields = [
            ('subscription_start_date', 'TIMESTAMP'),
            ('subscription_end_date', 'TIMESTAMP'),
            ('auto_renew_enabled', 'BOOLEAN DEFAULT FALSE'),
            ('payment_method_id', 'VARCHAR(255)'),
            ('stripe_subscription_id', 'VARCHAR(255)'),
            ('last_billing_date', 'TIMESTAMP'),
            ('next_billing_date', 'TIMESTAMP'),
            ('subscription_status', 'VARCHAR(20) DEFAULT \'active\'')
        ]
        
        for field_name, field_type in essential_fields:
            try:
                # Check if column exists
                result = db.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = '{field_name}'
                """))
                
                if not result.fetchone():
                    # Add column safely
                    if 'postgresql' in database_url.lower():
                        sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                    else:
                        sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                    
                    db.execute(text(sql))
                    print(f"✓ Added essential column: {field_name}")
                else:
                    print(f"✓ Essential column already exists: {field_name}")
                    
            except Exception as e:
                print(f"⚠ Error adding {field_name}: {str(e)}")
                # Continue with other fields
        
        db.commit()
        print("✓ Essential fields migration completed")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("Running full subscription fields migration...")
    migrate_subscription_fields()
    print("\nRunning essential fields migration...")
    safe_migrate_essential_fields()
