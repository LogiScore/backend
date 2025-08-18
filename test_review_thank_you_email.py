#!/usr/bin/env python3
"""
Test script for the review thank you email endpoint
This script tests the /api/email/review-thank-you endpoint
"""

import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your backend URL
ENDPOINT = "/api/email/review-thank-you"

def test_review_thank_you_email():
    """Test the review thank you email endpoint"""
    
    # Test data - you'll need to use a real review ID from your database
    test_data = {
        "review_id": "test-uuid-here"  # Replace with actual review ID
    }
    
    print(f"Testing endpoint: {BASE_URL}{ENDPOINT}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        # Make POST request
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Email sent successfully")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ FAILED: Request failed")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to the backend server")
        print("Make sure the backend is running on the specified URL")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_invalid_request():
    """Test with invalid request data"""
    
    print("\n" + "=" * 50)
    print("Testing with invalid request data")
    print("=" * 50)
    
    # Test with missing review_id
    invalid_data = {}
    
    print(f"Testing with invalid data: {json.dumps(invalid_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ SUCCESS: Properly handled invalid request")
            print(f"Response: {response.text}")
        else:
            print("❌ FAILED: Should have returned 400 for invalid request")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_nonexistent_review():
    """Test with non-existent review ID"""
    
    print("\n" + "=" * 50)
    print("Testing with non-existent review ID")
    print("=" * 50)
    
    # Generate a random UUID that won't exist in the database
    fake_uuid = str(uuid.uuid4())
    test_data = {
        "review_id": fake_uuid
    }
    
    print(f"Testing with fake UUID: {fake_uuid}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✅ SUCCESS: Properly handled non-existent review")
            print(f"Response: {response.text}")
        else:
            print("❌ FAILED: Should have returned 404 for non-existent review")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🚀 LogiScore Review Thank You Email Endpoint Test")
    print("=" * 60)
    
    # Test valid request (you'll need to update the review_id)
    test_review_thank_you_email()
    
    # Test invalid request
    test_invalid_request()
    
    # Test non-existent review
    test_nonexistent_review()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("\nNote: To test with real data, update the review_id in test_review_thank_you_email()")
    print("with an actual review ID from your database.")
