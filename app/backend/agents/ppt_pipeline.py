"""Agentic pipeline for PPT generation"""
from typing import Dict, Any, List, Optional
from agents.ppt_agents import (
    SlideContentAgent, DataExtractionAgent, QualityAssuranceAgent
)
from agents.pipeline import AgenticPipeline
from services.llm_service import LLMService
from utils.financial_parser import FinancialDataParser
from config import Config
import json


class PPTAgenticPipeline:
    """Orchestrates agentic pipeline for PPT generation"""
    
    def __init__(self, rag_pipeline: Optional[AgenticPipeline] = None):
        """
        Initialize PPT pipeline
        
        Args:
            rag_pipeline: Optional RAG pipeline for enhanced context retrieval
        """
        self.llm_service = LLMService()
        self.rag_pipeline = rag_pipeline
        self.parser = FinancialDataParser()
        
        # Initialize agents
        self.content_agent = SlideContentAgent(self.llm_service)
        self.extraction_agent = DataExtractionAgent(self.llm_service)
        self.qa_agent = QualityAssuranceAgent(self.llm_service)
    
    def generate_presentation(self, balance_sheet_text: str, company_profile_text: str,
                            selected_slides: List[str], template: str = 'professional',
                            theme: str = 'blue', use_enhanced_context: bool = True) -> Dict[str, Any]:
        """
        Generate presentation using agentic pipeline
        
        Args:
            balance_sheet_text: Raw balance sheet content
            company_profile_text: Raw company profile content
            selected_slides: List of slide types to generate
            template: Presentation template
            theme: Color theme
            use_enhanced_context: Whether to use RAG pipeline for context
            
        Returns:
            Dictionary with generated slides and metadata
        """
        # Parse financial data
        balance_data = self.parser.parse_balance_sheet(balance_sheet_text)
        
        # Use enhanced parser for company profile if we have RAG pipeline with company data
        if self.rag_pipeline and hasattr(self.rag_pipeline, 'company_data') and self.rag_pipeline.company_data:
            company_data = self.rag_pipeline.company_data
        else:
            # Fallback to basic parsing
            from utils.enhanced_company_parser import EnhancedCompanyParser
            company_data = EnhancedCompanyParser.parse_brochure(company_profile_text, self.llm_service)
        
        # ENSURE company_data has all fields - enhance with LLM if sparse
        if company_profile_text:
            company_data = self._ensure_comprehensive_company_data(company_data, company_profile_text)
        
        metrics = self.parser.extract_financial_metrics(balance_data)
        
        # Generate slides with agentic approach
        slides = []
        context_map = {}
        
        # Get enhanced context from RAG pipeline if available
        if use_enhanced_context and self.rag_pipeline:
            try:
                context_map = self.rag_pipeline.get_context_for_ppt(selected_slides)
            except Exception as e:
                print(f"Warning: Could not get enhanced context: {e}")
        
        # Generate each slide
        for slide_type in selected_slides:
            slide_content = self._generate_slide_with_agents(
                slide_type=slide_type,
                balance_data=balance_data,
                company_data=company_data,
                metrics=metrics,
                context_map=context_map,
                template=template,
                company_profile_text=company_profile_text
            )
            
            # Validate slide quality
            validation = self.qa_agent.validate_slide_content(slide_content)
            slide_content['validation'] = validation
            
            slides.append({
                'type': slide_type,
                'content': slide_content,
                'quality_score': validation.get('quality_score', 0)
            })
        
        # Calculate overall presentation quality
        avg_quality = sum(s.get('quality_score', 0) for s in slides) / len(slides) if slides else 0
        
        return {
            'slides': slides,
            'metadata': {
                'template': template,
                'theme': theme,
                'slide_count': len(slides),
                'avg_quality_score': avg_quality,
                'used_enhanced_context': bool(context_map),
                'context_slides': list(context_map.keys())
            }
        }
    
    def _generate_slide_with_agents(self, slide_type: str, balance_data: Dict,
                                    company_data: Dict, metrics: Dict,
                                    context_map: Dict, template: str,
                                    company_profile_text: str = None) -> Dict[str, Any]:
        """
        Generate single slide using agents and tools
        
        Args:
            slide_type: Type of slide
            balance_data: Parsed balance sheet data
            company_data: Parsed company profile data
            metrics: Financial metrics
            context_map: Map of enhanced contexts by slide type
            template: Template name
            company_profile_text: Raw company profile/brochure text for LLM fallback
            
        Returns:
            Generated slide content
        """
        # Get enhanced context for this slide type
        enhanced_context = None
        if slide_type in context_map:
            enhanced_context = context_map[slide_type].get('context', '')
        
        # Use content agent to generate slide
        slide_content = self.content_agent.generate_slide_content(
            slide_type=slide_type,
            balance_data=balance_data,
            company_data=company_data,
            metrics=metrics,
            enhanced_context=enhanced_context,
            company_profile_text=company_profile_text
        )
        
        # Extract additional data if needed
        if enhanced_context and slide_type in ['financials', 'assets', 'liabilities']:
            extracted_data = self.extraction_agent.extract_key_figures(
                enhanced_context, slide_type
            )
            slide_content['extracted_figures'] = extracted_data.get('figures', [])
        
        return slide_content
    
    def optimize_slide_order(self, slides: List[Dict]) -> List[Dict]:
        """
        Optimize slide order for better flow
        
        Args:
            slides: List of generated slides
            
        Returns:
            Reordered slides
        """
        # Define optimal order
        order_priority = {
            'title': 0,
            'executive': 1,
            'company': 2,
            'financials': 3,
            'assets': 4,
            'liabilities': 5,
            'ratios': 6,
            'trends': 7,
            'conclusion': 8
        }
        
        # Sort by priority
        sorted_slides = sorted(
            slides,
            key=lambda s: order_priority.get(s.get('type', ''), 99)
        )
        
        return sorted_slides
    
    def get_slide_recommendations(self, balance_sheet_text: str, company_profile_text: str) -> List[str]:
        """
        Recommend slides based on available data
        
        Args:
            balance_sheet_text: Raw balance sheet text
            company_profile_text: Raw company profile text
            
        Returns:
            List of recommended slide types
        """
        recommendations = ['title', 'executive', 'conclusion']
        
        # Parse balance sheet data first
        balance_data = self.parser.parse_balance_sheet(balance_sheet_text)
        metrics = self.parser.extract_financial_metrics(balance_data)
        
        # Recommend based on data availability
        if balance_data and balance_data.get('assets'):
            recommendations.append('assets')
        
        if balance_data and balance_data.get('liabilities'):
            recommendations.append('liabilities')
        
        if metrics and (metrics.get('current_ratio') or metrics.get('debt_to_equity')):
            recommendations.append('ratios')
        
        if balance_data and balance_data.get('assets') and balance_data.get('liabilities'):
            recommendations.append('financials')
            recommendations.append('trends')
        
        # Check company profile data
        if company_profile_text:
            # Use enhanced parser if RAG pipeline available
            if self.rag_pipeline and hasattr(self.rag_pipeline, 'company_data') and self.rag_pipeline.company_data:
                company_data = self.rag_pipeline.company_data
            else:
                from utils.enhanced_company_parser import EnhancedCompanyParser
                company_data = EnhancedCompanyParser.parse_brochure(company_profile_text, self.llm_service)
            
            if company_data.get('vision') or company_data.get('mission'):
                if 'vision_mission' not in recommendations:
                    recommendations.append('vision_mission')
            
            if company_data.get('products_services') or company_data.get('product_categories'):
                if 'products_services' not in recommendations:
                    recommendations.append('products_services')
            
            if company_data.get('markets') or company_data.get('locations'):
                if 'markets_locations' not in recommendations:
                    recommendations.append('markets_locations')
            
            if company_data.get('leadership'):
                if 'leadership' not in recommendations:
                    recommendations.append('leadership')
            
            if company_data.get('major_projects') or company_data.get('clients'):
                if 'major_projects' not in recommendations:
                    recommendations.append('major_projects')
        
        return recommendations
    
    def _ensure_comprehensive_company_data(self, company_data: Dict, brochure_text: str) -> Dict:
        """
        Ensure company_data has all necessary fields by extracting from brochure text if sparse
        
        Args:
            company_data: Existing parsed company data
            brochure_text: Raw brochure text
            
        Returns:
            Enhanced company data with all fields populated
        """
        # Check which fields are missing or sparse
        needs_enhancement = False
        
        if not company_data.get('products_services') or len(company_data.get('products_services', [])) < 2:
            needs_enhancement = True
        
        if not company_data.get('markets') or len(company_data.get('markets', [])) < 2:
            needs_enhancement = True
        
        if not company_data.get('leadership') or len(company_data.get('leadership', [])) < 2:
            needs_enhancement = True
        
        if not company_data.get('major_projects') or len(company_data.get('major_projects', [])) < 2:
            needs_enhancement = True
        
        if not company_data.get('clients') or len(company_data.get('clients', [])) < 2:
            needs_enhancement = True
        
        if not company_data.get('vision') and not company_data.get('mission'):
            needs_enhancement = True
        
        # Use LLM to extract comprehensive data if needed
        if needs_enhancement and brochure_text:
            try:
                prompt = f"""Extract comprehensive company information from this brochure text.
Extract ALL available information including products, services, markets, locations, leadership, projects, clients, vision, mission, values.

Brochure Text:
{brochure_text[:6000]}

Return a JSON object with these fields (extract everything you can find):
{{
    "products_services": ["product 1", "product 2", ...],
    "product_categories": ["category 1", ...],
    "markets": ["market 1", "market 2", ...],
    "locations": ["location 1", ...],
    "leadership": ["Name - Role", ...],
    "major_projects": ["project 1", ...],
    "clients": ["client 1", ...],
    "vision": "vision statement",
    "mission": "mission statement",
    "values": ["value 1", ...],
    "usps": ["USP 1", ...],
    "ceo_message": "CEO message text",
    "manufacturing": "manufacturing details",
    "certifications": ["cert 1", ...]
}}

Extract ALL information that exists in the text. Be comprehensive."""

                response = self.llm_service.client.chat.completions.create(
                    model=Config.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at extracting comprehensive company information from brochures. Extract ALL available information. Return ONLY valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content.strip()
                content = content.replace('```json', '').replace('```', '').strip()
                
                import json
                enhanced_data = json.loads(content)
                
                # Merge with existing data (enhanced data takes precedence if existing is sparse)
                for key, value in enhanced_data.items():
                    if key in company_data:
                        if isinstance(value, list) and value:
                            # Merge lists, remove duplicates
                            existing = company_data.get(key, [])
                            if isinstance(existing, list):
                                combined = list(set(existing + value))
                                company_data[key] = combined if combined else value
                            else:
                                company_data[key] = value
                        elif isinstance(value, str) and value and (not company_data.get(key) or len(company_data.get(key, '')) < len(value)):
                            # Use longer/more complete string
                            company_data[key] = value
                        elif not company_data.get(key):
                            # Fill in missing fields
                            company_data[key] = value
                    else:
                        company_data[key] = value
                        
            except Exception as e:
                print(f"Warning: Could not enhance company data with LLM: {e}")
        
        return company_data
    
    def generate_executive_brief(self, slides: List[Dict]) -> str:
        """
        Generate executive brief from slides
        
        Args:
            slides: Generated slides
            
        Returns:
            Executive brief text
        """
        prompt = f"""Based on the following slide contents, generate a concise executive brief (3-4 sentences) summarizing the key findings.

Slides:
{self._format_slides_for_llm(slides)}

Provide a professional executive brief:"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst creating executive briefs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Executive brief generation failed: {str(e)}"
    
    def _format_slides_for_llm(self, slides: List[Dict]) -> str:
        """Format slides for LLM processing"""
        formatted = []
        for slide in slides:
            slide_type = slide.get('type', 'unknown')
            content = slide.get('content', {})
            title = content.get('title', 'Untitled')
            
            # Extract key content
            if slide_type == 'executive':
                highlights = content.get('highlights', [])
                formatted.append(f"Executive Summary:\n- " + "\n- ".join(highlights[:3]))
            elif slide_type == 'financials':
                metrics = content.get('metrics', [])
                metric_text = ", ".join([f"{m.get('label')}: {m.get('value')}" for m in metrics[:3]])
                formatted.append(f"Financial Overview: {metric_text}")
            elif slide_type == 'company':
                name = content.get('company_name', 'Company')
                industry = content.get('industry', '')
                formatted.append(f"Company: {name} ({industry})")
        
        return "\n\n".join(formatted)

