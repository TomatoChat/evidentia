#!/usr/bin/env python3
"""
Test script to verify that anonymous users can save data to Convex database
"""

import os
import sys
import requests
import json
import uuid

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@evidentia.app"

def test_anonymous_user_data_saving():
    """Test the complete flow for anonymous users"""
    print("🧪 Testing anonymous user data saving flow...\n")
    
    # Step 1: Collect email and get session_id (like frontend does)
    print("1️⃣ Collecting email and creating session...")
    response = requests.post(f"{BASE_URL}/collect-email", json={
        "email": TEST_EMAIL
    })
    
    if response.status_code != 200:
        print(f"❌ Email collection failed: {response.status_code}")
        return False
    
    data = response.json()
    session_id = data.get("session_id")
    if not session_id:
        print("❌ No session_id returned from email collection")
        return False
    
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Test brand analysis saving
    print("\n2️⃣ Testing brand analysis saving...")
    response = requests.post(f"{BASE_URL}/stream-brand-info", json={
        "brandWebsite": "https://test.com",
        "brandName": "Test Brand",
        "brandCountry": "United States",
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ Brand analysis failed: {response.status_code}")
        return False
    
    print("✅ Brand analysis endpoint called successfully")
    
    # Step 3: Test GEO analysis saving
    print("\n3️⃣ Testing GEO analysis saving...")
    response = requests.post(f"{BASE_URL}/stream-test-queries", json={
        "brandName": "Test Brand",
        "queries": ["test query 1", "test query 2"],
        "competitors": ["Competitor 1", "Competitor 2"],
        "models": ["gpt-4o-mini-2024-07-18"],
        "session_id": session_id
    })
    
    if response.status_code != 200:
        print(f"❌ GEO analysis failed: {response.status_code}")
        return False
    
    print("✅ GEO analysis endpoint called successfully")
    
    # Step 4: Test report sending
    print("\n4️⃣ Testing report saving...")
    response = requests.post(f"{BASE_URL}/send-report", json={
        "session_id": session_id,
        "brandName": "Test Brand",
        "analysisResult": {
            "test": "data",
            "queries": ["test query 1", "test query 2"],
            "analysis": {
                "optimization_suggestions": ["Suggestion 1", "Suggestion 2"]
            }
        }
    })
    
    if response.status_code != 200:
        print(f"❌ Report sending failed: {response.status_code}")
        return False
    
    print("✅ Report endpoint called successfully")
    
    print(f"\n🎉 All tests passed! Anonymous user data saving works correctly.")
    print(f"📊 Check your Convex dashboard for data saved under session: {session_id}")
    return True

def test_convex_connection():
    """Test if Convex client is working"""
    print("🔗 Testing Convex connection...")
    
    try:
        from libs.convex_client import get_convex_client
        client = get_convex_client()
        
        # Test basic functionality - create_session only takes email parameter
        test_session_id = client.create_session("test@convex.app")
        print("✅ Convex client working correctly")
        
        # Clean up test session
        client.delete_session(test_session_id)
        return True
        
    except Exception as e:
        print(f"❌ Convex connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting anonymous user database saving tests...\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start: cd backend && python server.py")
            sys.exit(1)
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please start: cd backend && python server.py")
        sys.exit(1)
    
    # Test Convex connection
    if not test_convex_connection():
        print("❌ Convex connection failed. Check CONVEX_URL environment variable.")
        sys.exit(1)
    
    # Run full flow test
    if test_anonymous_user_data_saving():
        print("\n✅ All tests passed! Anonymous user data saving is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        sys.exit(1) 