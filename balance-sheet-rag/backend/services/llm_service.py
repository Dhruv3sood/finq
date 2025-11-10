from openai import OpenAI
from typing import List, Dict
from config import Config

class LLMService:
    """Service for interacting with OpenAI's LLM"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file.")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_summary(self, section_title: str, content: str) -> str:
        """
        Generate a concise summary of a balance sheet section
        
        Args:
            section_title: Title of the section
            content: Content to summarize
            
        Returns:
            Summary text
        """
        prompt = f"""Analyze this balance sheet section and provide a concise summary in 2-3 sentences.
Focus on key financial metrics, trends, and insights that would be valuable for financial analysis.

Section: {section_title}
Content: {content}

Provide a clear, professional summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at summarizing balance sheet data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def generate_summaries(self, sections: List[Dict]) -> List[Dict]:
        """Generate summaries for multiple sections"""
        summaries = []
        
        for section in sections:
            content = '\n'.join(section['content'])
            summary = self.generate_summary(section['title'], content)
            
            summaries.append({
                'section': section['title'],
                'original_content': content,
                'summary': summary
            })
        
        return summaries
    
    def chat(self, messages: List[Dict], context: str) -> str:
        """
        Generate a chat response with RAG context
        
        Args:
            messages: Chat history
            context: Retrieved relevant context
            
        Returns:
            Assistant's response
        """
        system_message = f"""You are a financial analyst assistant helping users understand their balance sheet.
Use the provided context to answer questions accurately and professionally.

Context from Balance Sheet:
{context}

Guidelines:
- Reference specific sections when relevant
- Provide concrete numbers when available
- If information isn't in the context, say so clearly
- Explain financial concepts if needed"""
        
        try:
            response = self.client.chat.completions.create(
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
            raise Exception(f"Error in chat: {str(e)}")