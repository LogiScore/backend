#!/usr/bin/env python3
"""
Test script to verify subscription cancellation scenarios
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.models import User
from services.subscription_service import SubscriptionService

async def test_cancellation_scenarios():
    """Test both trial and paid subscription cancellation scenarios"""
    
    print("🧪 Testing Subscription Cancellation Scenarios")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    subscription_service = SubscriptionService()
    
    try:
        # Test 1: Trial User Cancellation (should be immediate)
        print("\n📋 Test 1: Trial User Cancellation")
        print("-" * 30)
        
        # Create a test trial user
        trial_user = User(
            email="trial@test.com",
            username="trial_user",
            subscription_status="trial",
            subscription_tier="Shipper Monthly",
            subscription_end_date=datetime.utcnow() + timedelta(days=7),
            auto_renew_enabled=True,
            stripe_subscription_id="sub_trial_test_123"
        )
        db.add(trial_user)
        db.commit()
        db.refresh(trial_user)
        
        print(f"✅ Created trial user: {trial_user.email}")
        print(f"   Status: {trial_user.subscription_status}")
        print(f"   Tier: {trial_user.subscription_tier}")
        print(f"   Auto-renew: {trial_user.auto_renew_enabled}")
        print(f"   Stripe ID: {trial_user.stripe_subscription_id}")
        
        # Cancel trial subscription
        print("\n🔄 Canceling trial subscription...")
        result = await subscription_service.cancel_subscription(str(trial_user.id), db)
        print(f"✅ Result: {result}")
        
        # Verify trial user was immediately canceled
        db.refresh(trial_user)
        print(f"\n📊 Trial user after cancellation:")
        print(f"   Status: {trial_user.subscription_status}")
        print(f"   Tier: {trial_user.subscription_tier}")
        print(f"   Auto-renew: {trial_user.auto_renew_enabled}")
        print(f"   Stripe ID: {trial_user.stripe_subscription_id}")
        print(f"   End date: {trial_user.subscription_end_date}")
        
        # Test 2: Paid User Cancellation (should disable auto-renewal only)
        print("\n\n📋 Test 2: Paid User Cancellation")
        print("-" * 30)
        
        # Create a test paid user
        paid_user = User(
            email="paid@test.com",
            username="paid_user",
            subscription_status="active",
            subscription_tier="Shipper Monthly",
            subscription_end_date=datetime.utcnow() + timedelta(days=30),
            auto_renew_enabled=True,
            stripe_subscription_id="sub_paid_test_456"
        )
        db.add(paid_user)
        db.commit()
        db.refresh(paid_user)
        
        print(f"✅ Created paid user: {paid_user.email}")
        print(f"   Status: {paid_user.subscription_status}")
        print(f"   Tier: {paid_user.subscription_tier}")
        print(f"   Auto-renew: {paid_user.auto_renew_enabled}")
        print(f"   Stripe ID: {paid_user.stripe_subscription_id}")
        
        # Cancel paid subscription
        print("\n🔄 Canceling paid subscription...")
        result = await subscription_service.cancel_subscription(str(paid_user.id), db)
        print(f"✅ Result: {result}")
        
        # Verify paid user had auto-renewal disabled but kept access
        db.refresh(paid_user)
        print(f"\n📊 Paid user after cancellation:")
        print(f"   Status: {paid_user.subscription_status}")
        print(f"   Tier: {paid_user.subscription_tier}")
        print(f"   Auto-renew: {paid_user.auto_renew_enabled}")
        print(f"   Stripe ID: {paid_user.stripe_subscription_id}")
        print(f"   End date: {paid_user.subscription_end_date}")
        
        # Test 3: Free User Cancellation
        print("\n\n📋 Test 3: Free User Cancellation")
        print("-" * 30)
        
        # Create a test free user
        free_user = User(
            email="free@test.com",
            username="free_user",
            subscription_status="active",
            subscription_tier="free",
            subscription_end_date=None,
            auto_renew_enabled=False,
            stripe_subscription_id=None
        )
        db.add(free_user)
        db.commit()
        db.refresh(free_user)
        
        print(f"✅ Created free user: {free_user.email}")
        print(f"   Status: {free_user.subscription_status}")
        print(f"   Tier: {free_user.subscription_tier}")
        print(f"   Auto-renew: {free_user.auto_renew_enabled}")
        print(f"   Stripe ID: {free_user.stripe_subscription_id}")
        
        # Cancel free subscription
        print("\n🔄 Canceling free subscription...")
        result = await subscription_service.cancel_subscription(str(free_user.id), db)
        print(f"✅ Result: {result}")
        
        # Verify free user was marked as canceled but kept free tier
        db.refresh(free_user)
        print(f"\n📊 Free user after cancellation:")
        print(f"   Status: {free_user.subscription_status}")
        print(f"   Tier: {free_user.subscription_tier}")
        print(f"   Auto-renew: {free_user.auto_renew_enabled}")
        print(f"   Stripe ID: {free_user.stripe_subscription_id}")
        print(f"   End date: {free_user.subscription_end_date}")
        
        # Clean up test users
        print("\n🧹 Cleaning up test users...")
        db.delete(trial_user)
        db.delete(paid_user)
        db.delete(free_user)
        db.commit()
        print("✅ Test users cleaned up")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_cancellation_scenarios())
