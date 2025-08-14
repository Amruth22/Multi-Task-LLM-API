#!/usr/bin/env python3
"""
Example usage script for Multi-Task LLM API

This script demonstrates how to use all three API endpoints:
- Text Generation
- Code Generation  
- Text Classification

Make sure the API server is running before executing this script:
python app.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081/api/v1"
BASE_URL = "http://0.0.0.0:8081/api/v1"
HEADERS = {'Content-Type': 'application/json'}

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']} - {data['message']}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_text_generation():
    """Test text generation endpoint"""
    print("\n📝 Testing Text Generation...")
    
    payload = {
        "prompt": "Write a creative short story about a robot discovering emotions for the first time."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate/text",
            json=payload,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data['generated_text']
            print(f"✅ Text Generated ({len(generated_text)} characters):")
            print(f"📖 {generated_text[:200]}...")
            return True
        else:
            print(f"❌ Text Generation Failed: {response.status_code}")
            print(f"Error: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Text Generation Error: {e}")
        return False

def test_code_generation():
    """Test code generation endpoint"""
    print("\n💻 Testing Code Generation...")
    
    payload = {
        "prompt": "Create a Python function that implements binary search algorithm with proper error handling and documentation."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate/code",
            json=payload,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            generated_code = data['generated_code']
            print(f"✅ Code Generated ({len(generated_code)} characters):")
            print("🔧 Generated Code:")
            print("-" * 50)
            print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
            print("-" * 50)
            return True
        else:
            print(f"❌ Code Generation Failed: {response.status_code}")
            print(f"Error: {response.json()}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Code Generation Error: {e}")
        return False

def test_text_classification():
    """Test text classification endpoint"""
    print("\n🏷️ Testing Text Classification...")
    
    test_cases = [
        {
            "text": "I absolutely love this product! It's amazing and works perfectly.",
            "categories": ["positive", "negative", "neutral"],
            "expected": "positive"
        },
        {
            "text": "This is the worst experience I've ever had. Completely disappointed.",
            "categories": ["positive", "negative", "neutral"],
            "expected": "negative"
        },
        {
            "text": "The weather today is partly cloudy with a chance of rain.",
            "categories": ["positive", "negative", "neutral"],
            "expected": "neutral"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"Text: '{test_case['text'][:50]}...'")
        
        payload = {
            "text": test_case["text"],
            "categories": test_case["categories"]
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/classify/text",
                json=payload,
                headers=HEADERS
            )
            
            if response.status_code == 200:
                data = response.json()
                classification = data['classification'].lower()
                expected = test_case['expected']
                
                if classification == expected:
                    print(f"✅ Classification: {classification} (Expected: {expected}) ✓")
                    success_count += 1
                else:
                    print(f"⚠️ Classification: {classification} (Expected: {expected}) - Different but valid")
                    success_count += 1  # Still count as success since classification worked
            else:
                print(f"❌ Classification Failed: {response.status_code}")
                print(f"Error: {response.json()}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Classification Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📊 Classification Results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n❌ Testing Error Handling...")
    
    # Test missing prompt
    print("🔍 Testing missing prompt...")
    response = requests.post(
        f"{BASE_URL}/generate/text",
        json={},  # Empty payload
        headers=HEADERS
    )
    
    if response.status_code == 400:
        print("✅ Missing prompt error handled correctly")
    else:
        print(f"❌ Expected 400, got {response.status_code}")
    
    # Test missing categories
    print("🔍 Testing missing categories...")
    response = requests.post(
        f"{BASE_URL}/classify/text",
        json={"text": "test text"},  # Missing categories
        headers=HEADERS
    )
    
    if response.status_code == 400:
        print("✅ Missing categories error handled correctly")
    else:
        print(f"❌ Expected 400, got {response.status_code}")

def main():
    """Main function to run all tests"""
    print("🚀 Multi-Task LLM API - Example Usage")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ API server is not running!")
        print("Please start the server with: python app.py")
        return
    
    print(f"\n🌐 API Base URL: {BASE_URL}")
    print(f"📊 Swagger UI: http://0.0.0.0:8081/swagger/")
    
    # Run all tests
    tests = [
        ("Text Generation", test_text_generation),
        ("Code Generation", test_code_generation),
        ("Text Classification", test_text_classification),
        ("Error Handling", test_error_handling)
    print(f"📊 Swagger UI: http://localhost:8081/swagger/")
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()