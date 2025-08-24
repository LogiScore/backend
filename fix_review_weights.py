#!/usr/bin/env python3
"""
Fix script for missing or invalid review_weight values
This will update reviews that have NULL or 0 review_weight to have proper values
"""

import os
import sys
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.models import Review

def fix_review_weights():
    """Fix missing or invalid review_weight values"""
    
    print("🔧 Fixing Review Weight Values")
    print("=" * 40)
    
    try:
        # Get database session
        db = next(get_db())
        
        # Check current state
        print("📊 Checking current review_weight values...")
        
        total_reviews = db.query(Review).count()
        null_weights = db.query(Review).filter(Review.review_weight.is_(None)).count()
        zero_weights = db.query(Review).filter(Review.review_weight == 0).count()
        
        print(f"   Total reviews: {total_reviews}")
        print(f"   Reviews with NULL review_weight: {null_weights}")
        print(f"   Reviews with review_weight = 0: {zero_weights}")
        
        if null_weights == 0 and zero_weights == 0:
            print("✅ All reviews already have valid review_weight values!")
            return
        
        # Fix NULL review_weight values (set to 1.0 as default)
        if null_weights > 0:
            print(f"\n🔧 Fixing {null_weights} reviews with NULL review_weight...")
            
            # Update NULL values to 1.0 (assuming they are authenticated reviews)
            updated = db.execute(text("""
                UPDATE reviews 
                SET review_weight = 1.0 
                WHERE review_weight IS NULL
            """))
            
            print(f"   ✅ Updated {updated.rowcount} reviews")
        
        # Fix zero review_weight values
        if zero_weights > 0:
            print(f"\n🔧 Fixing {zero_weights} reviews with review_weight = 0...")
            
            # Update zero values to 1.0
            updated = db.execute(text("""
                UPDATE reviews 
                SET review_weight = 1.0 
                WHERE review_weight = 0
            """))
            
            print(f"   ✅ Updated {updated.rowcount} reviews")
        
        # Commit changes
        db.commit()
        print("\n✅ All review_weight values have been fixed!")
        
        # Verify the fix
        print("\n🔍 Verifying the fix...")
        null_weights_after = db.query(Review).filter(Review.review_weight.is_(None)).count()
        zero_weights_after = db.query(Review).filter(Review.review_weight == 0).count()
        
        print(f"   Reviews with NULL review_weight: {null_weights_after}")
        print(f"   Reviews with review_weight = 0: {zero_weights_after}")
        
        if null_weights_after == 0 and zero_weights_after == 0:
            print("✅ Verification successful! All reviews now have valid review_weight values.")
        else:
            print("⚠️  Some reviews still have invalid review_weight values.")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

def set_anonymous_review_weights():
    """Set review_weight to 0.5 for anonymous reviews"""
    
    print("\n🔧 Setting Anonymous Review Weights")
    print("=" * 40)
    
    try:
        db = next(get_db())
        
        # Find anonymous reviews
        anonymous_reviews = db.query(Review).filter(Review.is_anonymous == True).count()
        print(f"📊 Found {anonymous_reviews} anonymous reviews")
        
        if anonymous_reviews > 0:
            # Update anonymous reviews to have weight 0.5
            updated = db.execute(text("""
                UPDATE reviews 
                SET review_weight = 0.5 
                WHERE is_anonymous = true
            """))
            
            print(f"   ✅ Updated {updated.rowcount} anonymous reviews to weight 0.5")
            db.commit()
        else:
            print("   ℹ️  No anonymous reviews found")
        
    except Exception as e:
        print(f"❌ Error setting anonymous weights: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🚀 LogiScore Review Weight Fix Script")
    print("This script will fix missing or invalid review_weight values")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed with fixing review weights? (y/N): ")
    if response.lower() in ['y', 'yes']:
        fix_review_weights()
        set_anonymous_review_weights()
        print("\n🎉 Review weight fix completed!")
    else:
        print("❌ Operation cancelled by user")
