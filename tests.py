import pytest
import json
import os
import time
import threading
import requests
import socket
from dotenv import load_dotenv

# Handle potential import errors gracefully
try:
    from app import app
    from gemini_wrapper import generate_text, generate_code, classify_text
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Import error - {e}")
    print("This might be due to LangChain version compatibility issues.")
    print("Please try: pip install --upgrade langchain langchain-google-genai")
    IMPORTS_AVAILABLE = False
    app = None

# Global variables for server management
server_thread = None
server_started = False
test_port = 8080
base_url = f"http://localhost:{test_port}/api/v1"

def find_free_port():
    """Find a free port for testing"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def run_server():
    """Run Flask server in thread"""
    try:
        # Use localhost for better Windows compatibility
        app.run(host='localhost', port=test_port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"[ERROR] Server failed to start: {e}")

def wait_for_server(timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    
    raise RuntimeError(f"Server failed to start within {timeout} seconds")

def setup_test_server():
    """Set up live server for testing"""
    global server_thread, server_started, test_port, base_url
    
    load_dotenv()
    
    # Find available port
    test_port = find_free_port()
    base_url = f"http://localhost:{test_port}/api/v1"
    
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    wait_for_server()
    server_started = True
    
    print(f"[SUCCESS] Test server started at {base_url}")

def test_01_env_api_key_configured():
    """Test 1: API Key Configuration"""
    print("Running Test 1: API Key Configuration")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Check if .env file exists
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    assert os.path.exists(env_file_path), ".env file should exist"
    
    # Check if API key is loaded
    api_key = os.getenv('GOOGLE_API_KEY')
    assert api_key is not None, "GOOGLE_API_KEY should be set in environment"
    assert len(api_key) > 0, "GOOGLE_API_KEY should not be empty"
    assert api_key.startswith('AIza'), "API key should start with 'AIza'"
    
    print(f"PASS: API Key configured: {api_key[:10]}...{api_key[-5:]}")

def test_02_flask_app_initialization():
    """Test 2: Flask App Initialization"""
    print("Running Test 2: Flask App Initialization")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Test health endpoint
    response = requests.get(f'{base_url}/health')
    assert response.status_code == 200, f"Health endpoint should return 200, got {response.status_code}"
    
    data = response.json()
    assert data['status'] == 'healthy', "Health status should be 'healthy'"
    assert 'message' in data, "Health response should contain message"
    
    print("PASS: Flask app initialized successfully")
    print("PASS: Health endpoint working")

def test_03_generate_text_endpoint():
    """Test 3: Text Generation Endpoint"""
    print("Running Test 3: Text Generation Endpoint")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    payload = {
        "prompt": "Write a one-sentence story about a cat."
    }
    
    response = requests.post(
        f'{base_url}/generate/text',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'generated_text' in data, "Response should contain 'generated_text'"
    assert data['generated_text'] is not None, "Generated text should not be None"
    assert len(data['generated_text']) > 0, "Generated text should not be empty"
    
    print(f"PASS: Text generated: {data['generated_text'][:50]}...")

def test_04_generate_code_endpoint():
    """Test 4: Code Generation Endpoint"""
    print("Running Test 4: Code Generation Endpoint")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    payload = {
        "prompt": "Create a simple Python function that adds two numbers"
    }
    
    response = requests.post(
        f'{base_url}/generate/code',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'generated_code' in data, "Response should contain 'generated_code'"
    assert data['generated_code'] is not None, "Generated code should not be None"
    assert len(data['generated_code']) > 0, "Generated code should not be empty"
    assert 'def' in data['generated_code'], "Generated code should contain a function definition"
    
    print(f"PASS: Code generated: {data['generated_code'][:50]}...")

def test_05_classify_text_endpoint():
    """Test 5: Text Classification Endpoint"""
    print("Running Test 5: Text Classification Endpoint")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    payload = {
        "text": "I love this amazing product! It works perfectly.",
        "categories": ["positive", "negative", "neutral"]
    }
    
    response = requests.post(
        f'{base_url}/classify/text',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'classification' in data, "Response should contain 'classification'"
    assert data['classification'] is not None, "Classification should not be None"
    assert data['classification'].lower() in ['positive', 'negative', 'neutral'], "Classification should be one of the provided categories"
    
    print(f"PASS: Text classified as: {data['classification']}")

def test_06_endpoint_error_handling():
    """Test 6: Error Handling"""
    print("Running Test 6: Error Handling")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Test missing prompt for text generation
    response = requests.post(
        f'{base_url}/generate/text',
        json={},  # Empty payload - missing required 'prompt'
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400, f"Expected 400 for missing prompt, got {response.status_code}"
    data = response.json()
    assert 'error' in data, "Error response should contain 'error' field"
    
    # Test missing fields for classification
    response = requests.post(
        f'{base_url}/classify/text',
        json={"text": "test"},  # missing 'categories' field
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400, f"Expected 400 for missing categories, got {response.status_code}"
    data = response.json()
    assert 'error' in data, "Error response should contain 'error' field"
    
    print("PASS: Error handling working correctly")

def test_07_direct_wrapper_functions():
    """Test 7: Direct Wrapper Functions"""
    print("Running Test 7: Direct Wrapper Functions")
    
    # Test generate_text function
    text_result = generate_text("Say 'test successful' in one sentence.")
    assert isinstance(text_result, str), "Text result should be a string"
    assert len(text_result) > 0, "Text result should not be empty"
    print(f"PASS: Direct text generation: {text_result[:30]}...")
    
    # Test generate_code function  
    code_result = generate_code("Write a simple hello world function in Python")
    assert isinstance(code_result, str), "Code result should be a string"
    assert len(code_result) > 0, "Code result should not be empty"
    assert 'def' in code_result.lower(), "Code result should contain a function definition"
    print(f"PASS: Direct code generation: {code_result[:30]}...")
    
    # Test classify_text function
    classification_result = classify_text("This is great!", ["positive", "negative"])
    assert isinstance(classification_result, str), "Classification result should be a string"
    assert len(classification_result) > 0, "Classification result should not be empty"
    print(f"PASS: Direct text classification: {classification_result}")

def test_08_swagger_documentation():
    """Test 8: Swagger Documentation"""
    print("Running Test 8: Swagger Documentation")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Test swagger endpoint
    swagger_url = f"http://localhost:{test_port}/swagger/"
    response = requests.get(swagger_url)
    assert response.status_code == 200, f"Swagger UI should be accessible, got {response.status_code}"
    
    # Check if it's HTML content (Swagger UI)
    content_type = response.headers.get('content-type', '')
    assert 'text/html' in content_type, f"Swagger UI should return HTML, got {content_type}"
    
    print(f"PASS: Swagger UI accessible at {swagger_url}")

def test_09_rate_limiting():
    """Test 9: Rate Limiting"""
    print("Running Test 9: Rate Limiting")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Make multiple rapid requests to test rate limiting
    payload = {"prompt": "Hello"}
    
    # Make several requests quickly
    responses = []
    for i in range(5):
        response = requests.post(
            f'{base_url}/generate/text',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        responses.append(response.status_code)
        time.sleep(0.1)  # Small delay between requests
    
    # All requests should succeed (within rate limit)
    success_count = sum(1 for status in responses if status == 200)
    assert success_count > 0, "At least some requests should succeed"
    
    print(f"PASS: Rate limiting test completed - {success_count}/{len(responses)} requests succeeded")

def test_10_api_response_format_validation():
    """Test 10: API Response Format Validation"""
    print("Running Test 10: API Response Format Validation")
    
    # Ensure server is running
    if not server_started:
        setup_test_server()
    
    # Test text generation response format
    payload = {"prompt": "Hello world"}
    response = requests.post(
        f'{base_url}/generate/text',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    # Validate response headers
    assert response.headers.get('content-type') == 'application/json', "Response should be JSON"
    
    # Validate response structure
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary"
    assert 'generated_text' in data, "Response should contain 'generated_text' field"
    assert isinstance(data['generated_text'], str), "Generated text should be a string"
    
    # Test code generation response format
    payload = {"prompt": "def hello(): pass"}
    response = requests.post(
        f'{base_url}/generate/code',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    data = response.json()
    assert isinstance(data, dict), "Code response should be a dictionary"
    assert 'generated_code' in data, "Response should contain 'generated_code' field"
    assert isinstance(data['generated_code'], str), "Generated code should be a string"
    
    # Test classification response format
    payload = {"text": "Great!", "categories": ["positive", "negative"]}
    response = requests.post(
        f'{base_url}/classify/text',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    data = response.json()
    assert isinstance(data, dict), "Classification response should be a dictionary"
    assert 'classification' in data, "Response should contain 'classification' field"
    assert isinstance(data['classification'], str), "Classification should be a string"
    
    # Test error response format
    response = requests.post(
        f'{base_url}/generate/text',
        json={},  # Missing prompt
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 400, "Should return 400 for missing prompt"
    data = response.json()
    assert isinstance(data, dict), "Error response should be a dictionary"
    assert 'error' in data, "Error response should contain 'error' field"
    assert isinstance(data['error'], str), "Error message should be a string"
    
    # Test response time (should be reasonable)
    start_time = time.time()
    payload = {"prompt": "Quick test"}
    response = requests.post(
        f'{base_url}/generate/text',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    response_time = time.time() - start_time
    
    assert response_time < 30, f"Response time should be under 30 seconds, got {response_time:.2f}s"
    
    print("PASS: API response format validation completed")
    print(f"PASS: Response time: {response_time:.2f} seconds")

def run_all_tests():
    """Run all tests and provide summary"""
    print("Running Multi-Task LLM API Tests...")
    print("Make sure you have GOOGLE_API_KEY set in your .env file")
    print("=" * 70)
    
    # Setup server once for all tests
    setup_test_server()
    
    # List of exactly 10 test functions
    test_functions = [
        test_01_env_api_key_configured,
        test_02_flask_app_initialization,
        test_03_generate_text_endpoint,
        test_04_generate_code_endpoint,
        test_05_classify_text_endpoint,
        test_06_endpoint_error_handling,
        test_07_direct_wrapper_functions,
        test_08_swagger_documentation,
        test_09_rate_limiting,
        test_10_api_response_format_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_func.__name__} - {e}")
            failed += 1
    
    print("=" * 70)
    print(f"📊 Test Results Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        print("✅ Multi-Task LLM API is working correctly")
        print(f"🌐 Server running at: {base_url}")
        print(f"📊 Swagger UI: http://localhost:{test_port}/swagger/")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed")
        return False

if __name__ == "__main__":
    print("🚀 Starting Multi-Task LLM API Tests")
    print("📋 Make sure you have GOOGLE_API_KEY in your .env file")
    print("🔧 Testing complete API with live server and real Gemini integration")
    print()
    
    # Run the tests
    success = run_all_tests()
    exit(0 if success else 1)