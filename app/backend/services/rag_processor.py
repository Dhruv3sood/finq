from typing import Dict
from utils.parser import BalanceSheetParser
from utils.company_profile_parser import CompanyProfileParser
from .llm_service import LLMService
from .embedding_service import EmbeddingService
from .rag_service import RAGService

class FileProcessor:
    """Main file processing pipeline"""
    
    def __init__(self):
        self.parser = BalanceSheetParser()
        self.company_profile_parser = CompanyProfileParser()
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.rag_service = RAGService(self.embedding_service)
    
    def process_files(self, balance_sheet_content: str, company_profile_content: str = None) -> Dict:
        """
        Process balance sheet and company profile files through complete pipeline
        
        Args:
            balance_sheet_content: Raw balance sheet content
            company_profile_content: Raw company profile content (optional)
            
        Returns:
            Dictionary with processing results
        """
        # Step 1: Parse balance sheet into individual entries
        entries = self.parser.parse(balance_sheet_content)
        
        # Step 2: Parse company profile into meaningful sections (if provided)
        if company_profile_content:
            company_sections = self.company_profile_parser.parse(company_profile_content)
            # Add company profile sections to entries
            entries.extend(company_sections)
        
        if not entries:
            raise ValueError("No entries found in the file. Please check the file format.")
        
        # Step 3: Generate individual summaries for each entry using LLM
        summaries = self.llm_service.generate_summaries(entries)
        
        if not summaries:
            raise ValueError("Failed to generate summaries. Please check your OpenAI API key and file content.")
        
        # Step 4: Create embeddings for each entry's summary
        embedded_summaries = self.embedding_service.create_embeddings(summaries)
        
        # Step 5: Index in RAG system
        self.rag_service.index_documents(embedded_summaries)
        
        return {
            'sections_count': len(entries),  # Keep key name for backward compatibility
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