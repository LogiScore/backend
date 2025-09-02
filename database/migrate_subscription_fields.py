#!/usr/bin/env python3
"""
Migration script to add subscription expiration fields to users table.
This enables subscription expiration tracking and automatic tier reversion.
"""

import sqlite3
import os
from datetime import datetime

def migrate_subscription_fields():
    """Add subscription expiration fields to users table"""
    
    # Database path
    db_path = "test.db"  # Update this to your actual database path
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting subscription fields migration...")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        fields_to_add = [
            ("subscription_start_date", "DATETIME"),
            ("subscription_end_date", "DATETIME"),
            ("auto_renew_enabled", "BOOLEAN DEFAULT 0"),
            ("payment_method_id", "VARCHAR(255)"),
            ("stripe_subscription_id", "VARCHAR(255)"),
            ("last_billing_date", "DATETIME"),
            ("next_billing_date", "DATETIME"),
            ("subscription_status", "VARCHAR(20) DEFAULT 'active'")
        ]
        
        added_fields = []
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                    added_fields.append(field_name)
                    print(f"✓ Added column: {field_name}")
                except Exception as e:
                    print(f"✗ Failed to add {field_name}: {e}")
            else:
                print(f"- Column already exists: {field_name}")
        
        # Commit changes
        conn.commit()
        
        if added_fields:
            print(f"\nMigration completed successfully!")
            print(f"Added {len(added_fields)} new fields: {', '.join(added_fields)}")
        else:
            print("\nNo new fields were added - all fields already exist.")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

def safe_migrate_essential_fields():
    """Safely migrate essential subscription fields for PostgreSQL"""
    try:
        from database.database import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("Starting PostgreSQL subscription fields migration...")
                
                # Check if fields already exist
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                """))
                existing_columns = [row[0] for row in result.fetchall()]
                
                # Fields to add with PostgreSQL syntax
                fields_to_add = [
                    ("subscription_start_date", "TIMESTAMP WITH TIME ZONE"),
                    ("subscription_end_date", "TIMESTAMP WITH TIME ZONE"),
                    ("auto_renew_enabled", "BOOLEAN DEFAULT FALSE"),
                    ("payment_method_id", "VARCHAR(255)"),
                    ("stripe_subscription_id", "VARCHAR(255)"),
                    ("last_billing_date", "TIMESTAMP WITH TIME ZONE"),
                    ("next_billing_date", "TIMESTAMP WITH TIME ZONE"),
                    ("subscription_status", "VARCHAR(20) DEFAULT 'active'")
                ]
                
                added_fields = []
                for field_name, field_type in fields_to_add:
                    if field_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                            conn.execute(text(sql))
                            added_fields.append(field_name)
                            print(f"✓ Added column: {field_name}")
                        except Exception as e:
                            print(f"✗ Failed to add {field_name}: {e}")
                    else:
                        print(f"- Column already exists: {field_name}")
                
                # Commit transaction
                trans.commit()
                
                if added_fields:
                    print(f"\nMigration completed successfully!")
                    print(f"Added {len(added_fields)} new fields: {', '.join(added_fields)}")
                else:
                    print("\nNo new fields were added - all fields already exist.")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

def remove_username_unique_constraint():
    """Remove unique constraint on username column"""
    try:
        from database.database import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Check if unique constraint exists
                result = conn.execute(text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'users' 
                    AND constraint_type = 'UNIQUE' 
                    AND constraint_name LIKE '%username%'
                """))
                
                constraints = [row[0] for row in result.fetchall()]
                
                for constraint_name in constraints:
                    try:
                        sql = f"ALTER TABLE users DROP CONSTRAINT {constraint_name}"
                        conn.execute(text(sql))
                        print(f"✓ Removed constraint: {constraint_name}")
                    except Exception as e:
                        print(f"✗ Failed to remove constraint {constraint_name}: {e}")
                
                trans.commit()
                print("Username constraint removal completed")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"Constraint removal failed: {e}")
                return False
                
    except Exception as e:
        print(f"Constraint removal failed: {e}")
        return False

if __name__ == "__main__":
    migrate_subscription_fields()
