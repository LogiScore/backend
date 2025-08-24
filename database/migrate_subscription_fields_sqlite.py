"""
SQLite Migration script to add subscription fields to users table
Run this script to update your local SQLite database schema
"""

import sqlite3
import os
import sys

def migrate_subscription_fields_sqlite():
    """Add subscription fields to users table in SQLite"""
    try:
        # Connect to SQLite database
        db_path = "../test.db"
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            sys.exit(1)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting SQLite subscription fields migration...")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Existing columns: {existing_columns}")
        
        # Add missing fields
        fields_to_add = [
            ('subscription_start_date', 'TIMESTAMP'),
            ('subscription_end_date', 'TIMESTAMP'),
            ('auto_renew_enabled', 'BOOLEAN DEFAULT 0'),
            ('payment_method_id', 'VARCHAR(255)'),
            ('stripe_subscription_id', 'VARCHAR(255)'),
            ('last_billing_date', 'TIMESTAMP'),
            ('next_billing_date', 'TIMESTAMP'),
            ('subscription_status', 'VARCHAR(20) DEFAULT \'active\'')
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"
                    cursor.execute(sql)
                    print(f"✓ Added column: {field_name}")
                except Exception as e:
                    print(f"⚠ Warning adding {field_name}: {str(e)}")
            else:
                print(f"✓ Column already exists: {field_name}")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        # Verify migration
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
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
        
        # Show final table structure
        print("\nFinal table structure:")
        cursor.execute("PRAGMA table_info(users)")
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]}) - Default: {row[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    migrate_subscription_fields_sqlite()
