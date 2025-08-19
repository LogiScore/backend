#!/usr/bin/env python3
"""
Stripe Setup Verification Script for LogiScore
Run this script to verify your Stripe configuration is correct
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if all required environment variables are set"""
    required_vars = [
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_WEBHOOK_SECRET',
        'STRIPE_SHIPPER_MONTHLY_PRICE_ID',
        'STRIPE_SHIPPER_ANNUAL_PRICE_ID',
        'STRIPE_FORWARDER_MONTHLY_PRICE_ID',
        'STRIPE_FORWARDER_ANNUAL_PRICE_ID',
        'STRIPE_FORWARDER_ANNUAL_PLUS_PRICE_ID'
    ]
    
    print("🔍 Checking environment variables...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        elif var.endswith('_KEY') and not value.startswith(('sk_test_', 'pk_test_', 'sk_live_', 'pk_live_')):
            print(f"⚠️  {var}: Invalid format (should start with sk_test_, pk_test_, etc.)")
        elif var.endswith('_PRICE_ID') and not value.startswith('price_'):
            print(f"⚠️  {var}: Invalid format (should start with price_)")
        elif var == 'STRIPE_WEBHOOK_SECRET' and not value.startswith('whsec_'):
            print(f"⚠️  {var}: Invalid format (should start with whsec_)")
        else:
            print(f"✅ {var}: Configured")
    
    if missing_vars:
        print(f"\n❌ Missing {len(missing_vars)} required environment variables")
        print("Please set these in your .env file:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    else:
        print("✅ All environment variables configured!")
        return True

def test_stripe_connection():
    """Test connection to Stripe API"""
    try:
        import stripe
        
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        print("\n🔗 Testing Stripe API connection...")
        
        # Test API connection by listing products
        products = stripe.Product.list(limit=1)
        print("✅ Stripe API connection successful!")
        
        return True
        
    except ImportError:
        print("❌ Stripe library not installed. Run: pip install stripe")
        return False
    except stripe.error.AuthenticationError:
        print("❌ Invalid Stripe API key")
        return False
    except Exception as e:
        print(f"❌ Stripe API error: {str(e)}")
        return False

def verify_price_ids():
    """Verify that all price IDs exist in Stripe"""
    try:
        import stripe
        
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        print("\n💰 Verifying Stripe price IDs...")
        
        price_ids = {
            'Shipper Monthly': os.getenv('STRIPE_SHIPPER_MONTHLY_PRICE_ID'),
            'Shipper Annual': os.getenv('STRIPE_SHIPPER_ANNUAL_PRICE_ID'),
            'Forwarder Monthly': os.getenv('STRIPE_FORWARDER_MONTHLY_PRICE_ID'),
            'Forwarder Annual': os.getenv('STRIPE_FORWARDER_ANNUAL_PRICE_ID'),
            'Forwarder Annual Plus': os.getenv('STRIPE_FORWARDER_ANNUAL_PLUS_PRICE_ID')
        }
        
        valid_prices = 0
        for plan_name, price_id in price_ids.items():
            if not price_id:
                print(f"⚠️  {plan_name}: No price ID configured")
                continue
                
            try:
                price = stripe.Price.retrieve(price_id)
                product = stripe.Product.retrieve(price.product)
                print(f"✅ {plan_name}: {product.name} - ${price.unit_amount/100:.2f}/{price.recurring.interval}")
                valid_prices += 1
            except stripe.error.InvalidRequestError:
                print(f"❌ {plan_name}: Price ID '{price_id}' not found in Stripe")
            except Exception as e:
                print(f"❌ {plan_name}: Error retrieving price - {str(e)}")
        
        if valid_prices == len([p for p in price_ids.values() if p]):
            print("✅ All configured price IDs are valid!")
            return True
        else:
            print(f"⚠️  Only {valid_prices} out of {len([p for p in price_ids.values() if p])} price IDs are valid")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying price IDs: {str(e)}")
        return False

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    try:
        import requests
        
        print("\n🔗 Testing webhook endpoint...")
        
        # Test local development endpoint
        try:
            response = requests.get('http://localhost:8000/api/webhooks/stripe/webhook/test', timeout=5)
            if response.status_code == 200:
                print("✅ Webhook test endpoint accessible")
                return True
            else:
                print(f"⚠️  Webhook endpoint returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️  Webhook endpoint not accessible (server may not be running)")
            print("   Start the server with: python3 main.py")
            return False
        except Exception as e:
            print(f"❌ Error testing webhook endpoint: {str(e)}")
            return False
            
    except ImportError:
        print("⚠️  requests library not available for webhook testing")
        return True  # Don't fail the overall check for this

def main():
    """Main verification function"""
    print("🚀 LogiScore Stripe Configuration Verification")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 4
    
    # Check 1: Environment variables
    if check_env_vars():
        checks_passed += 1
    
    # Check 2: Stripe API connection
    if test_stripe_connection():
        checks_passed += 1
    
    # Check 3: Price ID verification
    if verify_price_ids():
        checks_passed += 1
    
    # Check 4: Webhook endpoint
    if test_webhook_endpoint():
        checks_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Your Stripe integration is ready!")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the setup guide:")
        print("   📖 See STRIPE_SETUP_GUIDE.md for detailed instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
