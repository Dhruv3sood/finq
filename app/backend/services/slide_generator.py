from typing import Dict, List
from .llm_service import LLMService
from .pptx_builder import PPTXBuilder
from utils.financial_parser import FinancialDataParser
from config import Config
import uuid
import os

class SlideGenerator:
    """Main service for generating presentation slides"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.parser = FinancialDataParser()
    
    def generate_presentation(self, balance_sheet_text: str, company_profile_text: str,
                            selected_slides: List[str], template: str, theme: str) -> Dict:
        """
        Generate complete presentation
        
        Args:
            balance_sheet_text: Raw balance sheet content
            company_profile_text: Raw company profile content
            selected_slides: List of slide types to include
            template: Template name
            theme: Color theme
            
        Returns:
            Dictionary with presentation data and file path
        """
        # Parse input data
        balance_data = self.parser.parse_balance_sheet(balance_sheet_text)
        # Use LLM service for enhanced company profile parsing
        company_data = self.parser.parse_company_profile(company_profile_text, llm_service=self.llm_service)
        metrics = self.parser.extract_financial_metrics(balance_data)
        
        # Generate slides
        slides = []
        for slide_type in selected_slides:
            content = self.llm_service.generate_slide_content(
                slide_type, balance_data, company_data, metrics
            )
            
            slides.append({
                'type': slide_type,
                'content': content
            })
        
        # Build PowerPoint file
        pptx_builder = PPTXBuilder(theme=theme)
        output_filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        
        file_path = pptx_builder.create_presentation(slides, output_path)
        
        return {
            'slides': slides,
            'file_path': file_path,
            'filename': output_filename,
            'slide_count': len(slides)
        }