#!/usr/bin/env python3
"""
Test script to verify the review count fix for the category scores API.
This script tests the specific case mentioned in the bug report:
- Company: Nippon Express
- City: San Francisco, US
- Expected: All categories should show 1 review (not inflated counts)
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Update this to your backend URL
TEST_COMPANY_NAME = "Nippon Express"
TEST_CITY = "San Francisco"
TEST_COUNTRY = "US"

def test_freight_forwarder_endpoint():
    """Test the freight forwarder endpoint to verify review count fix"""
    
    print(f"🔍 Testing review count fix for {TEST_COMPANY_NAME}")
    print(f"📍 Location: {TEST_CITY}, {TEST_COUNTRY}")
    print("=" * 60)
    
    try:
        # Step 1: Search for Nippon Express to get their ID
        print("1. Searching for Nippon Express...")
        search_response = requests.get(
            f"{BASE_URL}/api/freight-forwarders/",
            params={"search": TEST_COMPANY_NAME}
        )
        
        if search_response.status_code != 200:
            print(f"❌ Failed to search for company: {search_response.status_code}")
            return
        
        companies = search_response.json()
        if not companies:
            print(f"❌ No companies found matching '{TEST_COMPANY_NAME}'")
            return
        
        # Find Nippon Express
        nippon_express = None
        for company in companies:
            if TEST_COMPANY_NAME.lower() in company['name'].lower():
                nippon_express = company
                break
        
        if not nippon_express:
            print(f"❌ Company '{TEST_COMPANY_NAME}' not found in search results")
            return
        
        company_id = nippon_express['id']
        print(f"✅ Found {nippon_express['name']} with ID: {company_id}")
        
        # Step 2: Test without location filtering (should show inflated counts if bug exists)
        print("\n2. Testing WITHOUT location filtering (should show inflated counts if bug exists)...")
        no_filter_response = requests.get(f"{BASE_URL}/api/freight-forwarders/{company_id}")
        
        if no_filter_response.status_code != 200:
            print(f"❌ Failed to get company without filters: {no_filter_response.status_code}")
            return
        
        no_filter_data = no_filter_response.json()
        print(f"   Total reviews (no filter): {no_filter_data.get('review_count', 'N/A')}")
        
        category_scores = no_filter_data.get('category_scores_summary', {})
        if category_scores:
            print("   Category scores (no filter):")
            for category_id, data in category_scores.items():
                print(f"     {data.get('category_name', category_id)}: {data.get('total_reviews', 'N/A')} reviews")
        else:
            print("   No category scores found (no filter)")
        
        # Step 3: Test WITH location filtering (should show correct counts)
        print(f"\n3. Testing WITH location filtering ({TEST_CITY}, {TEST_COUNTRY})...")
        filtered_response = requests.get(
            f"{BASE_URL}/api/freight-forwarders/{company_id}",
            params={"city": TEST_CITY, "country": TEST_COUNTRY}
        )
        
        if filtered_response.status_code != 200:
            print(f"❌ Failed to get company with location filters: {filtered_response.status_code}")
            return
        
        filtered_data = filtered_response.json()
        print(f"   Total reviews (with filters): {filtered_data.get('review_count', 'N/A')}")
        
        category_scores_filtered = filtered_data.get('category_scores_summary', {})
        if category_scores_filtered:
            print("   Category scores (with filters):")
            for category_id, data in category_scores_filtered.items():
                print(f"     {data.get('category_name', category_id)}: {data.get('total_reviews', 'N/A')} reviews")
        else:
            print("   No category scores found (with filters)")
        
        # Step 4: Verify the fix
        print("\n4. Verifying the fix...")
        
        # Check if location filtering is working
        if filtered_data.get('review_count', 0) < no_filter_data.get('review_count', 0):
            print("   ✅ Location filtering is working (filtered count < unfiltered count)")
        else:
            print("   ⚠️  Location filtering may not be working as expected")
        
        # Check if category review counts are consistent
        category_review_counts = []
        for category_id, data in category_scores_filtered.items():
            category_review_counts.append(data.get('total_reviews', 0))
        
        if category_review_counts:
            unique_counts = set(category_review_counts)
            if len(unique_counts) == 1:
                print(f"   ✅ All categories show consistent review count: {list(unique_counts)[0]}")
            else:
                print(f"   ❌ Inconsistent review counts across categories: {unique_counts}")
        else:
            print("   ⚠️  No category scores to verify")
        
        # Check if the counts match the total review count
        total_reviews = filtered_data.get('review_count', 0)
        if category_review_counts:
            max_category_count = max(category_review_counts)
            if max_category_count == total_reviews:
                print(f"   ✅ Category review counts match total review count: {total_reviews}")
            else:
                print(f"   ❌ Category review count ({max_category_count}) doesn't match total review count ({total_reviews})")
        
        print("\n" + "=" * 60)
        print("🎯 Test Summary:")
        print(f"   Company: {nippon_express['name']}")
        print(f"   Location: {TEST_CITY}, {TEST_COUNTRY}")
        print(f"   Total reviews (unfiltered): {no_filter_data.get('review_count', 'N/A')}")
        print(f"   Total reviews (filtered): {filtered_data.get('review_count', 'N/A')}")
        
        if category_scores_filtered:
            print("   Category review counts (filtered):")
            for category_id, data in category_scores_filtered.items():
                print(f"     {data.get('category_name', category_id)}: {data.get('total_reviews', 'N/A')}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Make sure your backend is running on {BASE_URL}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_reviews_endpoint():
    """Test the reviews endpoint to get actual review data for verification"""
    
    print(f"\n🔍 Verifying actual review data for {TEST_COMPANY_NAME}")
    print("=" * 60)
    
    try:
        # Search for reviews by company name and location
        print(f"1. Searching for reviews by company and location...")
        
        # First, get reviews by company name
        reviews_response = requests.get(
            f"{BASE_URL}/api/reviews/",
            params={"search": TEST_COMPANY_NAME}
        )
        
        if reviews_response.status_code != 200:
            print(f"❌ Failed to get reviews: {reviews_response.status_code}")
            return
        
        reviews_data = reviews_response.json()
        reviews = reviews_data.get('reviews', [])
        
        print(f"   Found {len(reviews)} total reviews for {TEST_COMPANY_NAME}")
        
        # Filter by location
        location_filtered_reviews = []
        for review in reviews:
            if (review.get('city', '').lower() == TEST_CITY.lower() and 
                review.get('country', '').lower() == TEST_COUNTRY.lower()):
                location_filtered_reviews.append(review)
        
        print(f"   Reviews in {TEST_CITY}, {TEST_COUNTRY}: {len(location_filtered_reviews)}")
        
        if location_filtered_reviews:
            print("   Review details:")
            for i, review in enumerate(location_filtered_reviews, 1):
                print(f"     Review {i}:")
                print(f"       ID: {review.get('id')}")
                print(f"       Rating: {review.get('aggregate_rating')}")
                print(f"       Type: {review.get('review_type')}")
                print(f"       Created: {review.get('created_at')}")
                print(f"       City: {review.get('city')}")
                print(f"       Country: {review.get('country')}")
        
        # Get review statistics for the location
        print(f"\n2. Getting review statistics for {TEST_CITY}, {TEST_COUNTRY}...")
        stats_response = requests.get(
            f"{BASE_URL}/api/reviews/statistics/location",
            params={"city": TEST_CITY, "country": TEST_COUNTRY}
        )
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"   Total reviews in location: {stats_data.get('total_reviews', 'N/A')}")
            print(f"   Average rating: {stats_data.get('average_rating', 'N/A')}")
        else:
            print(f"   ⚠️  Could not get location statistics: {stats_response.status_code}")
        
    except Exception as e:
        print(f"❌ Review verification failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Review Count Fix Test")
    print("=" * 60)
    
    # Test the main endpoint
    test_freight_forwarder_endpoint()
    
    # Test the reviews endpoint for verification
    test_reviews_endpoint()
    
    print("\n🏁 Test completed!")
    print("\n📋 Expected Results:")
    print("   ✅ Location filtering should reduce review counts")
    print("   ✅ All categories should show the same review count")
    print("   ✅ Category review counts should match total review count")
    print("   ✅ No more inflated counts (45, 36, 54, 27, 18)")
