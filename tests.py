import unittest
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to Python path to import Project modules (cross-platform)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_dir = os.path.join(parent_dir, 'Project')
sys.path.insert(0, parent_dir)
sys.path.insert(0, project_dir)

class CoreGeminiTests(unittest.TestCase):
    """Core 5 unit tests for Gemini wrapper functions with real API"""
    
    @classmethod
    def setUpClass(cls):
        """Load environment variables and validate API key"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        env_file_path = os.path.join(parent_dir, 'Project', '.env')
        load_dotenv(env_file_path)
        
        # Validate API key
        cls.api_key = os.getenv('GOOGLE_API_KEY')
        if not cls.api_key or not cls.api_key.startswith('AIza'):
            raise unittest.SkipTest("Valid GOOGLE_API_KEY not found in environment")
        
        print(f"Using API Key: {cls.api_key[:10]}...{cls.api_key[-5:]}")

    def test_01_text_generation(self):
        """Test 1: Text generation function"""
        print("Running Test 1: Text generation")
        
        from Project.gemini_wrapper import generate_text
        
        # Test with simple prompt
        result = generate_text("Say hello")
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        print(f"PASS: Generated text: {result[:50]}...")

    def test_02_code_generation(self):
        """Test 2: Code generation function"""
        print("Running Test 2: Code generation")
        
        from Project.gemini_wrapper import generate_code
        
        # Test with code prompt
        result = generate_code("Write a Python function to add two numbers")
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn('def', result.lower())  # Should contain function definition
        
        print("PASS: Code generation contains function definition")

    def test_03_text_classification(self):
        """Test 3: Text classification function"""
        print("Running Test 3: Text classification")
        
        from Project.gemini_wrapper import classify_text
        
        # Test classification
        result = classify_text("Great product!", ["positive", "negative", "neutral"])
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertIn(result, ["positive", "negative", "neutral"])
        
        print(f"PASS: Classified text as: {result}")

    def test_04_rate_limit_detection(self):
        """Test 4: Rate limit error detection (Instant test)"""
        print("Running Test 4: Rate limit error detection")
        
        from Project.gemini_wrapper import is_rate_limit_error, is_retryable_error
        
        # Test rate limit detection functions without making API calls
        rate_limit_messages = [
            "rate limit exceeded",
            "quota exceeded", 
            "resource exhausted",
            "429 error occurred",
            "too many requests"
        ]
        
        retryable_messages = [
            "service unavailable",
            "timeout occurred", 
            "500 internal server error",
            "connection error"
        ]
        
        # Test rate limit detection
        for msg in rate_limit_messages:
            mock_error = Exception(msg)
            self.assertTrue(is_rate_limit_error(mock_error), f"Should detect rate limit: {msg}")
        
        # Test retryable error detection  
        for msg in retryable_messages:
            mock_error = Exception(msg)
            self.assertTrue(is_retryable_error(mock_error), f"Should detect retryable error: {msg}")
        
        # Test non-rate-limit errors
        normal_error = Exception("invalid input")
        self.assertFalse(is_rate_limit_error(normal_error), "Should not detect normal error as rate limit")
        
        print("PASS: Rate limit detection logic working correctly")

    def test_05_api_connection(self):
        """Test 5: API connection test"""
        print("Running Test 5: API connection test")
        
        from Project.gemini_wrapper import test_api_connection
        
        # Test API connection
        result = test_api_connection()
        
        # Should return boolean
        self.assertIsInstance(result, bool)
        
        print(f"PASS: API connection test result: {result}")

def run_core_tests():
    """Run core tests and provide summary"""
    print("=" * 50)
    print("[*] Core Gemini Unit Tests (5 Tests)")
    print("Testing with REAL Gemini API")
    print("=" * 50)
    
    # Check API key
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'Project', '.env'))
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key or not api_key.startswith('AIza'):
        print("[ERROR] Valid GOOGLE_API_KEY not found!")
        return False
    
    print(f"[OK] Using API Key: {api_key[:10]}...{api_key[-5:]}")
    print()
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(CoreGeminiTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("[*] Test Results:")
    print(f"[*] Tests Run: {result.testsRun}")
    print(f"[*] Failures: {len(result.failures)}")
    print(f"[*] Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n[FAILURES]:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n[ERRORS]:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n[SUCCESS] All 5 core tests passed!")
        print("[OK] Gemini wrapper functions working correctly")
    else:
        print(f"\n[WARNING] {len(result.failures) + len(result.errors)} test(s) failed")
    
    return success

if __name__ == "__main__":
    print("[*] Starting Core Gemini Tests")
    print("[*] 5 essential tests with real API")
    print()
    
    success = run_core_tests()
    exit(0 if success else 1)