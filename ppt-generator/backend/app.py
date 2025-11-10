from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from services.file_processor import FileProcessor
from services.slide_generator import SlideGenerator
from config import Config

app = Flask(__name__)
CORS(app)

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# Store generated presentations (in production, use database)
presentations = {}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload and validate files"""
    try:
        balance_sheet = request.files.get('balance_sheet')
        company_profile = request.files.get('company_profile')
        
        # Validate files
        validation = FileProcessor.validate_files(balance_sheet, company_profile)
        
        if not validation['valid']:
            return jsonify({
                'success': False,
                'errors': validation['errors']
            }), 400
        
        # Process files
        balance_sheet_text, company_profile_text = FileProcessor.process_files(
            balance_sheet, company_profile
        )
        
        # Generate session ID
        import hashlib
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

@app.route('/api/generate', methods=['POST'])
def generate_presentation():
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

@app.route('/api/download/<session_id>', methods=['GET'])
def download_presentation(session_id):
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

@app.route('/api/preview/<session_id>', methods=['GET'])
def preview_slides(session_id):
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
    app.run(debug=True, port=5001)