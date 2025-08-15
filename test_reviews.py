#!/usr/bin/env python3
"""
Test script for the LogiScore review system endpoints
Run this after starting your FastAPI server to test the review functionality
"""

import requests
import json
from uuid import uuid4

# Base URL for your API
BASE_URL = "http://localhost:8000"

def test_review_endpoints():
    """Test all review endpoints"""
    
    print("🧪 Testing LogiScore Review System Endpoints\n")
    
    # Test 1: Get review questions
    print("1. Testing GET /api/reviews/questions")
    try:
        response = requests.get(f"{BASE_URL}/api/reviews/questions")
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ Success! Found {len(questions)} categories")
            for category in questions:
                print(f"   - {category['name']}: {len(category['questions'])} questions")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Get reviews for a freight forwarder (this will be empty initially)
    print("2. Testing GET /api/reviews/freight-forwarder/{id}")
    try:
        # Use a dummy UUID for testing
        dummy_id = str(uuid4())
        response = requests.get(f"{BASE_URL}/api/reviews/freight-forwarder/{dummy_id}")
        if response.status_code == 200:
            reviews = response.json()
            print(f"✅ Success! Found {len(reviews)} reviews")
        elif response.status_code == 404:
            print("✅ Expected: No freight forwarder found (using dummy ID)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Health check
    print("3. Testing health check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Health: {health.get('status', 'unknown')}")
            print(f"   Database: {health.get('database', 'unknown')}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("🎯 Review system backend testing complete!")
    print("💡 To test review creation, you'll need:")
    print("   - A valid freight forwarder ID from your database")
    print("   - The review_questions table populated with questions")
    print("   - A valid JWT token for authenticated reviews")

if __name__ == "__main__":
    test_review_endpoints()
