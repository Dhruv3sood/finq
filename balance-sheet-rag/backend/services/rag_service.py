from typing import List, Dict
from .embedding_service import EmbeddingService
from config import Config

class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.knowledge_base = []
    
    def index_documents(self, embedded_summaries: List[Dict]):
        """Store embedded summaries in the knowledge base"""
        self.knowledge_base = embedded_summaries
    
    def retrieve_relevant_context(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve most relevant context for a query
        
        Args:
            query: User's question
            top_k: Number of results to return
            
        Returns:
            List of relevant context items with similarity scores
        """
        if not self.knowledge_base:
            raise ValueError("Knowledge base is empty. Please upload and process a file first.")
        
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        # Create embedding for query
        query_embedding = self.embedding_service.create_embedding(query)
        
        # Calculate similarities
        results = []
        for item in self.knowledge_base:
            similarity = self.embedding_service.cosine_similarity(
                query_embedding, 
                item['embedding']
            )
            
            results.append({
                'section': item['section'],
                'summary': item['summary'],
                'original_content': item['original_content'],
                'similarity': similarity
            })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def format_context(self, retrieved_items: List[Dict]) -> str:
        """Format retrieved items into a context string"""
        if not retrieved_items:
            return "No relevant context found."
        
        context_parts = []
        
        for item in retrieved_items:
            context_parts.append(
                f"Section: {item['section']}\n"
                f"Summary: {item['summary']}\n"
                f"Details: {item['original_content']}\n"
                f"Relevance: {item['similarity']:.2f}"
            )
        
        return "\n\n".join(context_parts)