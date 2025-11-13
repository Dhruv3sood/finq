"""Tools for agentic pipeline"""
from typing import List, Dict, Any, Optional
from utils.pdf_extractor import PDFExtractor
from services.embedding_service import EmbeddingService
from config import Config
import os
import json
import re

# Try to import web search libraries
try:
    from duckduckgo_search import DDGS
    HAS_DUCKDUCKGO = True
except ImportError:
    HAS_DUCKDUCKGO = False

try:
    from googlesearch import search as google_search
    HAS_GOOGLE_SEARCH = True
except ImportError:
    HAS_GOOGLE_SEARCH = False

# Try to import langchain, fallback to simple splitter
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


class PDFLoaderTool:
    """Tool for loading and extracting text from PDF files"""
    
    @staticmethod
    def load(file_path: str) -> Dict[str, Any]:
        """
        Load PDF file and extract text
        
        Args:
            file_path: Path to PDF file or file content as string
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Check if file_path is actual path or content
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    text = PDFExtractor.extract_text(f)
            else:
                # Assume it's file content or file-like object
                if isinstance(file_path, str) and len(file_path) > 1000:
                    # Likely content string
                    return {
                        'text': file_path,
                        'metadata': {'source': 'direct_input', 'type': 'text'}
                    }
                else:
                    text = PDFExtractor.extract_text(file_path)
            
            return {
                'text': text,
                'metadata': {
                    'source': file_path if isinstance(file_path, str) else 'uploaded_file',
                    'type': 'pdf',
                    'length': len(text)
                }
            }
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")


class TextSplitterTool:
    """Tool for splitting text into chunks"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if HAS_LANGCHAIN:
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        else:
            self.splitter = None
    
    def split(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if self.splitter:
            chunks = self.splitter.split_text(text)
        else:
            # Fallback simple splitter
            chunks = self._simple_split(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta.update({
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk)
            })
            result.append({
                'text': chunk,
                'metadata': chunk_meta
            })
        
        return result
    
    def _simple_split(self, text: str) -> List[str]:
        """Simple text splitter fallback"""
        # Split by paragraphs first
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > self.chunk_size:
                chunks.append(current_chunk)
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            
            # If single paragraph is too long, split by sentences
            if len(current_chunk) > self.chunk_size:
                sentences = re.split(r'[.!?]+\s+', current_chunk)
                temp_chunk = ""
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) > self.chunk_size:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = sentence
                    else:
                        temp_chunk += ". " + sentence if temp_chunk else sentence
                current_chunk = temp_chunk
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class EmbedderTool:
    """Tool for creating embeddings"""
    
    def __init__(self, model: str = None):
        self.embedding_service = EmbeddingService()
        self.model = model or Config.EMBEDDING_MODEL
    
    def embed(self, text: str) -> List[float]:
        """
        Create embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embedding_service.create_embedding(text)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.embedding_service.create_embedding(text) for text in texts]


class VectorDBTool:
    """Tool for vector database operations"""
    
    def __init__(self, db_name: str = "rag_db", persist_directory: str = None):
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.persist_directory = persist_directory or os.path.join(
                os.path.dirname(__file__), '..', '..', 'vector_db'
            )
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=db_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._in_memory_store = []  # Not used when ChromaDB is available
            self.use_chromadb = True
        except ImportError:
            # Fallback to in-memory storage if ChromaDB not available
            print("Warning: ChromaDB not installed, using in-memory storage")
            self.collection = None
            self._in_memory_store = []
            self.use_chromadb = False
    
    def store(self, documents: List[Dict[str, Any]], embeddings: List[List[float]], 
              metadatas: List[Dict] = None) -> bool:
        """
        Store documents with embeddings in vector DB
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            
        Returns:
            True if successful
        """
        if not self.use_chromadb or self.collection is None:
            # In-memory fallback
            for doc, emb, meta in zip(documents, embeddings, metadatas or [{}] * len(documents)):
                self._in_memory_store.append({
                    'text': doc.get('text', ''),
                    'embedding': emb,
                    'metadata': meta
                })
            return True
        
        texts = [doc.get('text', '') for doc in documents]
        ids = [f"doc_{i}" for i in range(len(texts))]
        
        if metadatas is None:
            metadatas = [doc.get('metadata', {}) for doc in documents]
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            raise Exception(f"Error storing in vector DB: {str(e)}")
    
    def search(self, query_embedding: List[float], k: int = 4, 
               filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar documents with scores
        """
        if not self.use_chromadb or self.collection is None:
            # In-memory fallback
            from services.embedding_service import EmbeddingService
            emb_service = EmbeddingService()
            results = []
            for item in self._in_memory_store:
                similarity = emb_service.cosine_similarity(
                    query_embedding, item['embedding']
                )
                results.append({
                    'text': item['text'],
                    'metadata': item['metadata'],
                    'score': similarity
                })
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:k]
        
        try:
            where = filter_metadata if filter_metadata else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where
            )
            
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1 - results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return formatted_results
        except Exception as e:
            raise Exception(f"Error searching vector DB: {str(e)}")


class ContextCompressorTool:
    """Tool for compressing and summarizing retrieved context - GENERALIZED"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def compress(self, retrieved_docs: List[Dict[str, Any]], 
                 query: Optional[str] = None) -> str:
        """
        Compress multiple retrieved chunks into concise context
        
        Args:
            retrieved_docs: List of retrieved document dictionaries
            query: Optional query to focus compression
            
        Returns:
            Compressed context string
        """
        if not retrieved_docs:
            return "No relevant context found."
        
        # Format retrieved documents
        context_text = "\n\n".join([
            f"[Document {i+1}]\n"
            f"Section: {doc.get('metadata', {}).get('section', 'Unknown')}\n"
            f"Content: {doc.get('text', '')}\n"
            f"Relevance: {doc.get('score', 0):.2f}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        prompt = f"""Organize and format the following retrieved text snippets for answering the user's question.
PRESERVE ALL relevant information - do not remove details that might be useful.
Focus on information relevant to the query, but keep comprehensive context.

{"User Query: " + query if query else ""}

Retrieved Context:
{context_text}

Provide a well-organized summary that:
1. Preserves ALL important facts, numbers, names, and details
2. Organizes information logically
3. Removes only obvious duplicates
4. Keeps all information that could be relevant to the query

Summary:"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at compressing and summarizing retrieved context while preserving all important factual information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to simple concatenation
            return context_text


class GroundingCheckerTool:
    """Tool for validating answer grounding in context"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def check(self, answer: str, context: str, query: str) -> Dict[str, Any]:
        """
        Check if answer is grounded in context
        
        Args:
            answer: Generated answer
            context: Retrieved context
            query: Original query
            
        Returns:
            Dictionary with validation result and corrected answer if needed
        """
        prompt = f"""Check if the following answer is grounded in the provided context.
If hallucination or unsupported claims are detected, provide a corrected version that only uses information from the context.
If the answer is well-grounded, return it as-is.

Query: {query}

Context:
{context}

Answer to check:
{answer}

Return a JSON object with:
{{
    "is_grounded": true/false,
    "corrected_answer": "corrected version if needed, otherwise original answer",
    "issues": ["list of any issues found"],
    "citations": ["list of specific facts that support the answer"]
}}"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at validating factual accuracy and grounding of answers in provided context. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            # Fallback: assume answer is grounded
            return {
                "is_grounded": True,
                "corrected_answer": answer,
                "issues": [],
                "citations": []
            }


class CompanyProfileParserTool:
    """Tool for parsing company profile/brochure - Enhanced version"""
    
    def __init__(self, llm_service=None):
        """Initialize with optional LLM service"""
        self.llm_service = llm_service
    
    def parse(self, text: str) -> Dict:
        """Parse company profile/brochure into comprehensive sections"""
        from utils.enhanced_company_parser import EnhancedCompanyParser
        
        # Parse with enhanced parser
        company_data = EnhancedCompanyParser.parse_brochure(text, self.llm_service)
        
        # Create indexable sections for RAG
        sections = []
        
        # Core information
        if company_data.get('about_us'):
            sections.append({
                'title': 'About Us',
                'content': company_data['about_us'],
                'category': 'overview'
            })
        
        if company_data.get('ceo_message'):
            sections.append({
                'title': "CEO's Message",
                'content': company_data['ceo_message'],
                'category': 'leadership'
            })
        
        if company_data.get('history'):
            sections.append({
                'title': 'Company History',
                'content': company_data['history'],
                'category': 'background'
            })
        
        # Vision, Mission, Values
        if company_data.get('mission'):
            sections.append({
                'title': 'Mission Statement',
                'content': company_data['mission'],
                'category': 'values'
            })
        
        if company_data.get('vision'):
            sections.append({
                'title': 'Vision Statement',
                'content': company_data['vision'],
                'category': 'values'
            })
        
        if company_data.get('values'):
            sections.append({
                'title': 'Core Values',
                'content': '\n'.join(company_data['values']),
                'category': 'values'
            })
        
        # Products & Services
        if company_data.get('products_services'):
            sections.append({
                'title': 'Products & Services',
                'content': '\n'.join(company_data['products_services']),
                'category': 'offerings'
            })
        
        if company_data.get('product_categories'):
            sections.append({
                'title': 'Product Categories',
                'content': '\n'.join(company_data['product_categories']),
                'category': 'offerings'
            })
        
        # Markets & Operations
        if company_data.get('markets'):
            sections.append({
                'title': 'Markets & Industries',
                'content': '\n'.join(company_data['markets']),
                'category': 'markets'
            })
        
        if company_data.get('locations'):
            sections.append({
                'title': 'Locations & Presence',
                'content': '\n'.join(company_data['locations']),
                'category': 'operations'
            })
        
        if company_data.get('manufacturing'):
            sections.append({
                'title': 'Manufacturing Capabilities',
                'content': company_data['manufacturing'],
                'category': 'operations'
            })
        
        # Achievements & Credentials
        if company_data.get('certifications'):
            sections.append({
                'title': 'Certifications & Standards',
                'content': '\n'.join(company_data['certifications']),
                'category': 'credentials'
            })
        
        if company_data.get('major_projects'):
            sections.append({
                'title': 'Major Projects',
                'content': '\n'.join(company_data['major_projects']),
                'category': 'achievements'
            })
        
        # Clients & Partners - combine list and text
        clients_content = []
        if company_data.get('clients_text'):
            clients_content.append(company_data['clients_text'])
        if company_data.get('clients'):
            clients_list = '\n'.join([f"• {client}" for client in company_data['clients']])
            clients_content.append(clients_list)
        
        if clients_content:
            sections.append({
                'title': 'Clients & Partners',
                'content': '\n\n'.join(clients_content),
                'category': 'relationships'
            })
        
        # Competitive Advantages
        if company_data.get('usps'):
            sections.append({
                'title': 'Unique Selling Points',
                'content': '\n'.join(company_data['usps']),
                'category': 'advantages'
            })
        
        if company_data.get('leadership'):
            sections.append({
                'title': 'Leadership Team',
                'content': '\n'.join(company_data['leadership']),
                'category': 'leadership'
            })
        
        return {
            'company_data': company_data,
            'sections': sections,
            'section_count': len(sections),
            'section_titles': [s['title'] for s in sections],
            'categories': list(set(s['category'] for s in sections))
        }


class DocumentAnalysisTool:
    """Tool for analyzing full document text when retrieval is insufficient"""
    
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    def analyze_document_for_query(self, document_text: str, query: str, 
                                   doc_type: str = "company_profile") -> Dict[str, Any]:
        """
        Analyze full document text to answer a query when retrieval is insufficient
        
        Args:
            document_text: Full document text (brochure, balance sheet, etc.)
            query: User's question
            doc_type: Type of document (company_profile, balance_sheet, etc.)
            
        Returns:
            Dictionary with answer and relevant excerpts
        """
        try:
            # Use up to 10000 chars for comprehensive analysis
            text_chunk = document_text[:10000] if len(document_text) > 10000 else document_text
            
            prompt = f"""You are analyzing a {doc_type} document to answer a user's question.

User Question: {query}

Document Text:
{text_chunk}

Analyze the entire document and provide a comprehensive answer to the question. 
Extract ALL relevant information, even if it's not explicitly stated in a single section.
Be thorough and cite specific details from the document.

Return a JSON object with:
{{
    "answer": "comprehensive answer to the question",
    "relevant_excerpts": ["excerpt 1", "excerpt 2", ...],
    "confidence": "high/medium/low",
    "found_information": true/false
}}"""
            
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing company documents and extracting comprehensive information. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Warning: Document analysis failed: {e}")
            return {
                "answer": "I couldn't analyze the document to answer this question.",
                "relevant_excerpts": [],
                "confidence": "low",
                "found_information": False
            }
    
    def analyze_multiple_documents(self, documents: Dict[str, str], query: str) -> Dict[str, Any]:
        """
        Analyze multiple documents (e.g., balance sheet + company profile) for a query
        
        Args:
            documents: Dictionary mapping doc_type to document text
            query: User's question
            
        Returns:
            Dictionary with comprehensive answer combining all documents
        """
        try:
            # Combine all documents (up to 12000 chars total)
            combined_text = ""
            doc_types = []
            for doc_type, text in documents.items():
                chunk = text[:4000] if len(text) > 4000 else text
                combined_text += f"\n\n[{doc_type.upper()}]\n{chunk}\n"
                doc_types.append(doc_type)
            
            combined_text = combined_text[:12000]
            
            prompt = f"""You are analyzing multiple company documents to answer a user's question.

User Question: {query}

Documents Available: {', '.join(doc_types)}

Combined Document Text:
{combined_text}

Analyze ALL documents comprehensively and provide a thorough answer to the question.
Extract information from any relevant section across all documents.
Be comprehensive and cite which document/section the information comes from.

Return a JSON object with:
{{
    "answer": "comprehensive answer combining information from all documents",
    "relevant_excerpts": ["excerpt 1", "excerpt 2", ...],
    "confidence": "high/medium/low",
    "found_information": true/false,
    "sources": ["document_type: section", ...]
}}"""
            
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing multiple company documents and synthesizing comprehensive answers. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Warning: Multi-document analysis failed: {e}")
            return {
                "answer": "I couldn't analyze the documents to answer this question.",
                "relevant_excerpts": [],
                "confidence": "low",
                "found_information": False,
                "sources": []
            }


class WebSearchTool:
    """Tool for searching the web when document context is insufficient"""
    
    def __init__(self, use_duckduckgo: bool = True, use_google: bool = False):
        """
        Initialize web search tool
        
        Args:
            use_duckduckgo: Use DuckDuckGo search (free, no API key)
            use_google: Use Google search (requires no API key, but rate limited)
        """
        self.use_duckduckgo = use_duckduckgo and HAS_DUCKDUCKGO
        self.use_google = use_google and HAS_GOOGLE_SEARCH
        
        if not self.use_duckduckgo and not self.use_google:
            print("Warning: No web search libraries available. Install duckduckgo-search or googlesearch-python")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and URL
        """
        results = []
        
        # Try DuckDuckGo first (free, no API key needed)
        if self.use_duckduckgo:
            try:
                with DDGS() as ddgs:
                    search_results = ddgs.text(query, max_results=max_results)
                    for result in search_results:
                        results.append({
                            'title': result.get('title', ''),
                            'snippet': result.get('body', ''),
                            'url': result.get('href', ''),
                            'source': 'duckduckgo'
                        })
                    if results:
                        return results
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
        
        # Fallback to Google search
        if self.use_google and not results:
            try:
                google_results = list(google_search(query, num_results=max_results))
                # Google search returns URLs, we need to fetch content
                # For now, just return URLs (can be enhanced with content fetching)
                for i, url in enumerate(google_results[:max_results]):
                    results.append({
                        'title': f'Result {i+1}',
                        'snippet': url,
                        'url': url,
                        'source': 'google'
                    })
            except Exception as e:
                print(f"Google search failed: {e}")
        
        return results
    
    def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        """
        Search the web and return a summarized context string
        
        Args:
            query: Search query
            max_results: Maximum number of results to use
            
        Returns:
            Summarized context string from web search results
        """
        results = self.search(query, max_results=max_results)
        
        if not results:
            return ""
        
        # Format results into context string
        context_parts = []
        for result in results:
            context_parts.append(
                f"Title: {result['title']}\n"
                f"Content: {result['snippet']}\n"
                f"Source: {result['url']}"
            )
        
        return "\n\n".join(context_parts)

