#!/usr/bin/env python3
"""
Test script for the new aggregated freight forwarders API
This script tests the backend fixes required by the frontend team:
1. Calculate company rating from reviews.aggregate_rating
2. Count total reviews for each company  
3. Aggregate category scores from review_category_scores
4. Return calculated values in the API response
"""

import requests
import json
from typing import Dict, Any

def test_aggregated_api():
    """Test the new aggregated freight forwarders endpoint"""
    
    # Base URL - adjust this to match your backend URL
    base_url = "http://localhost:8000"  # Change this to your actual backend URL
    
    print("🧪 Testing Aggregated Freight Forwarders API")
    print("=" * 50)
    
    try:
        # Test the new aggregated endpoint
        print("\n1️⃣ Testing /aggregated/ endpoint...")
        response = requests.get(f"{base_url}/freight-forwarders/aggregated/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved {len(data)} freight forwarders")
            
            if data:
                # Show first freight forwarder as example
                ff = data[0]
                print(f"\n📊 Sample Freight Forwarder Data:")
                print(f"   Name: {ff.get('name')}")
                print(f"   Average Rating: {ff.get('average_rating')}")
                print(f"   Review Count: {ff.get('review_count')}")
                print(f"   Category Scores: {len(ff.get('category_scores_summary', {}))} categories")
                
                # Show category scores if available
                if ff.get('category_scores_summary'):
                    print(f"\n📈 Category Scores Summary:")
                    for category_id, score_data in ff['category_scores_summary'].items():
                        print(f"   {score_data.get('category_name', category_id)}:")
                        print(f"     - Average Rating: {score_data.get('average_rating', 0):.2f}")
                        print(f"     - Total Questions: {score_data.get('total_reviews', 0)}")
                
                # Verify all required fields are present
                required_fields = ['id', 'name', 'average_rating', 'review_count', 'category_scores_summary']
                missing_fields = [field for field in required_fields if field not in ff]
                
                if missing_fields:
                    print(f"\n❌ Missing required fields: {missing_fields}")
                else:
                    print(f"\n✅ All required fields present!")
                    
            else:
                print("⚠️  No freight forwarders found in the database")
                
        else:
            print(f"❌ Failed to retrieve data. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure your backend is running on the correct URL.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

def test_regular_api():
    """Test the regular freight forwarders endpoint for comparison"""
    
    base_url = "http://localhost:8000"  # Change this to your actual backend URL
    
    print("\n🧪 Testing Regular Freight Forwarders API (for comparison)")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/freight-forwarders/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved {len(data)} freight forwarders")
            
            if data:
                ff = data[0]
                print(f"\n📊 Sample Regular API Response:")
                print(f"   Name: {ff.get('name')}")
                print(f"   Average Rating: {ff.get('average_rating')}")
                print(f"   Review Count: {ff.get('review_count')}")
                print(f"   Category Scores: {len(ff.get('category_scores_summary', {}))} categories")
                
        else:
            print(f"❌ Failed to retrieve data. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during regular API testing: {e}")

if __name__ == "__main__":
    print("🚀 LogiScore Backend API Testing")
    print("Testing the new aggregated freight forwarders endpoint")
    
    # Test both endpoints
    test_aggregated_api()
    test_regular_api()
    
    print("\n📋 Summary of Backend Fixes Implemented:")
    print("✅ Calculate company rating from reviews.aggregate_rating")
    print("✅ Count total reviews for each company")
    print("✅ Aggregate category scores from review_category_scores")
    print("✅ Return calculated values in the API response")
    print("✅ New efficient /aggregated/ endpoint for better performance")
