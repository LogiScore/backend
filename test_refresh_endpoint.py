#!/usr/bin/env python3
"""
Test script for the JWT refresh endpoint
This script tests the /api/auth/refresh endpoint functionality
"""

import requests
import json
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

def create_expired_token(user_id: str, minutes_ago: int = 35) -> str:
    """Create an expired JWT token for testing"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() - timedelta(minutes=minutes_ago),
        "iat": datetime.utcnow() - timedelta(minutes=minutes_ago + 5)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def test_refresh_endpoint():
    """Test the refresh endpoint with various scenarios"""
    
    print("🧪 Testing JWT Refresh Endpoint")
    print("=" * 50)
    
    # Test 1: Valid expired token
    print("\n1. Testing with valid expired token...")
    expired_token = create_expired_token("test-user-123")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"token": expired_token},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! New token: {data['access_token'][:20]}...")
        print(f"Token type: {data['token_type']}")
        print(f"Expires in: {data['expires_in']} seconds")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 2: Invalid token format
    print("\n2. Testing with invalid token format...")
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"token": "invalid.token.format"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly rejected invalid token")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Test 3: Missing token
    print("\n3. Testing with missing token...")
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 422:  # Validation error
        print("✅ Correctly rejected missing token")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Test 4: Token with non-existent user
    print("\n4. Testing with token for non-existent user...")
    expired_token_nonexistent = create_expired_token("non-existent-user-456")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        json={"token": expired_token_nonexistent},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly rejected token for non-existent user")
    else:
        print(f"❌ Unexpected response: {response.text}")

if __name__ == "__main__":
    try:
        test_refresh_endpoint()
        print("\n🎉 Refresh endpoint testing completed!")
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        print("Make sure your FastAPI backend is running on the correct port")

