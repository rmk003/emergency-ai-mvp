"""
Тест локального запуска перед деплоем на Railway
"""
import subprocess
import time
import requests
import sys
import os

print("🧪 Testing Railway deployment preparation...\n")

def test_environment_setup():
    print("1. 🔧 Testing environment setup...")
    
    # Проверяем наличие необходимых переменных окружения
    required_env = ["BLAND_API_KEY", "EMERGENCY_PHONE"]
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print(f"❌ Missing environment variables: {', '.join(missing_env)}")
        print("   Set them in your .env file for local testing")
        return False
    else:
        print("✅ Environment variables configured")
        return True

def test_server_startup():
    print("2. 🚀 Testing server startup...")
    
    # Останавливаем текущий сервер если запущен
    print("   Stopping any existing server...")
    
    # Запускаем новый сервер
    print("   Starting fresh server...")
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Ждем запуска
    time.sleep(5)
    
    try:
        # Тестируем health check endpoint
        response = requests.get("http://localhost:8000/api/test", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server started successfully")
            print(f"   Service: {data['service']}")
            print(f"   Version: {data['version']}")
            return True, process
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False, process
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return False, process

def test_emergency_endpoint(process):
    print("3. 🚨 Testing emergency endpoint...")
    
    try:
        payload = {
            "incident_type": "medical_emergency",
            "severity": "high", 
            "additional_info": "Railway deployment test - DO NOT DISPATCH"
        }
        
        response = requests.post(
            "http://localhost:8000/api/emergency",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Emergency endpoint working")
            print(f"   Call ID: {data.get('call_id', 'N/A')}")
            print(f"   Emergency Phone: {data.get('emergency_phone', 'N/A')}")
            return True
        else:
            print(f"❌ Emergency endpoint failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Emergency endpoint test failed: {e}")
        return False
    finally:
        # Останавливаем сервер
        process.terminate()
        process.wait()

def main():
    print("🛡️ Railway Deployment Test - Emergency AI Assistant")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Тест 1: Environment
    if test_environment_setup():
        tests_passed += 1
    
    print()
    
    # Тест 2: Server startup
    server_ok, process = test_server_startup()
    if server_ok:
        tests_passed += 1
        
        print()
        
        # Тест 3: Emergency endpoint (только если сервер работает)
        if test_emergency_endpoint(process):
            tests_passed += 1
    else:
        if process:
            process.terminate()
    
    print()
    print("📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Ready for Railway deployment!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Ready for Railway deployment'")
        print("3. git branch -M main") 
        print("4. Push to GitHub")
        print("5. Connect to Railway")
    else:
        print("⚠️  Some tests failed. Fix issues before deploying.")
        if tests_passed == 0:
            print("\nTroubleshooting:")
            print("- Make sure .env file has BLAND_API_KEY and EMERGENCY_PHONE")
            print("- Check if port 8000 is available") 
            print("- Verify all dependencies are installed")

if __name__ == "__main__":
    main()