#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_server_status():
    print("🔍 Testing server status...")
    try:
        response = requests.get(f"{BASE_URL}/api/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is online: {data['service']} v{data['version']}")
            print(f"📅 Server time: {data['timestamp']}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_emergency_endpoint():
    print("\n🚨 Testing emergency endpoint...")
    try:
        payload = {
            "incident_type": "medical_emergency",
            "severity": "high",
            "additional_info": "Local test call - DO NOT DISPATCH REAL SERVICES"
        }
        
        print("📤 Sending emergency request...")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/emergency", 
            json=payload, 
            timeout=30
        )
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Emergency endpoint test successful!")
            print(f"📞 Call ID: {data.get('call_id', 'N/A')}")
            print(f"📱 Emergency phone: {data.get('emergency_phone', 'N/A')}")
            print(f"🕒 Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"📧 SMS sent: {data.get('sms_sent', False)}")
            
            if 'data_used' in data:
                print("📋 Data used in emergency call:")
                for key, value in data['data_used'].items():
                    print(f"   {key}: {value}")
            
            return True
        else:
            print(f"❌ Emergency endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error details: {error_data}")
            except:
                print(f"🔍 Raw response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during emergency test: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False

def test_demo_page():
    print("\n🖥️  Testing demo page...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Demo page is accessible")
            print(f"📄 Content length: {len(response.content)} bytes")
            if "RideGuard Safety" in response.text:
                print("✅ Demo page contains expected content")
                return True
            else:
                print("❌ Demo page missing expected content")
                return False
        else:
            print(f"❌ Demo page returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access demo page: {e}")
        return False

def main():
    print("🛡️ RideGuard Emergency AI Assistant - Local Test Suite")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Testing against: {BASE_URL}")
    print()
    
    print("⚠️  IMPORTANT: This is a local test script.")
    print("⚠️  No real emergency calls will be made.")
    print("⚠️  Ensure your .env file has BLAND_API_KEY configured.")
    print()
    
    # Test sequence
    tests = [
        ("Server Status", test_server_status),
        ("Demo Page", test_demo_page),
        ("Emergency Endpoint", test_emergency_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running test: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 30)
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for demo.")
    else:
        print("⚠️  Some tests failed. Check configuration and server status.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the server is running (./run.sh)")
        print("2. Check your .env file has BLAND_API_KEY configured")
        print("3. Verify all dependencies are installed")
        print("4. Check firewall settings for port 8000")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()