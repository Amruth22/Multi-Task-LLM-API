import unittest
import json
import os
import time
import threading
import requests
from dotenv import load_dotenv
from app import app
from gemini_wrapper import generate_text, generate_code, classify_text

class TestMultiTaskLLMAPI(unittest.TestCase):
    
    server_thread = None
    base_url = "http://localhost:8081/api/v1"
    base_url = "http://0.0.0.0:8080/api/v1"
    
    @classmethod
    def setUpClass(cls):
        """Set up live server and load environment"""
        load_dotenv()
        
        # Start the Flask server in a separate thread
        cls.server_thread = threading.Thread(target=cls._run_server, daemon=True)
        cls.server_thread.start()
        
        # Wait for server to start
        cls._wait_for_server()
        
        print(f"✅ Test server started at {cls.base_url}")
    
    @classmethod
    def _run_server(cls):
        """Run Flask server in thread"""
        try:
            app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False, threaded=True)
        except Exception as e:
                response = requests.get("http://localhost:8081/api/v1/health", timeout=2)
    
    @classmethod
    def _wait_for_server(cls, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://127.0.0.1:8080/api/v1/health", timeout=2)
                if response.status_code == 200:
                    cls.server_started = True
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        
        raise RuntimeError(f"Server failed to start within {timeout} seconds")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        print("\n🧹 Cleaning up test environment...")
        # Note: Server thread will be cleaned up automatically as it's a daemon thread
    
    def test_01_env_api_key_configured(self):
        """Test that the GOOGLE_API_KEY is properly configured in .env"""
        print("\n🔑 Testing API Key Configuration...")
        
        # Check if .env file exists
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        self.assertTrue(os.path.exists(env_file_path), ".env file should exist")
        
        # Check if API key is loaded
        api_key = os.getenv('GOOGLE_API_KEY')
        self.assertIsNotNone(api_key, "GOOGLE_API_KEY should be set in environment")
        self.assertTrue(len(api_key) > 0, "GOOGLE_API_KEY should not be empty")
        self.assertTrue(api_key.startswith('AIza'), "API key should start with 'AIza'")
        
        print(f"✅ API Key configured: {api_key[:10]}...{api_key[-5:]}")
        
    def test_02_flask_app_initialization(self):
        """Test Flask app and extensions initialization"""
        print("\n🚀 Testing Flask App Initialization...")
        
        # Test health endpoint
        response = requests.get(f'{self.base_url}/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('message', data)
        
        print("✅ Flask app initialized successfully")
        print("✅ Health endpoint working")
        
    def test_03_generate_text_endpoint(self):
        """Test the /api/v1/generate/text endpoint"""
        print("\n📝 Testing Text Generation Endpoint...")
        
        payload = {
            "prompt": "Write a one-sentence story about a cat."
        }
        
        response = requests.post(
            f'{self.base_url}/generate/text',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('generated_text', data)
        self.assertIsNotNone(data['generated_text'])
        self.assertTrue(len(data['generated_text']) > 0)
        
        print(f"✅ Text generated: {data['generated_text'][:50]}...")
        
    def test_04_generate_code_endpoint(self):
        """Test the /api/v1/generate/code endpoint"""
        print("\n💻 Testing Code Generation Endpoint...")
        
        payload = {
            "prompt": "Create a simple Python function that adds two numbers"
        }
        
        response = requests.post(
            f'{self.base_url}/generate/code',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('generated_code', data)
        self.assertIsNotNone(data['generated_code'])
        self.assertTrue(len(data['generated_code']) > 0)
        self.assertIn('def', data['generated_code'])  # Should contain a function definition
        
        print(f"✅ Code generated: {data['generated_code'][:50]}...")
        
    def test_05_classify_text_endpoint(self):
        """Test the /api/v1/classify/text endpoint"""
        print("\n🏷️ Testing Text Classification Endpoint...")
        
        payload = {
            "text": "I love this amazing product! It works perfectly.",
            "categories": ["positive", "negative", "neutral"]
        }
        
        response = requests.post(
            f'{self.base_url}/classify/text',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('classification', data)
        self.assertIsNotNone(data['classification'])
        self.assertIn(data['classification'].lower(), ['positive', 'negative', 'neutral'])
        
        print(f"✅ Text classified as: {data['classification']}")
        
    def test_06_endpoint_error_handling(self):
        """Test error handling for missing required fields"""
        print("\n❌ Testing Error Handling...")
        
        # Test missing prompt for text generation
        response = requests.post(
            f'{self.base_url}/generate/text',
            json={},  # Empty payload - missing required 'prompt'
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        # Test missing fields for classification
        response = requests.post(
            f'{self.base_url}/classify/text',
            json={"text": "test"},  # missing 'categories' field
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        
        print("✅ Error handling working correctly")
    
    def test_07_direct_wrapper_functions(self):
        """Test the gemini_wrapper functions directly"""
        print("\n🔧 Testing Wrapper Functions Directly...")
        
        # Test generate_text function
        text_result = generate_text("Say 'test successful' in one sentence.")
        self.assertIsInstance(text_result, str)
        response = requests.get("http://localhost:8081/swagger/")
        print(f"✅ Direct text generation: {text_result[:30]}...")
        
        # Test generate_code function  
        code_result = generate_code("Write a simple hello world function in Python")
        self.assertIsInstance(code_result, str)
        self.assertTrue(len(code_result) > 0)
        self.assertIn('def', code_result.lower())
        print(f"✅ Direct code generation: {code_result[:30]}...")
        
        # Test classify_text function
        classification_result = classify_text("This is great!", ["positive", "negative"])
        self.assertIsInstance(classification_result, str)
        self.assertTrue(len(classification_result) > 0)
        print(f"✅ Direct text classification: {classification_result}")
    
    def test_08_swagger_documentation(self):
        """Test Swagger UI accessibility"""
        print("\n📚 Testing Swagger Documentation...")
        
        # Test swagger endpoint
        response = requests.get("http://127.0.0.1:8080/swagger/")
        self.assertEqual(response.status_code, 200)
        
        # Check if it's HTML content (Swagger UI)
        self.assertIn('text/html', response.headers.get('content-type', ''))
        
        print("✅ Swagger UI accessible at /swagger/")
    
    def test_09_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n⏱️ Testing Rate Limiting...")
    print("📡 Testing against live server: http://localhost:8081")
        # Make multiple rapid requests to test rate limiting
        payload = {"prompt": "Hello"}
        
        # Make several requests quickly
        responses = []
        for i in range(5):
            response = requests.post(
                f'{self.base_url}/generate/text',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
        print("🌐 Live server tested at: http://localhost:8081")
        print("📊 Swagger UI: http://localhost:8081/swagger/")
        
        # All requests should succeed (within rate limit)
        success_count = sum(1 for status in responses if status == 200)
        self.assertGreater(success_count, 0, "At least some requests should succeed")
        
        print(f"✅ Rate limiting test completed - {success_count}/{len(responses)} requests succeeded")

if __name__ == '__main__':
    print("🚀 Starting Multi-Task LLM API Unit Tests...")
    print("📡 Testing against live server: http://0.0.0.0:8080")
    print("🔄 Server will start automatically and run tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMultiTaskLLMAPI)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        print("🌐 Live server tested at: http://0.0.0.0:8080")
        print("📊 Swagger UI: http://0.0.0.0:8080/swagger/")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    print(f"📊 Tests run: {result.testsRun}")
    print("=" * 60)
