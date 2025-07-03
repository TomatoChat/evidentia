#!/usr/bin/env python3
"""
Quick test to check server connectivity and brand analysis
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def quick_test():
    print("🔍 Quick server and brand analysis test...\n")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return
    
    # Test 2: Create session
    try:
        response = requests.post(f"{BASE_URL}/collect-email", json={
            "email": "mikececco2000@gmail.com"
        })
        if response.status_code == 200:
            session_id = response.json().get("session_id")
            print(f"✅ Session created: {session_id}")
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return
    
    # Test 3: Simple brand analysis
    try:
        print("\n📊 Testing brand analysis...")
        response = requests.post(f"{BASE_URL}/stream-brand-info", json={
            "brandWebsite": "https://apple.com",
            "brandName": "Apple",
            "brandCountry": "United States",
            "session_id": session_id
        })
        
        print(f"Brand analysis status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if we got streaming data
            if response.text:
                print("✅ Got response data")
                lines = response.text.split('\n')[:5]  # Show first 5 lines
                for line in lines:
                    if line.strip():
                        print(f"  {line[:100]}...")
            else:
                print("⚠️ Empty response")
        else:
            print(f"❌ Brand analysis failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Brand analysis error: {e}")

if __name__ == "__main__":
    quick_test() 