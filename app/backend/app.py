from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import hashlib
import io
import uuid
from services.rag_processor import FileProcessor as RAGProcessor
from services.file_processor import FileProcessor as PPTFileProcessor
from services.slide_generator import SlideGenerator
from agents.pipeline import AgenticPipeline
from config import Config
from utils.pdf_extractor import PDFExtractor

app = Flask(__name__)
CORS(app)

# Ensure output directory exists
os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# Store processor instances per session (in production, use Redis/database)
rag_processors = {}  # Legacy RAG processors (fallback)
agentic_pipelines = {}  # New agentic pipelines
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
        
        # Read file content (handle PDF or text files)
        if PDFExtractor.is_pdf_file(balance_sheet.filename):
            balance_sheet.seek(0)  # Reset file pointer
            balance_sheet_content = PDFExtractor.extract_text(balance_sheet)
        else:
            balance_sheet_content = balance_sheet.read().decode('utf-8')
        
        company_profile_content = None
        if company_profile:
            if PDFExtractor.is_pdf_file(company_profile.filename):
                company_profile.seek(0)  # Reset file pointer
                company_profile_content = PDFExtractor.extract_text(company_profile)
            else:
                company_profile_content = company_profile.read().decode('utf-8')
        
        # Generate session ID
        session_id = str(hash(balance_sheet_content + (company_profile_content or '')))
        
        # Track processing time
        import time
        start_time = time.time()
        
        # Create agentic pipeline instance
        pipeline = AgenticPipeline(db_name=f"rag_db_{session_id}")
        
        # Ingest documents through agentic pipeline
        result = pipeline.ingest(balance_sheet_content, company_profile_content)
        
        # Store pipeline instance
        agentic_pipelines[session_id] = pipeline
        
        # Also keep legacy processor for backward compatibility
        processor = RAGProcessor()
        rag_processors[session_id] = processor
        processor.process_files(balance_sheet_content, company_profile_content)
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'chunks_count': result.get('chunks_count', 0),
            'balance_sheet_entries': result.get('balance_sheet_entries', 0),
            'company_profile_sections': result.get('company_profile_sections', 0),
            'processing_time': processing_time,
            'message': 'Documents ingested successfully using agentic pipeline',
            'ready_for_chat': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    """Chat with the balance sheet data using agentic pipeline"""
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')
    chat_history = data.get('chat_history', [])
    
    if not session_id:
        return jsonify({'error': 'Invalid session'}), 400
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # Try agentic pipeline first
        if session_id in agentic_pipelines:
            pipeline = agentic_pipelines[session_id]
            result = pipeline.query(question, chat_history)
            
            return jsonify({
                'success': True,
                'answer': result['answer'],
                'context': result.get('compressed_context', ''),
                'citations': result.get('citations', []),
                'route_info': result.get('route_info', {}),
                'grounding_check': result.get('grounding_check', {}),
                'pipeline': 'agentic',
                'query_used': result.get('query_used'),
                'web_search_used': result.get('web_search_used', False),
                'doc_analysis_used': result.get('doc_analysis_used', False)
            })
        # Fallback to legacy processor
        elif session_id in rag_processors:
        processor = rag_processors[session_id]
        result = processor.query(question, chat_history)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
                'context': result['context'],
                'method': 'legacy'
        })
        else:
            return jsonify({'error': 'Invalid session. Please upload files first.'}), 400
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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
        
        # Process files (handle PDF or text files)
        balance_sheet_text = None
        company_profile_text = None
        
        # Extract balance sheet content
        if PDFExtractor.is_pdf_file(balance_sheet.filename):
            balance_sheet.seek(0)  # Reset file pointer
            balance_sheet_text = PDFExtractor.extract_text(balance_sheet)
        else:
            balance_sheet_text = balance_sheet.read().decode('utf-8')
        
        # Extract company profile content
        if PDFExtractor.is_pdf_file(company_profile.filename):
            company_profile.seek(0)  # Reset file pointer
            company_profile_text = PDFExtractor.extract_text(company_profile)
        else:
            company_profile_text = company_profile.read().decode('utf-8')
        
        # Generate session ID
        session_id = hashlib.md5(
            (balance_sheet_text + company_profile_text).encode()
        ).hexdigest()
        
        # Also ingest into agentic pipeline for enhanced context
        try:
            pipeline = AgenticPipeline(db_name=f"ppt_rag_db_{session_id}")
            pipeline.ingest(balance_sheet_text, company_profile_text)
            agentic_pipelines[session_id] = pipeline
        except Exception as e:
            print(f"Warning: Could not create agentic pipeline: {e}")
        
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
        
        # Get RAG pipeline if available for enhanced context
        rag_pipeline = agentic_pipelines.get(session_id)
        
        # Generate presentation with agentic pipeline
        from agents.ppt_pipeline import PPTAgenticPipeline
        ppt_pipeline = PPTAgenticPipeline(rag_pipeline=rag_pipeline)
        
        result = ppt_pipeline.generate_presentation(
            balance_sheet_text=session_data['balance_sheet'],
            company_profile_text=session_data['company_profile'],
            selected_slides=selected_slides,
            template=template,
            theme=theme,
            use_enhanced_context=bool(rag_pipeline)
        )
        
        # Optimize slide order
        slides = result['slides']
        slides = ppt_pipeline.optimize_slide_order(slides)
        
        # Generate executive brief
        executive_brief = ppt_pipeline.generate_executive_brief(slides)
        
        # Build PowerPoint file
        from services.pptx_builder import PPTXBuilder
        pptx_builder = PPTXBuilder(theme=theme)
        output_filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        
        file_path = pptx_builder.create_presentation(slides, output_path)
        
        result = {
            'slides': slides,
            'file_path': file_path,
            'filename': output_filename,
            'slide_count': len(slides),
            'metadata': result.get('metadata', {}),
            'executive_brief': executive_brief,
            'generation_method': 'agentic'
        }
        
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

@app.route('/api/ppt/recommendations/<session_id>', methods=['GET'])
def ppt_recommendations(session_id):
    """Get AI-powered slide recommendations"""
    try:
        if session_id not in presentations:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        session_data = presentations[session_id]
        
        # Use agentic pipeline for recommendations
        from agents.ppt_pipeline import PPTAgenticPipeline
        rag_pipeline = agentic_pipelines.get(session_id)
        ppt_pipeline = PPTAgenticPipeline(rag_pipeline=rag_pipeline)
        
        recommendations = ppt_pipeline.get_slide_recommendations(
            session_data['balance_sheet'],
            session_data['company_profile']
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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

