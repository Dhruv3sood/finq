import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'text'}
    
    # LLM Configuration
    SUMMARY_MODEL = 'gpt-3.5-turbo'
    CHAT_MODEL = 'gpt-3.5-turbo'
    EMBEDDING_MODEL = 'text-embedding-ada-002'
    
    # RAG Configuration
    TOP_K_RESULTS = 3
    SIMILARITY_THRESHOLD = 0.7