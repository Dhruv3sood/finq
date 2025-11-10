from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from services.file_processor import FileProcessor
from config import Config

app = Flask(__name__)
CORS(app)

# Store processor instances per session (in production, use Redis/database)
processors = {}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process balance sheet file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Check file extension
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'error': f'Invalid file type. Allowed: {Config.ALLOWED_EXTENSIONS}'}), 400
    
    try:
        # Read file content
        content = file.read().decode('utf-8')
        
        # Create processor instance
        processor = FileProcessor()
        session_id = str(hash(content))  # Simple session ID
        processors[session_id] = processor
        
        # Process file
        result = processor.process_file(content)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'summaries': result['summaries'],
            'sections_count': result['sections_count']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with the balance sheet data"""
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')
    chat_history = data.get('chat_history', [])
    
    if not session_id or session_id not in processors:
        return jsonify({'error': 'Invalid session'}), 400
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        processor = processors[session_id]
        result = processor.query(question, chat_history)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'context': result['context']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)