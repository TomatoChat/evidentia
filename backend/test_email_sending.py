#!/usr/bin/env python3
"""
Test script to verify email sending functionality
"""

import os
import sys
import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "mike@gmail.com"  # Change this to your real email for testing

def test_email_sending():
    """Test the complete email sending flow"""
    print("📧 Testing email sending functionality...\n")
    
    # Step 1: Collect email and get session_id
    print("1️⃣ Creating session with email...")
    response = requests.post(f"{BASE_URL}/collect-email", json={
        "email": TEST_EMAIL
    })
    
    if response.status_code != 200:
        print(f"❌ Email collection failed: {response.status_code}")
        return False
    
    data = response.json()
    session_id = data.get("session_id")
    if not session_id:
        print("❌ No session_id returned")
        return False
    
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Test email sending with mock data
    print(f"\n2️⃣ Testing email sending to {TEST_EMAIL}...")
    
    mock_analysis_result = {
        "queries": [
            {"topic": "Brand awareness", "prompt": "Test query 1"},
            {"topic": "Market positioning", "prompt": "Test query 2"}
        ],
        "analysis": {
            "competitors_analyzed": ["Competitor A", "Competitor B"],
            "optimization_suggestions": [
                "Improve brand visibility in search results",
                "Optimize content for better AI response inclusion",
                "Focus on industry-specific keywords",
                "Enhance brand authority signals",
                "Create more comprehensive content"
            ],
            "sources": [
                {"title": "Test Source 1", "url": "https://example.com/1"},
                {"title": "Test Source 2", "url": "https://example.com/2"}
            ]
        }
    }
    
    response = requests.post(f"{BASE_URL}/send-report", json={
        "session_id": session_id,
        "brandName": "Test Brand",
        "analysisResult": mock_analysis_result
    })
    
    print(f"📨 Email send response status: {response.status_code}")
    print(f"📨 Email send response: {response.text}")
    
    if response.status_code != 200:
        print(f"❌ Email sending failed: {response.status_code}")
        print(f"❌ Response: {response.text}")
        return False
    
    result = response.json()
    if result.get("success"):
        print(f"✅ Email sent successfully to {result.get('message', 'unknown recipient')}")
        print(f"📧 Check your inbox at {TEST_EMAIL}")
        return True
    else:
        print(f"❌ Email sending failed: {result.get('error', 'Unknown error')}")
        return False

def test_smtp_configuration():
    """Test SMTP configuration"""
    print("🔧 Testing SMTP configuration...\n")
    
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD") 
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    
    print(f"SMTP_EMAIL: {smtp_email[:10] + '***' if smtp_email else 'NOT SET'}")
    print(f"SMTP_PASSWORD: {'SET' if smtp_password else 'NOT SET'}")
    print(f"SMTP_SERVER: {smtp_server}")
    
    if not smtp_email or not smtp_password:
        print("❌ SMTP credentials not properly configured!")
        print("   Set SMTP_EMAIL and SMTP_PASSWORD environment variables")
        return False
    
    print("✅ SMTP credentials are configured")
    return True

def test_email_service_directly():
    """Test email service module directly"""
    print("\n🧪 Testing email service module directly...\n")
    
    try:
        import libs.email_service as email_service
        
        mock_analysis_result = {
            "queries": [{"topic": "Test", "prompt": "Test query"}],
            "analysis": {
                "competitors_analyzed": ["Test Competitor"],
                "optimization_suggestions": ["Test suggestion 1", "Test suggestion 2"]
            }
        }
        
        print(f"📧 Attempting to send email to {TEST_EMAIL}...")
        success = email_service.send_report_email(
            recipient_email=TEST_EMAIL,
            brand_name="Test Brand Direct",
            analysis_result=mock_analysis_result
        )
        
        if success:
            print("✅ Email sent successfully via direct module call!")
            return True
        else:
            print("❌ Email sending failed via direct module call")
            return False
            
    except Exception as e:
        print(f"❌ Direct email test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting email functionality tests...\n")
    
    # Test SMTP configuration
    if not test_smtp_configuration():
        print("\n❌ SMTP configuration test failed. Fix configuration and try again.")
        sys.exit(1)
    
    # Test email service directly
    print("\n" + "="*50)
    if test_email_service_directly():
        print("\n✅ Direct email service test passed!")
    else:
        print("\n❌ Direct email service test failed!")
    
    # Test via API endpoints
    print("\n" + "="*50)
    if test_email_sending():
        print("\n✅ API email sending test passed!")
    else:
        print("\n❌ API email sending test failed!")
    
    print(f"\n📧 If tests passed, check your email at {TEST_EMAIL}")
    print("💡 If you didn't receive emails, check:")
    print("   1. Spam/junk folder")
    print("   2. SMTP credentials are correct")
    print("   3. Gmail app passwords (if using Gmail)")
    print("   4. Firewall/network restrictions") 