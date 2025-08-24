#!/usr/bin/env python3
"""
Simple script to run the locations migration
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from migrate_locations_to_db import main
    print("🚀 Starting locations migration...")
    main()
    print("\n✅ Migration completed successfully!")
    print("Your locations API now uses the database with UUIDs!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install pandas sqlalchemy psycopg2-binary python-dotenv")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    print("Check your database connection and environment variables")
    sys.exit(1)
