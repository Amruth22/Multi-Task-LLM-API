import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom exception for rate limiting
class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    pass

# Custom exception for API errors
class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    pass

def is_rate_limit_error(exception):
    """Detect if the exception is a rate limit error"""
    error_message = str(exception).lower()
    rate_limit_indicators = [
        'rate limit exceeded',
        'quota exceeded',
        'resource exhausted',
        'too many requests',
        '429',
        'rate_limit_exceeded'
    ]
    
    return any(indicator in error_message for indicator in rate_limit_indicators)

def is_retryable_error(exception):
    """Check if an error should trigger a retry"""
    error_message = str(exception).lower()
    retryable_indicators = [
        'rate limit exceeded',
        'quota exceeded', 
        'resource exhausted',
        'too many requests',
        'temporary failure',
        'service unavailable',
        'timeout',
        'connection error',
        '429',
        '500',
        '502',
        '503',
        '504'
    ]
    
    return any(indicator in error_message for indicator in retryable_indicators)

def retry_on_rate_limit(retry_state):
    """Custom retry condition for rate limiting"""
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        return is_retryable_error(exception)
    return False

@retry(
    retry=retry_on_rate_limit,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    reraise=True
)
def generate_text(prompt):
    """
    Generate text using Google Gemini 2.0 Flash with optimized settings for creative content
    
    Args:
        prompt (str): The text prompt for generation
        
    Returns:
        str: Generated text response
        
    Raises:
        GeminiAPIError: If API call fails after retries
        ValueError: If prompt is empty or invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    try:
        # Initialize Gemini model with creative settings
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,  # Creative and varied outputs
            max_tokens=2048,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create message and invoke model
        message = HumanMessage(content=prompt)
        response = llm.invoke([message])
        
        # Extract text content from response
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
    except Exception as e:
        error_msg = str(e)
        if is_rate_limit_error(e):
            raise RateLimitError(f"Rate limit exceeded: {error_msg}")
        else:
            raise GeminiAPIError(f"Gemini API error in text generation: {error_msg}")

@retry(
    retry=retry_on_rate_limit,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    reraise=True
)
def generate_code(prompt):
    """
    Generate code using Google Gemini 2.0 Flash with optimized settings for consistent code output
    
    Args:
        prompt (str): The code generation prompt
        
    Returns:
        str: Generated code response
        
    Raises:
        GeminiAPIError: If API call fails after retries
        ValueError: If prompt is empty or invalid
    """
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string")
    
    try:
        # Initialize Gemini model with consistent settings for code generation
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.2,  # Low temperature for consistent and reliable code
            max_tokens=2048,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Enhanced prompt for better code generation
        enhanced_prompt = f"""
        Generate clean, well-commented, and functional code for the following request:
        
        {prompt}
        
        Please provide:
        1. Working code with proper syntax
        2. Clear variable names and structure
        3. Brief comments where helpful
        4. Example usage if applicable
        
        Code:
        """
        
        # Create message and invoke model
        message = HumanMessage(content=enhanced_prompt)
        response = llm.invoke([message])
        
        # Extract text content from response
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
            
    except Exception as e:
        error_msg = str(e)
        if is_rate_limit_error(e):
            raise RateLimitError(f"Rate limit exceeded: {error_msg}")
        else:
            raise GeminiAPIError(f"Gemini API error in code generation: {error_msg}")

@retry(
    retry=retry_on_rate_limit,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    reraise=True
)
def classify_text(text, categories):
    """
    Classify text into one of the provided categories using Google Gemini 2.0 Flash
    
    Args:
        text (str): The text to classify
        categories (list): List of possible categories
        
    Returns:
        str: The classification result (one of the provided categories)
        
    Raises:
        GeminiAPIError: If API call fails after retries
        ValueError: If text or categories are invalid
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
        
    if not categories or not isinstance(categories, list) or len(categories) == 0:
        raise ValueError("Categories must be a non-empty list")
    
    try:
        # Initialize Gemini model with deterministic settings for classification
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.0,  # Deterministic classification
            max_tokens=50,    # Short response for classification
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Create structured prompt for classification
        categories_str = ", ".join(categories)
        classification_prompt = f"""
        Please classify the following text into exactly one of these categories: {categories_str}
        
        Text to classify: "{text}"
        
        Instructions:
        1. Choose ONLY ONE category from the provided list
        2. Respond with ONLY the category name, nothing else
        3. Do not add explanations or additional text
        4. The response must be one of: {categories_str}
        
        Classification:
        """
        
        # Create message and invoke model
        message = HumanMessage(content=classification_prompt)
        response = llm.invoke([message])
        
        # Extract and clean the response
        if hasattr(response, 'content'):
            result = response.content.strip().lower()
        else:
            result = str(response).strip().lower()
        
        # Validate that the response is one of the provided categories
        categories_lower = [cat.lower() for cat in categories]
        
        # Find the best match
        for category in categories_lower:
            if category in result:
                # Return the original case category
                original_index = categories_lower.index(category)
                return categories[original_index]
        
        # If no exact match, return the first category as fallback
        return categories[0]
        
    except Exception as e:
        error_msg = str(e)
        if is_rate_limit_error(e):
            raise RateLimitError(f"Rate limit exceeded: {error_msg}")
        else:
            raise GeminiAPIError(f"Gemini API error in text classification: {error_msg}")

def test_api_connection():
    """
    Test the connection to Google Gemini API
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Simple test with minimal prompt
        test_response = generate_text("Say 'API connection successful'")
        return len(test_response) > 0
    except Exception as e:
        print(f"API connection test failed: {e}")
        return False

if __name__ == "__main__":
    """
    Test the wrapper functions directly
    """
    print("Testing Gemini Wrapper Functions...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please ensure your .env file contains a valid Google API key")
        exit(1)
    
    if not api_key.startswith('AIza'):
        print("❌ Invalid Google API key format (should start with 'AIza')")
        exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    print()
    
    try:
        # Test text generation
        print("Testing text generation...")
        text_result = generate_text("Write a short sentence about artificial intelligence.")
        print(f"✅ Text Generation: {text_result}")
        print()
        
        # Test code generation
        print("Testing code generation...")
        code_result = generate_code("Create a Python function that calculates the factorial of a number")
        print(f"✅ Code Generation: {code_result[:100]}...")
        print()
        
        # Test text classification
        print("Testing text classification...")
        classification_result = classify_text("This movie is absolutely fantastic!", ["positive", "negative", "neutral"])
        print(f"✅ Text Classification: {classification_result}")
        print()
        
        print("🎉 All wrapper functions working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing wrapper functions: {e}")
        exit(1)