#!/usr/bin/env python3
"""
Script to fetch Price IDs from Stripe - for Render environment
This script can be run in your Render environment where Stripe keys are configured
"""

import os
import sys

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
        
        # Set up Stripe API key (from Render environment)
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_key:
            print("❌ STRIPE_SECRET_KEY not found in environment variables")
            print("Make sure this script is running in your Render environment")
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
        
        # Generate environment configuration
        if env_vars:
            print("\n" + "=" * 60)
            print("🔧 Environment Variables for Render:")
            print("=" * 60)
            
            print("# Add these to your Render environment variables:")
            for env_var in env_vars:
                print(env_var)
            
            print("\n✅ Copy these variables to your Render environment!")
            
            # Save to file for easy copying
            with open('render_stripe_config.txt', 'w') as f:
                f.write("# Stripe Price IDs for Render Environment\n")
                f.write("# Copy these to your Render environment variables\n\n")
                for env_var in env_vars:
                    f.write(env_var + "\n")
            
            print(f"💾 Configuration saved to: render_stripe_config.txt")
            
        return True
        
    except ImportError:
        print("❌ Stripe library not installed. Run: pip install stripe")
        return False
    except stripe.error.AuthenticationError:
        print("❌ Invalid Stripe API key. Please check your STRIPE_SECRET_KEY in Render")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 LogiScore Stripe Price ID Fetcher - Render Version")
    print("This script will fetch Price IDs for your Stripe products")
    print("Run this in your Render environment where Stripe keys are configured")
    print()
    
    if fetch_price_ids():
        print("\n🎉 Success! Your Price IDs have been fetched.")
        print("Next steps:")
        print("1. Copy the environment variables to your Render environment")
        print("2. Deploy your updated backend")
        print("3. Test the subscription system!")
        return 0
    else:
        print("\n❌ Failed to fetch Price IDs. Please check your Stripe configuration in Render.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
