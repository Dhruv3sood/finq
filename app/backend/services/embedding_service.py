from openai import OpenAI
import numpy as np
from typing import List, Dict
from config import Config

class EmbeddingService:
    """Service for creating and managing embeddings"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file.")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create an embedding for a piece of text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=Config.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error creating embedding: {str(e)}")
    
    def create_embeddings(self, summaries: List[Dict]) -> List[Dict]:
        """
        Create embeddings for all summaries
        
        Args:
            summaries: List of summary dictionaries
            
        Returns:
            Summaries with embeddings added
        """
        embedded_data = []
        
        for summary in summaries:
            embedding = self.create_embedding(summary['summary'])
            
            embedded_data.append({
                'section': summary['section'],
                'summary': summary['summary'],
                'original_content': summary['original_content'],
                'embedding': embedding
            })
        
        return embedded_data
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)