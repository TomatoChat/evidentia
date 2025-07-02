#!/usr/bin/env python3
"""
Debug script to check why brand_analyses might be empty
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "mikececco2000@gmail.com"

def debug_brand_analysis():
    print("🔍 Debugging brand analysis saving...\n")
    
    # Step 1: Create session
    print("1️⃣ Creating session...")
    response = requests.post(f"{BASE_URL}/collect-email", json={
        "email": TEST_EMAIL
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data.get("session_id")
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Test brand analysis endpoint
    print(f"\n2️⃣ Testing brand analysis endpoint...")
    
    brand_data = {
        "brandWebsite": "https://testcompany.com",
        "brandName": "Test Company",
        "brandCountry": "United States",
        "session_id": session_id
    }
    
    print(f"📤 Sending request to /stream-brand-info with data:")
    print(f"   {json.dumps(brand_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/stream-brand-info", json=brand_data)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Brand analysis request successful")
        
        # Read the streaming response
        print("\n📊 Stream response:")
        response_text = response.text
        if response_text:
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: '
                        if data.get('status'):
                            print(f"   Status: {data['status']}")
                        if data.get('result'):
                            print(f"   Result: {data['result']}")
                        if data.get('error'):
                            print(f"   ❌ Error: {data['error']}")
                    except:
                        print(f"   Raw: {line}")
    else:
        print(f"❌ Brand analysis failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Step 3: Test Perplexity endpoint
    print(f"\n3️⃣ Testing Perplexity brand analysis...")
    
    perplexity_data = {
        "brandName": "Test Company Perplexity",
        "brandWebsite": "https://testcompany.com",
        "competitors": ["Competitor A", "Competitor B"],
        "session_id": session_id
    }
    
    response = requests.post(f"{BASE_URL}/perplexity-brand-analysis", json=perplexity_data)
    
    print(f"📥 Perplexity response status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Perplexity brand analysis successful")
        result = response.json()
        print(f"   Result keys: {list(result.keys())}")
    else:
        print(f"❌ Perplexity brand analysis failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    print(f"\n🎯 Session ID for database check: {session_id}")
    print("💡 Check server logs for Convex saving messages")
    print("💡 Look for messages like '✅ Brand analysis saved to Convex'")

if __name__ == "__main__":
    debug_brand_analysis() 