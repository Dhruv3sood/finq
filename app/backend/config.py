import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'text', 'xlsx', 'pdf'}
    
    # LLM Configuration
    SUMMARY_MODEL = 'gpt-3.5-turbo'
    CHAT_MODEL = 'gpt-3.5-turbo'
    EMBEDDING_MODEL = 'text-embedding-ada-002'
    MODEL = 'gpt-3.5-turbo'
    MAX_TOKENS = 800
    TEMPERATURE = 0.7
    
    # RAG Configuration
    TOP_K_RESULTS = 3
    SIMILARITY_THRESHOLD = 0.7
    
    # Presentation Configuration
    SLIDE_WIDTH = 10  # inches
    SLIDE_HEIGHT = 7.5  # inches
    
    # Template Paths
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
    
    # Slide Types
    AVAILABLE_SLIDES = [
        'title', 'executive', 'financials', 'assets',
        'liabilities', 'ratios', 'trends', 'company', 'conclusion'
    ]

