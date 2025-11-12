from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import hashlib
from services.rag_processor import FileProcessor as RAGProcessor
from services.file_processor import FileProcessor as PPTFileProcessor
from services.slide_generator import SlideGenerator
from config import Config

app = Flask(__name__)
CORS(app)

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# Store processor instances per session (in production, use Redis/database)
rag_processors = {}
presentations = {}

# ==================== Health Check ====================
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

# ==================== RAG Endpoints ====================
@app.route('/api/rag/upload', methods=['POST'])
def rag_upload():
    """Upload and process balance sheet and company profile for RAG"""
    try:
        balance_sheet = request.files.get('balance_sheet')
        company_profile = request.files.get('company_profile')  # Optional
        
        if not balance_sheet:
            return jsonify({'error': 'Balance sheet file is required'}), 400
        
        # Check file extension
        ext = balance_sheet.filename.rsplit('.', 1)[1].lower() if '.' in balance_sheet.filename else ''
        if ext not in Config.ALLOWED_EXTENSIONS:
            return jsonify({'error': f'Invalid file type. Allowed: {Config.ALLOWED_EXTENSIONS}'}), 400
        
        # Read file content
        balance_sheet_content = balance_sheet.read().decode('utf-8')
        company_profile_content = None
        
        if company_profile:
            company_profile_content = company_profile.read().decode('utf-8')
        
        # Create processor instance
        processor = RAGProcessor()
        session_id = str(hash(balance_sheet_content + (company_profile_content or '')))
        rag_processors[session_id] = processor
        
        # Process files
        result = processor.process_files(balance_sheet_content, company_profile_content)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'summaries': result['summaries'],
            'sections_count': result['sections_count']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    """Chat with the balance sheet data"""
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')
    chat_history = data.get('chat_history', [])
    
    if not session_id or session_id not in rag_processors:
        return jsonify({'error': 'Invalid session'}), 400
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        processor = rag_processors[session_id]
        result = processor.query(question, chat_history)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'context': result['context']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PPT Endpoints ====================
@app.route('/api/ppt/upload', methods=['POST'])
def ppt_upload():
    """Upload and validate files for PPT generation"""
    try:
        balance_sheet = request.files.get('balance_sheet')
        company_profile = request.files.get('company_profile')
        
        # Validate files
        validation = PPTFileProcessor.validate_files(balance_sheet, company_profile)
        
        if not validation['valid']:
            return jsonify({
                'success': False,
                'errors': validation['errors']
            }), 400
        
        # Process files
        balance_sheet_text, company_profile_text = PPTFileProcessor.process_files(
            balance_sheet, company_profile
        )
        
        # Generate session ID
        session_id = hashlib.md5(
            (balance_sheet_text + company_profile_text).encode()
        ).hexdigest()
        
        # Store data temporarily
        presentations[session_id] = {
            'balance_sheet': balance_sheet_text,
            'company_profile': company_profile_text
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Files uploaded successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ppt/generate', methods=['POST'])
def ppt_generate():
    """Generate PowerPoint presentation"""
    try:
        data = request.json
        session_id = data.get('session_id')
        selected_slides = data.get('slides', [])
        template = data.get('template', 'professional')
        theme = data.get('theme', 'blue')
        
        if not session_id or session_id not in presentations:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 400
        
        if not selected_slides:
            return jsonify({
                'success': False,
                'error': 'No slides selected'
            }), 400
        
        # Get stored data
        session_data = presentations[session_id]
        
        # Generate presentation
        generator = SlideGenerator()
        result = generator.generate_presentation(
            session_data['balance_sheet'],
            session_data['company_profile'],
            selected_slides,
            template,
            theme
        )
        
        # Store result
        presentations[session_id]['result'] = result
        
        return jsonify({
            'success': True,
            'slides': result['slides'],
            'filename': result['filename'],
            'slide_count': result['slide_count']
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ppt/download/<session_id>', methods=['GET'])
def ppt_download(session_id):
    """Download generated presentation"""
    try:
        if session_id not in presentations:
            return jsonify({
                'success': False,
                'error': 'Presentation not found'
            }), 404
        
        result = presentations[session_id].get('result')
        if not result:
            return jsonify({
                'success': False,
                'error': 'Presentation not generated yet'
            }), 400
        
        file_path = result['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=result['filename'],
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ppt/preview/<session_id>', methods=['GET'])
def ppt_preview(session_id):
    """Get slide preview data"""
    try:
        if session_id not in presentations:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        result = presentations[session_id].get('result')
        if not result:
            return jsonify({
                'success': False,
                'error': 'Presentation not generated'
            }), 400
        
        return jsonify({
            'success': True,
            'slides': result['slides']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

