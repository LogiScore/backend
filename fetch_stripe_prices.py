#!/usr/bin/env python3
"""
Script to fetch Price IDs from Stripe using Product IDs
This will help you get the Price IDs needed for the subscription system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Your Product IDs from the CSV
PRODUCT_IDS = {
    'shipper_monthly': 'prod_StYy4QPzGhoMQU',
    'shipper_annual': 'prod_StZ0qjHzGSSZZ9', 
    'forwarder_monthly': 'prod_StZ1HjEEPrZ8oo',
    'forwarder_annual': 'prod_StZ2pVrOSMVZIn',
    'forwarder_annual_plus': 'prod_StZ3890Xh8lQCZ'
}

def fetch_price_ids():
    """Fetch Price IDs from Stripe for each Product ID"""
    try:
        import stripe
        
        # Set up Stripe API key
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_key:
            print("❌ STRIPE_SECRET_KEY not found in environment variables")
            print("Please add your Stripe secret key to .env file:")
            print("STRIPE_SECRET_KEY=sk_test_your_key_here")
            return False
        
        stripe.api_key = stripe_key
        
        print("🔍 Fetching Price IDs from Stripe...")
        print("=" * 60)
        
        env_vars = []
        
        for plan_name, product_id in PRODUCT_IDS.items():
            try:
                print(f"\n📦 {plan_name.replace('_', ' ').title()}: {product_id}")
                
                # Get product details
                product = stripe.Product.retrieve(product_id)
                print(f"   Product Name: {product.name}")
                
                # Get all prices for this product
                prices = stripe.Price.list(product=product_id, limit=10)
                
                if len(prices.data) == 0:
                    print("   ⚠️  No prices found for this product")
                    continue
                
                # Display all prices
                for i, price in enumerate(prices.data):
                    interval = price.recurring.interval if price.recurring else 'one-time'
                    amount = price.unit_amount / 100 if price.unit_amount else 'N/A'
                    currency = price.currency.upper()
                    
                    print(f"   Price {i+1}: {price.id}")
                    print(f"            Amount: {currency} {amount} per {interval}")
                    print(f"            Active: {price.active}")
                    
                    # If this is the first/active price, use it for env var
                    if i == 0 or price.active:
                        env_var_name = f"STRIPE_{plan_name.upper()}_PRICE_ID"
                        env_vars.append(f"{env_var_name}={price.id}")
                        print(f"   ✅ Will use: {price.id}")
                        break
                
            except stripe.error.InvalidRequestError as e:
                print(f"   ❌ Error: {str(e)}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {str(e)}")
        
        # Generate .env configuration
        if env_vars:
            print("\n" + "=" * 60)
            print("🔧 Environment Variables for .env file:")
            print("=" * 60)
            
            # Add basic Stripe config
            print("# Stripe Configuration")
            print(f"STRIPE_SECRET_KEY={stripe_key}")
            print("STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here")
            print("STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here")
            print()
            print("# Stripe Price IDs")
            for env_var in env_vars:
                print(env_var)
            
            print("\n✅ Copy the above configuration to your .env file!")
            
            # Save to file
            with open('.env.generated', 'w') as f:
                f.write("# Generated Stripe Configuration\n")
                f.write(f"STRIPE_SECRET_KEY={stripe_key}\n")
                f.write("STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here\n")
                f.write("STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here\n\n")
                f.write("# Stripe Price IDs\n")
                for env_var in env_vars:
                    f.write(env_var + "\n")
            
            print(f"💾 Configuration also saved to: .env.generated")
            
        return True
        
    except ImportError:
        print("❌ Stripe library not installed. Run: pip install stripe")
        return False
    except stripe.error.AuthenticationError:
        print("❌ Invalid Stripe API key. Please check your STRIPE_SECRET_KEY")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 LogiScore Stripe Price ID Fetcher")
    print("This script will fetch Price IDs for your Stripe products")
    print()
    
    if fetch_price_ids():
        print("\n🎉 Success! Your Price IDs have been fetched.")
        print("Next steps:")
        print("1. Copy the environment variables to your .env file")
        print("2. Run: python3 verify_stripe_setup.py")
        print("3. Test the subscription system!")
        return 0
    else:
        print("\n❌ Failed to fetch Price IDs. Please check your Stripe configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
