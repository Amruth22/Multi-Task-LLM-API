# 🚀 Multi-Task LLM API Features

This document outlines the features and capabilities of the simplified Multi-Task LLM API.

## 🎯 Core Features

### 1. Multi-Task AI Capabilities
- **📝 Text Generation**: Creative writing, summaries, content creation
- **💻 Code Generation**: Programming assistance with optimized settings
- **🏷️ Text Classification**: Categorize text into custom categories

### 2. API Design
- **🔄 RESTful API**: Clean REST endpoints with proper HTTP methods
- **📊 Swagger UI**: Interactive API documentation at `/swagger/`
- **🏥 Health Check**: Monitor API status at `/health`
- **🌐 CORS Support**: Cross-origin resource sharing enabled

### 3. Rate Limiting & Security
- **⚡ Smart Rate Limiting**: 200/day, 50/hour, 10/minute per endpoint
- **🔐 Environment Configuration**: Secure API key management
- **🛡️ Input Validation**: Proper request validation and error handling

### 4. Reliability Features
- **🔄 Exponential Backoff**: Intelligent retry logic for API failures
- **⚠️ Error Handling**: Graceful error responses with proper HTTP codes
- **📡 Rate Limit Detection**: Automatic handling of Gemini API limits

## 🏗️ Technical Architecture

### Model Configuration
| Task | Model | Temperature | Purpose |
|------|-------|-------------|---------|
| Text Generation | Gemini 2.0 Flash | 0.7 | Creative and varied outputs |
| Code Generation | Gemini 2.0 Flash | 0.2 | Consistent and reliable code |
| Text Classification | Gemini 2.0 Flash | 0.0 | Deterministic classification |

### API Endpoints

#### Text Generation
```http
POST /api/v1/generate/text
{
  "prompt": "Your text prompt here"
}
```

#### Code Generation
```http
POST /api/v1/generate/code
{
  "prompt": "Your code request here"
}
```

#### Text Classification
```http
POST /api/v1/classify/text
{
  "text": "Text to classify",
  "categories": ["category1", "category2", "category3"]
}
```

#### Health Check
```http
GET /api/v1/health
```

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite
- ✅ **Environment Configuration**: API key validation
- ✅ **Flask App Initialization**: Server startup and health checks
- ✅ **Endpoint Functionality**: All three AI capabilities
- ✅ **Error Handling**: Missing fields and invalid requests
- ✅ **Rate Limiting**: Request throttling functionality
- ✅ **Direct Function Testing**: Wrapper function validation
- ✅ **Swagger UI**: Documentation accessibility
- ✅ **Integration Testing**: End-to-end API testing

### Example Usage Script
- 📋 **Automated Testing**: `example_usage.py` for quick validation
- 🔍 **Error Scenarios**: Tests invalid requests and error handling
- 📊 **Performance Monitoring**: Response time and success rate tracking

## 🚀 Deployment Options

### Development
```bash
python app.py
# Runs on http://0.0.0.0:8080
```

### Production
```bash
waitress-serve --host=0.0.0.0 --port=8080 app:app
# Production WSGI server with better performance
```

## 📦 Dependencies

### Core Framework
- **Flask**: Web framework
- **Flask-RESTX**: Swagger UI and API documentation
- **Flask-Limiter**: Rate limiting functionality
- **Flask-CORS**: Cross-origin resource sharing

### AI Integration
- **LangChain**: LLM framework and utilities
- **langchain-google-genai**: Google Gemini integration
- **tenacity**: Retry logic and exponential backoff

### Configuration & Utilities
- **python-dotenv**: Environment variable management
- **waitress**: Production WSGI server

## 🔧 Configuration

### Environment Variables
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Rate Limits
- **Daily**: 200 requests per day
- **Hourly**: 50 requests per hour  
- **Per Minute**: 10 requests per minute per endpoint

### Retry Configuration
- **Max Retries**: 5 attempts
- **Initial Delay**: 1 second
- **Max Delay**: 60 seconds
- **Strategy**: Exponential backoff

## 📊 API Response Format

### Success Response
```json
{
  "generated_text": "Generated content here...",
  "generated_code": "def example():\n    pass",
  "classification": "positive"
}
```

### Error Response
```json
{
  "error": "Descriptive error message"
}
```

## 🎯 Use Cases

### Text Generation
- **Content Creation**: Blog posts, articles, creative writing
- **Summarization**: Document and text summarization
- **Creative Writing**: Stories, poems, creative content

### Code Generation
- **Function Creation**: Generate specific functions
- **Code Examples**: Create code snippets and examples
- **Algorithm Implementation**: Implement algorithms and data structures

### Text Classification
- **Sentiment Analysis**: Positive, negative, neutral classification
- **Content Categorization**: Topic classification
- **Intent Recognition**: User intent classification

## 🔮 Future Enhancements

While this is the simplified version, potential enhancements could include:

- **Authentication**: User authentication and API keys
- **Usage Analytics**: Request tracking and usage statistics
- **Caching**: Response caching for improved performance
- **Database Integration**: Persistent storage for requests/responses
- **Multi-Model Support**: Support for additional AI models
- **Batch Processing**: Handle multiple requests in a single call

## 📞 Getting Started

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Configure environment**: Create `.env` with your Google API key
4. **Run the server**: `python app.py`
5. **Test the API**: Use `python example_usage.py`
6. **Explore documentation**: Visit `http://0.0.0.0:8080/swagger/`

## 🤝 Contributing

This simplified API provides a clean foundation for:
- **Learning**: Understanding LLM API development
- **Prototyping**: Quick AI application development
- **Extension**: Building more complex features on top
- **Integration**: Embedding AI capabilities in existing applications

The codebase is designed to be readable, maintainable, and easily extensible for future enhancements.