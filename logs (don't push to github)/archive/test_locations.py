#!/usr/bin/env python3
"""
Test script for the database-based locations endpoint
Run this after starting your FastAPI server and running the migration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_locations_endpoint():
    """Test the database-based locations endpoint with various queries"""
    
    print("🚀 Testing LogiScore Database-Based Locations API Endpoint\n")
    
    # Test 1: Get all locations
    print("1. Testing GET /api/locations (all locations)")
    try:
        response = requests.get(f"{BASE_URL}/api/locations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} locations")
            if data:
                print(f"   First location: {data[0]['name']} (UUID: {data[0]['uuid'][:8]}...)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Search by query
    print("2. Testing GET /api/locations?q=new york")
    try:
        response = requests.get(f"{BASE_URL}/api/locations?q=new york")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} locations matching 'new york'")
            for loc in data[:3]:  # Show first 3
                print(f"   - {loc['name']} (UUID: {loc['uuid'][:8]}...)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Filter by region
    print("3. Testing GET /api/locations?region=Europe")
    try:
        response = requests.get(f"{BASE_URL}/api/locations?region=Europe")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} locations in Europe")
            for loc in data[:3]:  # Show first 3
                print(f"   - {loc['name']} (UUID: {loc['uuid'][:8]}...)")
            if len(data) > 3:
                print(f"   ... and {len(data) - 3} more")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: Filter by country
    print("4. Testing GET /api/locations?country=USA")
    try:
        response = requests.get(f"{BASE_URL}/api/locations?country=USA")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} locations in USA")
            for loc in data[:3]:  # Show first 3
                print(f"   - {loc['name']} (UUID: {loc['uuid'][:8]}...)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 5: Search with limit
    print("5. Testing GET /api/locations?q=london&limit=5")
    try:
        response = requests.get(f"{BASE_URL}/api/locations?q=london&limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} locations (limited to 5)")
            for loc in data:
                print(f"   - {loc['name']} (UUID: {loc['uuid'][:8]}...)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 6: Get regions
    print("6. Testing GET /api/locations/regions")
    try:
        response = requests.get(f"{BASE_URL}/api/locations/regions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Available regions: {', '.join(data['regions'])}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 7: Get countries
    print("7. Testing GET /api/locations/countries")
    try:
        response = requests.get(f"{BASE_URL}/api/locations/countries")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data['countries'])} countries")
            print(f"   Sample countries: {', '.join(data['countries'][:10])}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 8: Get location by UUID (if we have data)
    print("8. Testing GET /api/locations/{uuid}")
    try:
        # First get a location to extract its UUID
        response = requests.get(f"{BASE_URL}/api/locations?limit=1")
        if response.status_code == 200:
            data = response.json()
            if data:
                location_uuid = data[0]['uuid']
                print(f"   Testing with UUID: {location_uuid[:8]}...")
                
                # Now test the UUID endpoint
                uuid_response = requests.get(f"{BASE_URL}/api/locations/{location_uuid}")
                if uuid_response.status_code == 200:
                    location_data = uuid_response.json()
                    print(f"✅ Success! Retrieved location: {location_data['name']}")
                    print(f"   UUID: {location_data['uuid']}")
                    print(f"   City: {location_data['city']}, Country: {location_data['country']}")
                else:
                    print(f"❌ Failed to get location by UUID: {uuid_response.status_code}")
            else:
                print("   No locations available for UUID test")
        else:
            print(f"   Could not get sample location: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in UUID test: {e}")
    
    print()
    
    # Test 9: Autocomplete search
    print("9. Testing GET /api/locations/search/autocomplete?q=lon")
    try:
        response = requests.get(f"{BASE_URL}/api/locations/search/autocomplete?q=lon")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} autocomplete results for 'lon'")
            for loc in data[:3]:  # Show first 3
                print(f"   - {loc['name']} (UUID: {loc['uuid'][:8]}...)")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Testing complete!")
    print("\n💡 Key Benefits of Database Implementation:")
    print("   - UUIDs for reviews system integration")
    print("   - Fast database queries with indexes")
    print("   - Scalable to millions of locations")
    print("   - Real-time data updates")
    print("   - Better performance and memory usage")

if __name__ == "__main__":
    test_locations_endpoint()
