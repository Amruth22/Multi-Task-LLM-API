#!/usr/bin/env python3
"""
Test Runner for Multi-Task LLM API

This script provides a reliable way to run tests with proper error handling
and Windows compatibility.
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please create a .env file with your GOOGLE_API_KEY")
        print("💡 You can copy .env.example to .env and add your API key")
        return False
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment!")
        print("📝 Please add your Google API key to the .env file")
        return False
    
    if not api_key.startswith('AIza'):
        print("⚠️ API key format looks incorrect (should start with 'AIza')")
        print("🔑 Please verify your Google API key")
        return False
    
    print(f"✅ Environment configured correctly")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        'flask', 'flask-restx', 'flask-limiter', 'flask-cors',
        'python-dotenv', 'tenacity', 'langchain', 'langchain-google-genai',
        'requests', 'unittest'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'unittest':
                import unittest
            elif package == 'flask-restx':
                import flask_restx
            elif package == 'flask-limiter':
                import flask_limiter
            elif package == 'flask-cors':
                import flask_cors
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'langchain-google-genai':
                import langchain_google_genai
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📝 Please install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_direct_wrapper_test():
    """Test the wrapper functions directly (fastest test)"""
    print("\n🧪 Running Direct Wrapper Test...")
    
    try:
        from gemini_wrapper import generate_text
        
        # Quick test
        result = generate_text("Say 'Hello World' in one sentence.")
        if result and len(result) > 0:
            print(f"✅ Direct wrapper test passed: {result[:50]}...")
            return True
        else:
            print("❌ Direct wrapper test failed: Empty response")
            return False
            
    except Exception as e:
        print(f"❌ Direct wrapper test failed: {e}")
        return False

def run_unit_tests():
    """Run the unit tests"""
    print("\n🚀 Running Unit Tests...")
    
    # Try the fixed test file first
    if os.path.exists('test_unit_fixed.py'):
        print("📋 Using Windows-compatible test file...")
        try:
            result = subprocess.run([sys.executable, 'test_unit_fixed.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    # Fallback to original test file
    elif os.path.exists('test_unit.py'):
        print("📋 Using original test file...")
        try:
            result = subprocess.run([sys.executable, 'test_unit.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Tests timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    else:
        print("❌ No test files found!")
        return False

def run_example_usage():
    """Run the example usage script"""
    print("\n📋 Running Example Usage Script...")
    
    if not os.path.exists('example_usage.py'):
        print("❌ example_usage.py not found!")
        return False
    
    # First, start the server
    print("🚀 Starting server for example usage...")
    
    try:
        # Start server in background
        server_process = subprocess.Popen([sys.executable, 'app.py'])
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:8081/api/v1/health', timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully")
                
                # Run example usage
                result = subprocess.run([sys.executable, 'example_usage.py'], 
                                      capture_output=True, text=True, timeout=120)
                
                print("Example Usage Output:")
                print(result.stdout)
                
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                
                success = result.returncode == 0
                
            else:
                print("❌ Server health check failed")
                success = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            success = False
        
        # Clean up server
        server_process.terminate()
        server_process.wait(timeout=10)
        
        return success
        
    except Exception as e:
        print(f"❌ Error running example usage: {e}")
        return False

def main():
    """Main test runner function"""
    print("🚀 Multi-Task LLM API Test Runner")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed!")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        return False
    
    # Run direct wrapper test (fastest)
    if not run_direct_wrapper_test():
        print("\n❌ Direct wrapper test failed!")
        print("🔧 This usually indicates an API key or network issue")
        return False
    
    # Ask user which tests to run
    print("\n🎯 Choose test type:")
    print("1. Unit Tests (comprehensive, starts own server)")
    print("2. Example Usage (requires manually starting server)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    success = True
    
    if choice in ['1', '3']:
        success &= run_unit_tests()
    
    if choice in ['2', '3']:
        if choice == '2':
            print("\n⚠️ Please start the server manually in another terminal:")
            print("   python app.py")
            input("Press Enter when server is running...")
        
        success &= run_example_usage()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)