#!/usr/bin/env python3
"""
Simple API test script for the Smart Budgeting App
"""
import urllib.request
import urllib.error
import json
import sys

def test_api_endpoint(endpoint, description):
    """Test an API endpoint and return the result"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:5000{endpoint}") as response:
            data = response.read().decode('utf-8')
            json_data = json.loads(data)
            print(f"✅ {description}: SUCCESS")
            print(f"   Response: {json.dumps(json_data, indent=2)}")
            return True
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        return False

def main():
    print("🧪 Testing Smart Budgeting App API Endpoints")
    print("=" * 50)

    tests_passed = 0
    total_tests = 0

    # Test balance API
    total_tests += 1
    if test_api_endpoint("/api/balance", "Balance API"):
        tests_passed += 1

    # Test transactions API
    total_tests += 1
    if test_api_endpoint("/api/transactions", "Transactions API"):
        tests_passed += 1

    # Test category data API
    total_tests += 1
    if test_api_endpoint("/category_data", "Category Data API"):
        tests_passed += 1

    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All API tests passed! The OOP refactoring is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the application logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
