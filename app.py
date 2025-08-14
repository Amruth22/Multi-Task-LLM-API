from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os

from gemini_wrapper import generate_text, generate_code, classify_text

app = Flask(__name__)

# Configure CORS
CORS(app, 
     origins=['*'],  # Configure specific origins in production
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With']
)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

api = Api(
    app, 
    version='1.0', 
    title='Multi-Task LLM API',
    description='A Flask API that provides text generation, code generation, and text classification using Google Gemini 2.0 Flash',
    doc='/swagger/',
    prefix='/api/v1'
)

ns_generate = api.namespace('generate', description='Text and code generation operations')
ns_classify = api.namespace('classify', description='Text classification operations')

# API Models for Swagger documentation
text_generation_model = api.model('TextGeneration', {
    'prompt': fields.String(required=True, description='The text prompt for generation', example='Write a short story about a robot')
})

code_generation_model = api.model('CodeGeneration', {
    'prompt': fields.String(required=True, description='The prompt for code generation', example='Create a Python function to calculate fibonacci numbers')
})

text_classification_model = api.model('TextClassification', {
    'text': fields.String(required=True, description='The text to classify', example='This movie was amazing!'),
    'categories': fields.List(fields.String, required=True, description='List of categories to classify into', example=['positive', 'negative', 'neutral'])
})

text_response_model = api.model('TextResponse', {
    'generated_text': fields.String(description='The generated text response')
})

code_response_model = api.model('CodeResponse', {
    'generated_code': fields.String(description='The generated code response')
})

classification_response_model = api.model('ClassificationResponse', {
    'classification': fields.String(description='The classification result')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Health check endpoint
@app.route('/api/v1/health')
def health_check():
    return {'status': 'healthy', 'message': 'Multi-Task LLM API is running'}

@ns_generate.route('/text')
class TextGeneration(Resource):
    @ns_generate.expect(text_generation_model)
    @ns_generate.doc(
        description='Generate text based on a given prompt using Google Gemini 2.0 Flash',
        responses={
            200: ('Success - Text generated', text_response_model),
            400: ('Bad Request - Missing prompt', error_model),
            500: ('Internal Server Error', error_model)
        }
    )
    @limiter.limit("10 per minute")
    def post(self):
        """Generate text based on a prompt"""
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return {'error': 'Prompt is required'}, 400
        
        try:
            text = generate_text(prompt)
            return {'generated_text': text}
            
        except Exception as e:
            return {'error': str(e)}, 500

@ns_generate.route('/code')
class CodeGeneration(Resource):
    @ns_generate.expect(code_generation_model)
    @ns_generate.doc(
        description='Generate code based on a given prompt using Google Gemini 2.0 Flash with optimized settings for code generation',
        responses={
            200: ('Success - Code generated', code_response_model),
            400: ('Bad Request - Missing prompt', error_model),
            500: ('Internal Server Error', error_model)
        }
    )
    @limiter.limit("10 per minute")
    def post(self):
        """Generate code based on a prompt"""
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return {'error': 'Prompt is required'}, 400

        try:
            code = generate_code(prompt)
            return {'generated_code': code}
            
        except Exception as e:
            return {'error': str(e)}, 500

@ns_classify.route('/text')
class TextClassification(Resource):
    @ns_classify.expect(text_classification_model)
    @ns_classify.doc(
        description='Classify text into one of the provided categories using Google Gemini 2.0 Flash',
        responses={
            200: ('Success - Text classified', classification_response_model),
            400: ('Bad Request - Missing text or categories', error_model),
            500: ('Internal Server Error', error_model)
        }
    )
    @limiter.limit("10 per minute")
    def post(self):
        """Classify text into provided categories"""
        data = request.get_json()
        text = data.get('text')
        categories = data.get('categories')

        if not text or not categories:
            return {'error': 'Text and categories are required'}, 400

        try:
            classification = classify_text(text, categories)
            return {'classification': classification}
            
        except Exception as e:
            return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)