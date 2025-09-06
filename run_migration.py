#!/usr/bin/env python3
"""
Run the shipment_reference migration on production
"""
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

from database.migrate_shipment_reference_production import migrate_shipment_reference

if __name__ == "__main__":
    print("🚀 Running shipment_reference migration on production...")
    success = migrate_shipment_reference()
    
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")
        sys.exit(1)
