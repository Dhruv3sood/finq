"""Agentic pipeline orchestrator"""
from typing import Dict, Any, List, Optional
from agents.agents import (
    LoaderAgent, QueryRouterAgent, QueryRewriterAgent, RetrieverAgent,
    ContextCompressorAgent, AnswerAgent, GroundingCheckerAgent, SummarizerAgent
)
from agents.tools import EmbedderTool, VectorDBTool, WebSearchTool, DocumentAnalysisTool
from services.llm_service import LLMService
from config import Config


class AgenticPipeline:
    """Orchestrates the agentic pipeline for RAG and PPT generation"""
    
    def __init__(self, db_name: str = "rag_db", enable_web_search: bool = True):
        self.db_name = db_name
        self.llm_service = LLMService()
        self.embedder = EmbedderTool()
        self.enable_web_search = enable_web_search
        
        # Initialize web search tool (optional)
        self.web_search = WebSearchTool(use_duckduckgo=True, use_google=False) if enable_web_search else None
        
        # Initialize document analysis tool for full document analysis
        self.doc_analyzer = DocumentAnalysisTool(self.llm_service)
        
        # Initialize agents (pass LLM service to loader for enhanced parsing)
        self.loader_agent = LoaderAgent(llm_service=self.llm_service)
        self.query_router = QueryRouterAgent(self.llm_service)
        self.query_rewriter = QueryRewriterAgent(self.llm_service)
        self.context_compressor = ContextCompressorAgent(self.llm_service)
        self.answer_agent = AnswerAgent(self.llm_service)
        self.grounding_checker = GroundingCheckerAgent(self.llm_service)
        self.summarizer_agent = SummarizerAgent(self.llm_service)
        
        # Vector DB will be initialized during ingestion
        self.vector_db = None
        
        # Store original documents for full document analysis fallback
        self.original_balance_sheet = None
        self.original_company_profile = None
        self.retriever_agent = None
        self.company_data = None  # Store parsed company data
    
    def ingest(self, balance_sheet_content: str, company_profile_content: str = None) -> Dict[str, Any]:
        """
        Ingest balance sheet and company profile data
        
        Args:
            balance_sheet_content: Balance sheet text content
            company_profile_content: Company profile text content (optional)
            
        Returns:
            Dictionary with ingestion results
        """
        # Initialize vector DB FIRST (before loader uses it)
        self.vector_db = VectorDBTool(db_name=self.db_name)
        
        # Pass the vector_db to loader so it uses the SAME instance
        result = self.loader_agent.process(
            balance_sheet_content,
            company_profile_content,
            vector_db=self.vector_db  # Pass the same instance!
        )
        
        # Store company data for PPT generation
        self.company_data = result.get('company_data', {})
        
        # Store original documents for full document analysis fallback
        self.original_balance_sheet = balance_sheet_content
        self.original_company_profile = company_profile_content
        
        # Initialize retriever with the SAME vector DB instance
        self.retriever_agent = RetrieverAgent(self.vector_db, self.embedder)
        
        return result
    
    def query(self, user_query: str, chat_history: List[Dict] = None, 
              k: int = 4) -> Dict[str, Any]:
        """
        Process user query through agentic pipeline
        
        Args:
            user_query: User's question
            chat_history: Optional chat history
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        if not self.retriever_agent:
            raise ValueError("Pipeline not initialized. Please run ingest() first.")
        
        # Step 1: Route query
        route_info = self.query_router.route(user_query)
        query_type = route_info.get('type', 'factual')
        needs_rewrite = route_info.get('needs_rewrite', False)
        
        # Step 2: Rewrite if needed (but preserve original intent)
        effective_query = user_query
        if needs_rewrite or query_type == 'vague':
            effective_query = self.query_rewriter.rewrite(user_query)
        
        # Step 3: Retrieve context - use BOTH original and rewritten query for better coverage
        # Retrieve with higher k and use both queries for comprehensive coverage
        retrieved_docs_1 = self.retriever_agent.retrieve(effective_query, k=k*3)
        retrieved_docs_2 = self.retriever_agent.retrieve(user_query, k=k*2) if effective_query != user_query else []
        
        # Combine and deduplicate by text content (keep highest scoring version)
        all_docs = {}
        for doc in retrieved_docs_1 + retrieved_docs_2:
            text_key = doc.get('text', '')[:100]  # Use first 100 chars as key
            if text_key not in all_docs or doc.get('score', 0) > all_docs[text_key].get('score', 0):
                all_docs[text_key] = doc
        
        retrieved_docs = sorted(all_docs.values(), key=lambda x: x.get('score', 0), reverse=True)[:k*2]
        
        # Check if we have sufficient context
        has_sufficient_context = len(retrieved_docs) > 0 and any(
            doc.get('score', 0) > 0.5 for doc in retrieved_docs[:3]
        )
        
        # Use web search if context is insufficient and web search is enabled
        web_context = ""
        web_used = False
        if not has_sufficient_context and self.enable_web_search and self.web_search:
            try:
                # Search web for additional context
                web_context = self.web_search.search_and_summarize(user_query, max_results=3)
                web_used = bool(web_context)
            except Exception as e:
                print(f"Web search failed: {e}")
        
        if not retrieved_docs and not web_context:
            return {
                'answer': "I couldn't find relevant information to answer your question in the uploaded documents or through web search. Please try re-uploading your files or rephrasing your question.",
                'context': [],
                'route_info': route_info,
                'citations': [],
                'web_search_used': False
            }
        
        # Step 4: Process based on query type
        if query_type == 'summary':
            # Use summarizer agent
            answer = self.summarizer_agent.summarize(retrieved_docs, user_query)
            context_text = "\n\n".join([doc.get('text', '') for doc in retrieved_docs])
        else:
            # Step 4a: Compress context
            context_text = self.context_compressor.compress(retrieved_docs, effective_query)
            
            # Add web context if available
            if web_context:
                context_text += f"\n\n[Additional Information from Web Search]\n{web_context}"
            
            # Step 4b: Generate answer
            answer = self.answer_agent.generate(effective_query, context_text, chat_history)
        
        # Step 4.5: Check if answer is sufficient, use full document analysis if needed
        answer_quality = self._assess_answer_quality(answer, retrieved_docs, user_query)
        doc_analysis_used = False
        
        if not answer_quality.get('sufficient', True) and (self.original_balance_sheet or self.original_company_profile):
            # Answer is insufficient, try full document analysis
            documents = {}
            if self.original_balance_sheet:
                documents['balance_sheet'] = self.original_balance_sheet
            if self.original_company_profile:
                documents['company_profile'] = self.original_company_profile
            
            if documents:
                doc_analysis = self.doc_analyzer.analyze_multiple_documents(documents, user_query)
                
                if doc_analysis.get('found_information', False) and doc_analysis.get('confidence') in ['high', 'medium']:
                    # Use document analysis answer if it found information
                    answer = doc_analysis.get('answer', answer)
                    doc_analysis_used = True
                    
                    # Add relevant excerpts to context
                    excerpts = doc_analysis.get('relevant_excerpts', [])
                    if excerpts:
                        context_text += f"\n\n[Additional Information from Full Document Analysis]\n" + "\n".join(excerpts)
        
        # Step 5: Grounding check
        grounding_result = self.grounding_checker.check(answer, context_text, user_query)
        
        # Use corrected answer if needed
        final_answer = grounding_result.get('corrected_answer', answer)
        
        # Extract citations from metadata
        citations = []
        for doc in retrieved_docs:
            section = doc.get('metadata', {}).get('section', 'Unknown')
            if section not in citations:
                citations.append(section)
        
        return {
            'answer': final_answer,
            'context': retrieved_docs,
            'compressed_context': context_text,
            'route_info': route_info,
            'grounding_check': grounding_result,
            'citations': citations,
            'query_used': effective_query if effective_query != user_query else None,
            'web_search_used': web_used,
            'doc_analysis_used': doc_analysis_used
        }
    
    def _assess_answer_quality(self, answer: str, retrieved_docs: List[Dict], query: str) -> Dict[str, Any]:
        """
        Assess if the answer is sufficient or if we need full document analysis
        
        Args:
            answer: Generated answer
            retrieved_docs: Retrieved documents
            query: Original query
            
        Returns:
            Dictionary with quality assessment
        """
        # Check for indicators of insufficient answer
        insufficient_indicators = [
            "i couldn't find",
            "i don't have",
            "no information",
            "not available",
            "not mentioned",
            "not provided",
            "unable to find",
            "couldn't find relevant"
        ]
        
        answer_lower = answer.lower()
        has_insufficient_indicator = any(indicator in answer_lower for indicator in insufficient_indicators)
        
        # Check if we have enough retrieved docs
        has_enough_docs = len(retrieved_docs) >= 2
        
        # Check if answer is too short (might be insufficient)
        answer_too_short = len(answer) < 50
        
        # Determine if answer is sufficient
        sufficient = not (has_insufficient_indicator or (answer_too_short and not has_enough_docs))
        
        return {
            'sufficient': sufficient,
            'has_insufficient_indicator': has_insufficient_indicator,
            'answer_length': len(answer),
            'docs_retrieved': len(retrieved_docs)
        }
    
    def get_context_for_ppt(self, slide_types: List[str] = None) -> Dict[str, Any]:
        """
        Get optimized context for PPT generation
        
        Args:
            slide_types: List of slide types to generate context for
            
        Returns:
            Dictionary with context organized by slide type
        """
        if not self.vector_db:
            raise ValueError("Pipeline not initialized. Please run ingest() first.")
        
        slide_types = slide_types or ['executive', 'financials', 'company', 'assets', 'liabilities']
        
        context_by_slide = {}
        
        # Define queries for each slide type
        slide_queries = {
            'executive': 'What are the key financial highlights and summary metrics?',
            'financials': 'What are the detailed financial numbers, assets, liabilities, and equity?',
            'company': 'What is the company overview, mission, vision, and key facts?',
            'assets': 'What are the asset breakdown, current assets, and non-current assets?',
            'liabilities': 'What are the liabilities breakdown, current liabilities, and long-term debt?',
            'ratios': 'What are the financial ratios and key metrics?',
            'trends': 'What are the trends, insights, and patterns in the financial data?',
            'conclusion': 'What are the key takeaways and conclusions?',
            'products_services': 'What products and services does the company offer? What are the product categories and certifications?',
            'markets_locations': 'What markets and industries does the company serve? Where are the company locations and offices? What are the manufacturing capabilities?',
            'leadership': 'Who are the leadership team members? What is the CEO message? Who are the executives and management?',
            'major_projects': 'What are the major projects and notable work? Who are the clients and customers? What partnerships exist?',
            'vision_mission': 'What is the company vision and mission statement? What are the core values and unique selling points?'
        }
        
        for slide_type in slide_types:
            if slide_type in slide_queries:
                query = slide_queries[slide_type]
                retrieved_docs = self.retriever_agent.retrieve(query, k=6)
                
                # Compress context for this slide
                context_text = self.context_compressor.compress(retrieved_docs, query)
                
                context_by_slide[slide_type] = {
                    'context': context_text,
                    'documents': retrieved_docs,
                    'query': query
                }
        
        return context_by_slide
    
    def get_enhanced_context(self, query: str, k: int = 8) -> str:
        """
        Get enhanced context for a specific query (useful for PPT generation)
        
        Args:
            query: Query to get context for
            k: Number of documents to retrieve
            
        Returns:
            Enhanced context string
        """
        if not self.retriever_agent:
            raise ValueError("Pipeline not initialized. Please run ingest() first.")
        
        retrieved_docs = self.retriever_agent.retrieve(query, k=k)
        return self.context_compressor.compress(retrieved_docs, query)

