#!/usr/bin/env python3
"""
Test script for the new review endpoints.
Run this to test the country and city-based review search functionality.
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your backend URL
API_BASE = f"{BASE_URL}/api/reviews"

def test_endpoint(endpoint: str, params: Optional[dict] = None, description: str = ""):
    """Test an endpoint and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    if params:
        print(f"Parameters: {params}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(endpoint, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    """Test all the new review endpoints"""
    print("Testing LogiScore Review Endpoints")
    print("=" * 60)
    
    # Test 1: Get all reviews (no filters)
    test_endpoint(
        f"{API_BASE}/",
        description="Get all reviews (no filters)"
    )
    
    # Test 2: Get reviews by country
    test_endpoint(
        f"{API_BASE}/",
        {"country": "australia", "page": 1, "page_size": 10},
        "Get reviews by country (Australia)"
    )
    
    # Test 3: Get reviews by city and country
    test_endpoint(
        f"{API_BASE}/",
        {"city": "berlin", "country": "germany", "page": 1, "page_size": 10},
        "Get reviews by city and country (Berlin, Germany)"
    )
    
    # Test 4: Get reviews by city only
    test_endpoint(
        f"{API_BASE}/",
        {"city": "sydney", "page": 1, "page_size": 10},
        "Get reviews by city only (Sydney)"
    )
    
    # Test 5: Get available countries
    test_endpoint(
        f"{API_BASE}/countries",
        description="Get list of available countries"
    )
    
    # Test 6: Get available cities
    test_endpoint(
        f"{API_BASE}/cities",
        description="Get list of available cities"
    )
    
    # Test 7: Get cities by country
    test_endpoint(
        f"{API_BASE}/cities",
        {"country": "australia"},
        "Get cities in Australia"
    )
    
    # Test 8: Get review statistics by location
    test_endpoint(
        f"{API_BASE}/statistics/location",
        {"country": "australia"},
        "Get review statistics for Australia"
    )
    
    # Test 9: Get review statistics by city
    test_endpoint(
        f"{API_BASE}/statistics/location",
        {"city": "sydney", "country": "australia"},
        "Get review statistics for Sydney, Australia"
    )
    
    # Test 10: Search reviews with text
    test_endpoint(
        f"{API_BASE}/",
        {"search": "service", "page": 1, "page_size": 10},
        "Search reviews containing 'service'"
    )
    
    print(f"\n{'='*60}")
    print("Testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
