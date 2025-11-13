"""Agent classes for agentic pipeline"""
from typing import Dict, Any, List, Optional
from services.llm_service import LLMService
from agents.tools import (
    PDFLoaderTool, TextSplitterTool, EmbedderTool, 
    VectorDBTool, ContextCompressorTool, GroundingCheckerTool,
    CompanyProfileParserTool
)
from utils.parser import BalanceSheetParser
from utils.company_profile_parser import CompanyProfileParser
from config import Config
import json


class LoaderAgent:
    """Agent for loading and processing documents"""
    
    def __init__(self, llm_service=None):
        self.pdf_loader = PDFLoaderTool()
        self.text_splitter = TextSplitterTool(
            chunk_size=800,
            chunk_overlap=100
        )
        self.embedder = EmbedderTool()
        self.vector_db = None
        self.balance_sheet_parser = BalanceSheetParser()
        self.company_profile_parser = CompanyProfileParserTool(llm_service=llm_service)
        self.llm_service = llm_service
    
    def process(self, balance_sheet_content: str, company_profile_content: str = None,
                db_name: str = "rag_db", vector_db: VectorDBTool = None) -> Dict[str, Any]:
        """
        Process balance sheet and company profile through ingestion pipeline
        
        Args:
            balance_sheet_content: Balance sheet text content
            company_profile_content: Company profile text content (optional)
            db_name: Name of vector database collection
            vector_db: Optional pre-initialized vector DB instance
            
        Returns:
            Dictionary with processing results
        """
        # Use provided vector DB or create new one
        self.vector_db = vector_db if vector_db else VectorDBTool(db_name=db_name)
        
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        
        # Process balance sheet
        balance_entries = self.balance_sheet_parser.parse(balance_sheet_content)
        for entry in balance_entries:
            content = '\n'.join(entry.get('content', []))
            chunks = self.text_splitter.split(
                content,
                metadata={
                    'section': entry.get('title', 'Balance Sheet Entry'),
                    'type': 'balance_sheet',
                    'source': 'balance_sheet'
                }
            )
            all_chunks.extend(chunks)
        
        # Process company profile with enhanced parser
        company_data = {}
        if company_profile_content:
            parsed_result = self.company_profile_parser.parse(company_profile_content)
            company_data = parsed_result.get('company_data', {})
            company_sections = parsed_result.get('sections', [])
            
            for section in company_sections:
                content = section.get('content', '')
                if content:
                    chunks = self.text_splitter.split(
                        content,
                        metadata={
                            'section': section.get('title', 'Company Section'),
                            'category': section.get('category', 'general'),
                            'type': 'company_profile',
                            'source': 'company_profile'
                        }
                    )
                    all_chunks.extend(chunks)
        
        # Create embeddings for all chunks
        texts = [chunk['text'] for chunk in all_chunks]
        all_embeddings = self.embedder.embed_batch(texts)
        
        # Prepare metadatas
        all_metadatas = [chunk['metadata'] for chunk in all_chunks]
        
        # Store in vector DB
        self.vector_db.store(all_chunks, all_embeddings, all_metadatas)
        
        company_sections_count = len(company_sections) if company_profile_content and 'company_sections' in locals() else 0
        
        return {
            'chunks_count': len(all_chunks),
            'balance_sheet_entries': len(balance_entries),
            'company_profile_sections': company_sections_count,
            'company_data': company_data,
            'db_name': db_name
        }


class QueryRouterAgent:
    """Agent for routing queries to appropriate handlers"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        Determine query type and route accordingly
        
        Args:
            query: User query
            
        Returns:
            Dictionary with route information
        """
        prompt = f"""Analyze the following query and determine its type.
Return ONLY a JSON object with no markdown formatting.

Query: {query}

Return JSON with:
{{
    "type": "factual" | "vague" | "summary",
    "reasoning": "brief explanation",
    "needs_rewrite": true/false
}}

Query types:
- "factual": Specific question about data, numbers, or facts
- "vague": Unclear, ambiguous, or underspecified query
- "summary": Request for overview, summary, or high-level information"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing queries and routing them appropriately. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            # Default to factual
            return {
                "type": "factual",
                "reasoning": "Default routing due to error",
                "needs_rewrite": False
            }


class QueryRewriterAgent:
    """Agent for rewriting vague queries"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def rewrite(self, query: str, context_hint: str = None) -> str:
        """
        Rewrite vague query to be more specific - PRESERVE USER INTENT
        
        Args:
            query: Original vague query
            context_hint: Optional context hint (e.g., company name)
            
        Returns:
            Rewritten query that preserves original intent
        """
        prompt = f"""You are helping to improve a search query for finding information in company documents (financial reports, company profiles, brochures).

CRITICAL: Preserve the EXACT intent and topic of the original query. Only make it clearer for semantic search.

Examples:
- "what does the company do" → "company business activities products services what company does"
- "who are the clients" → "clients customers partners who company works with"
- "what are core values" → "core values company values principles"

Original Query: {query}

Return ONLY the improved query (keep it broad and semantic), no explanation:"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at rewriting queries to be more specific and effective for information retrieval."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return query  # Return original if rewrite fails


class RetrieverAgent:
    """Agent for retrieving relevant context from vector DB"""
    
    def __init__(self, vector_db: VectorDBTool, embedder: EmbedderTool):
        self.vector_db = vector_db
        self.embedder = embedder
    
    def retrieve(self, query: str, k: int = 4, 
                 filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for query
        
        Args:
            query: User query
            k: Number of results to retrieve
            filter_metadata: Optional metadata filters
            
        Returns:
            List of retrieved documents
        """
        query_embedding = self.embedder.embed(query)
        results = self.vector_db.search(query_embedding, k=k, filter_metadata=filter_metadata)
        return results


class ContextCompressorAgent:
    """Agent for compressing retrieved context"""
    
    def __init__(self, llm_service: LLMService):
        self.tool = ContextCompressorTool(llm_service)
    
    def compress(self, retrieved_docs: List[Dict[str, Any]], query: str = None) -> str:
        """
        Compress retrieved context - PRESERVE ALL RELEVANT INFO
        
        Args:
            retrieved_docs: Retrieved documents
            query: Original query
            
        Returns:
            Compressed context string with all relevant information
        """
        # Don't over-compress - preserve important details
        # Just format it nicely, don't lose information
        context_parts = []
        for doc in retrieved_docs:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            section = metadata.get('section', 'Unknown Section')
            doc_type = metadata.get('type', 'unknown')
            
            # Include section info for better context
            context_parts.append(f"[{section} - {doc_type}]\n{text}")
        
        return "\n\n".join(context_parts)


class AnswerAgent:
    """Agent for generating answers"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def generate(self, query: str, context: str, chat_history: List[Dict] = None) -> str:
        """
        Generate answer from context - DYNAMIC and GENERALIZED
        
        Args:
            query: User query
            context: Compressed context
            chat_history: Optional chat history
            
        Returns:
            Generated answer
        """
        system_message = f"""You are an intelligent assistant that answers questions about companies using their financial documents, company profiles, and optionally web search results.

INSTRUCTIONS:
1. Answer the user's question using the provided context
2. The context may contain:
   - Financial data (balance sheets, assets, liabilities, ratios) from uploaded documents
   - Company information (what they do, products, services, history) from uploaded documents
   - Company profile details (mission, vision, values, clients, partnerships, leadership, etc.) from uploaded documents
   - Additional information from web search (if available and marked as such)
3. PRIORITIZE information from uploaded documents over web search results
4. Extract and present relevant information from ANY section that relates to the question
5. If the question is about a specific topic (e.g., clients, values, products), search through ALL context sections
6. Be comprehensive - if multiple sections have relevant info, include it all
7. Cite specific sections when mentioning data
8. If web search information is used, mention it's supplementary information
9. If information isn't in the context, clearly state that

Context (from company documents and optionally web search):
{context}

User Question: {query}

Provide a comprehensive answer using any relevant information from the context above."""
        
        messages = chat_history or []
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    *messages
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"


class GroundingCheckerAgent:
    """Agent for validating answer grounding"""
    
    def __init__(self, llm_service: LLMService):
        self.tool = GroundingCheckerTool(llm_service)
    
    def check(self, answer: str, context: str, query: str) -> Dict[str, Any]:
        """
        Check answer grounding
        
        Args:
            answer: Generated answer
            context: Retrieved context
            query: Original query
            
        Returns:
            Validation result with corrected answer if needed
        """
        return self.tool.check(answer, context, query)


class SummarizerAgent:
    """Agent for generating summaries"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def summarize(self, retrieved_docs: List[Dict[str, Any]], 
                  query: str = None) -> str:
        """
        Generate summary from retrieved documents
        
        Args:
            retrieved_docs: Retrieved documents
            query: Optional query to focus summary
            
        Returns:
            Summary text
        """
        context_text = "\n\n".join([
            f"[{doc.get('metadata', {}).get('section', 'Section')}]\n"
            f"{doc.get('text', '')}"
            for doc in retrieved_docs
        ])
        
        prompt = f"""Generate a comprehensive summary based on the following retrieved documents.
{"Focus on: " + query if query else "Provide a general overview"}

Documents:
{context_text}

Provide a well-structured summary that covers key points:"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating comprehensive summaries from multiple documents."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

