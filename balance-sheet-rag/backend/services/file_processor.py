from typing import Dict
from utils.parser import BalanceSheetParser
from .llm_service import LLMService
from .embedding_service import EmbeddingService
from .rag_service import RAGService

class FileProcessor:
    """Main file processing pipeline"""
    
    def __init__(self):
        self.parser = BalanceSheetParser()
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.rag_service = RAGService(self.embedding_service)
    
    def process_file(self, file_content: str) -> Dict:
        """
        Process balance sheet file through complete pipeline
        
        Args:
            file_content: Raw file content
            
        Returns:
            Dictionary with processing results
        """
        # Step 1: Parse balance sheet into sections
        sections = self.parser.parse(file_content)
        
        if not sections:
            raise ValueError("No sections found in the file. Please check the file format.")
        
        # Step 2: Generate summaries using LLM
        summaries = self.llm_service.generate_summaries(sections)
        
        if not summaries:
            raise ValueError("Failed to generate summaries. Please check your OpenAI API key and file content.")
        
        # Step 3: Create embeddings
        embedded_summaries = self.embedding_service.create_embeddings(summaries)
        
        # Step 4: Index in RAG system
        self.rag_service.index_documents(embedded_summaries)
        
        return {
            'sections_count': len(sections),
            'summaries': summaries,
            'embedded_data': embedded_summaries
        }
    
    def query(self, question: str, chat_history: list = None) -> Dict:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            chat_history: Previous chat messages
            
        Returns:
            Answer and relevant context
        """
        # Retrieve relevant context
        relevant_context = self.rag_service.retrieve_relevant_context(question)
        context_text = self.rag_service.format_context(relevant_context)
        
        # Generate answer
        messages = chat_history or []
        messages.append({"role": "user", "content": question})
        
        answer = self.llm_service.chat(messages, context_text)
        
        return {
            'answer': answer,
            'context': relevant_context
        }