#!/usr/bin/env python3
"""
Script to fix user type issues in the LogiScore database.
This script allows admins to update a user's type from 'shipper' to 'forwarder'.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

def get_db_session():
    """Create database session"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return None

def check_user_type(email):
    """Check current user type"""
    db = get_db_session()
    if not db:
        return None
    
    try:
        from database.models import User
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if user:
            return {
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type,
                "username": user.username,
                "company_name": user.company_name
            }
        return None
    except Exception as e:
        print(f"Error checking user: {e}")
        return None
    finally:
        db.close()

def update_user_type(email, new_user_type):
    """Update user type"""
    if new_user_type not in ["shipper", "forwarder", "admin"]:
        print(f"Invalid user type: {new_user_type}")
        return False
    
    db = get_db_session()
    if not db:
        return False
    
    try:
        from database.models import User
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            print(f"User with email {email} not found")
            return False
        
        old_type = user.user_type
        user.user_type = new_user_type
        db.commit()
        
        print(f"Successfully updated user {email} from '{old_type}' to '{new_user_type}'")
        return True
        
    except Exception as e:
        print(f"Error updating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("LogiScore User Type Fix Script")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage: python fix_user_type.py <email> [new_user_type]")
        print("Example: python fix_user_type.py user@example.com forwarder")
        print("\nIf no new_user_type is provided, will just show current user info")
        return
    
    email = sys.argv[1]
    new_user_type = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Checking user: {email}")
    
    # Check current user info
    user_info = check_user_type(email)
    if not user_info:
        print(f"User not found: {email}")
        return
    
    print(f"\nCurrent user info:")
    print(f"  ID: {user_info['id']}")
    print(f"  Email: {user_info['email']}")
    print(f"  Username: {user_info['username']}")
    print(f"  Company: {user_info['company_name']}")
    print(f"  Current Type: {user_info['user_type']}")
    
    if new_user_type:
        if user_info['user_type'] == new_user_type:
            print(f"\nUser is already '{new_user_type}' - no change needed")
            return
        
        print(f"\nUpdating user type from '{user_info['user_type']}' to '{new_user_type}'...")
        
        if update_user_type(email, new_user_type):
            print("✅ User type updated successfully!")
            
            # Verify the change
            updated_info = check_user_type(email)
            if updated_info:
                print(f"✅ Verified: User type is now '{updated_info['user_type']}'")
        else:
            print("❌ Failed to update user type")
    else:
        print(f"\nTo change user type, run:")
        print(f"python fix_user_type.py {email} forwarder")

if __name__ == "__main__":
    main()
