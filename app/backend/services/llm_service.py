from openai import OpenAI
from typing import List, Dict
from config import Config
import json

class LLMService:
    """Unified service for interacting with OpenAI's LLM for both RAG and PPT generation"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file.")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    # ==================== RAG Methods ====================
    
    def generate_summary(self, entry_title: str, content: str) -> str:
        """
        Generate a concise summary of a balance sheet entry
        
        Args:
            entry_title: Title/name of the entry
            content: Content to summarize (values across time periods)
            
        Returns:
            Summary text
        """
        prompt = f"""Analyze this balance sheet entry and provide a concise summary in 2-3 sentences.
Focus on key financial metrics, trends over time, and insights that would be valuable for financial analysis.
Highlight significant changes, patterns, or notable values.

Entry: {entry_title}
Data: {content}

Provide a clear, professional summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at summarizing individual balance sheet entries and identifying trends over time."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def generate_summaries(self, entries: List[Dict]) -> List[Dict]:
        """Generate individual summaries for each balance sheet entry"""
        summaries = []
        
        for entry in entries:
            content = '\n'.join(entry['content'])
            summary = self.generate_summary(entry['title'], content)
            
            summaries.append({
                'section': entry['title'],  # Keep 'section' key for backward compatibility
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
    
    # ==================== PPT Methods ====================
    
    def generate_slide_content(self, slide_type: str, balance_data: Dict, 
                              company_data: Dict, metrics: Dict) -> Dict:
        """Generate content for a specific slide type"""
        
        prompts = {
            'title': self._title_prompt(company_data),
            'executive': self._executive_prompt(balance_data, metrics),
            'financials': self._financials_prompt(metrics),
            'assets': self._assets_prompt(balance_data, metrics),
            'liabilities': self._liabilities_prompt(balance_data, metrics),
            'ratios': self._ratios_prompt(metrics),
            'trends': self._trends_prompt(balance_data, metrics),
            'company': self._company_prompt(company_data),
            'conclusion': self._conclusion_prompt(balance_data, metrics)
        }
        
        prompt = prompts.get(slide_type, '')
        if not prompt:
            return {'error': f'Unknown slide type: {slide_type}'}
        
        try:
            response = self.client.chat.completions.create(
                model=Config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial presentation expert. Generate content for PowerPoint slides. Always respond with valid JSON only, no markdown formatting or additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
            
            content = response.choices[0].message.content
            # Clean any markdown formatting
            content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}, Content: {content}")
            return self._fallback_content(slide_type, balance_data, company_data, metrics)
        except Exception as e:
            print(f"Error generating content: {e}")
            return {'error': str(e)}
    
    def _title_prompt(self, company_data: Dict) -> str:
        return f"""Create a title slide for a financial presentation.

Company Information:
{json.dumps(company_data, indent=2)}

Return ONLY a JSON object with these fields:
{{
    "title": "Main presentation title",
    "subtitle": "Subtitle or tagline",
    "company_name": "Company name",
    "date": "Presentation date"
}}"""

    def _executive_prompt(self, balance_data: Dict, metrics: Dict) -> str:
        return f"""Create an executive summary slide with 4-5 key highlights.

Financial Data:
Total Assets: ${metrics.get('total_assets', 0):,.2f}
Total Liabilities: ${metrics.get('total_liabilities', 0):,.2f}
Total Equity: ${metrics.get('total_equity', 0):,.2f}

Return ONLY a JSON object:
{{
    "title": "Executive Summary",
    "highlights": ["highlight 1", "highlight 2", "highlight 3", "highlight 4"]
}}"""

    def _financials_prompt(self, metrics: Dict) -> str:
        return f"""Create a financial overview slide with key metrics.

Metrics:
{json.dumps(metrics, indent=2)}

Return ONLY a JSON object:
{{
    "title": "Financial Overview",
    "metrics": [
        {{"label": "Metric Name", "value": "$X.XX", "trend": "up/down/stable"}},
        ...
    ]
}}"""

    def _assets_prompt(self, balance_data: Dict, metrics: Dict) -> str:
        assets = balance_data.get('assets', {})
        return f"""Analyze and present asset breakdown.

Assets:
{json.dumps(assets, indent=2)}

Total Assets: ${metrics.get('total_assets', 0):,.2f}
Current Assets: ${metrics.get('current_assets', 0):,.2f}
Non-Current Assets: ${metrics.get('non_current_assets', 0):,.2f}

Return ONLY a JSON object:
{{
    "title": "Assets Breakdown",
    "total": "$XX",
    "current": "$XX",
    "non_current": "$XX",
    "breakdown": [
        {{"category": "Cash", "amount": "$XX", "percentage": XX}},
        ...
    ],
    "insight": "Key insight about asset composition"
}}"""

    def _liabilities_prompt(self, balance_data: Dict, metrics: Dict) -> str:
        liabilities = balance_data.get('liabilities', {})
        return f"""Analyze and present liabilities breakdown.

Liabilities:
{json.dumps(liabilities, indent=2)}

Total Liabilities: ${metrics.get('total_liabilities', 0):,.2f}
Current Liabilities: ${metrics.get('current_liabilities', 0):,.2f}
Long-term Liabilities: ${metrics.get('long_term_liabilities', 0):,.2f}

Return ONLY a JSON object:
{{
    "title": "Liabilities Analysis",
    "total": "$XX",
    "current": "$XX",
    "long_term": "$XX",
    "debt_ratio": "X.XX",
    "insight": "Key insight about debt structure"
}}"""

    def _ratios_prompt(self, metrics: Dict) -> str:
        return f"""Calculate and explain key financial ratios.

Metrics:
{json.dumps(metrics, indent=2)}

Return ONLY a JSON object:
{{
    "title": "Financial Ratios",
    "ratios": [
        {{
            "name": "Current Ratio",
            "value": "X.XX",
            "interpretation": "What this means",
            "benchmark": "Industry standard"
        }},
        ...
    ]
}}"""

    def _trends_prompt(self, balance_data: Dict, metrics: Dict) -> str:
        return f"""Identify trends and provide insights.

Financial Data:
{json.dumps(metrics, indent=2)}

Return ONLY a JSON object:
{{
    "title": "Trends & Insights",
    "insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""

    def _company_prompt(self, company_data: Dict) -> str:
        return f"""Create a company profile slide.

Company Data:
{json.dumps(company_data, indent=2)}

Return ONLY a JSON object:
{{
    "title": "Company Profile",
    "company_name": "Name",
    "industry": "Industry",
    "founded": "Year",
    "mission": "Mission statement",
    "key_facts": ["fact 1", "fact 2", "fact 3"]
}}"""

    def _conclusion_prompt(self, balance_data: Dict, metrics: Dict) -> str:
        return f"""Create a conclusion slide.

Key Metrics:
{json.dumps(metrics, indent=2)}

Return ONLY a JSON object:
{{
    "title": "Conclusion & Next Steps",
    "summary": "Brief summary of key findings",
    "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3"],
    "next_steps": ["step 1", "step 2"]
}}"""

    def _fallback_content(self, slide_type: str, balance_data: Dict, 
                         company_data: Dict, metrics: Dict) -> Dict:
        """Provide fallback content if LLM fails"""
        fallbacks = {
            'title': {
                'title': 'Financial Presentation',
                'subtitle': 'Annual Report',
                'company_name': company_data.get('company_name', 'Company Name'),
                'date': '2024'
            },
            'executive': {
                'title': 'Executive Summary',
                'highlights': [
                    f"Total Assets: ${metrics.get('total_assets', 0):,.2f}",
                    f"Total Liabilities: ${metrics.get('total_liabilities', 0):,.2f}",
                    f"Equity: ${metrics.get('total_equity', 0):,.2f}"
                ]
            },
        }
        return fallbacks.get(slide_type, {'title': slide_type.title(), 'content': 'Content unavailable'})
