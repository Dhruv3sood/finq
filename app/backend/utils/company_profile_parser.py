import re
from typing import List, Dict

class CompanyProfileParser:
    """Parse company profile documents into meaningful sections"""
    
    @staticmethod
    def parse(text: str) -> List[Dict]:
        """
        Parse company profile text into meaningful sections
        
        Args:
            text: Raw company profile content
            
        Returns:
            List of dictionaries containing section information
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return []
        
        sections = []
        current_section = None
        current_content = []
        
        # Common section headers/keywords
        section_patterns = {
            'Company Overview': ['company overview', 'about us', 'about the company', 'company background'],
            'Mission & Vision': ['mission', 'vision', 'mission statement', 'vision statement', 'values'],
            'History': ['history', 'founded', 'established', 'timeline', 'heritage'],
            'Products & Services': ['products', 'services', 'offerings', 'solutions', 'portfolio'],
            'Market Position': ['market', 'position', 'competitive', 'industry', 'sector'],
            'Leadership': ['leadership', 'management', 'executive', 'team', 'ceo', 'founder'],
            'Financial Highlights': ['financial', 'revenue', 'growth', 'performance', 'earnings'],
            'Operations': ['operations', 'facilities', 'locations', 'manufacturing', 'production'],
            'Technology': ['technology', 'innovation', 'r&d', 'research', 'development'],
            'Partnerships': ['partnerships', 'alliances', 'collaborations', 'clients', 'customers'],
            'Future Plans': ['future', 'strategy', 'plans', 'roadmap', 'goals', 'objectives']
        }
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line is a section header
            section_found = None
            for section_name, keywords in section_patterns.items():
                if any(keyword in line_lower for keyword in keywords) and len(line) < 100:
                    # Save previous section if exists
                    if current_section and current_content:
                        sections.append({
                            'title': current_section,
                            'content': current_content
                        })
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                # Add to current section or create default
                if current_section:
                    current_content.append(line)
                else:
                    # If no section yet, check if line looks like a header
                    if len(line) < 80 and not line.endswith('.') and not line.endswith(','):
                        # Might be a header
                        current_section = line[:50]
                        current_content = []
                    else:
                        # Default section
                        current_section = 'Company Information'
                        current_content = [line]
        
        # Add last section
        if current_section and current_content:
            sections.append({
                'title': current_section,
                'content': current_content
            })
        
        # If no sections found, split by paragraphs
        if not sections:
            # Try to split by double newlines or long paragraphs
            paragraphs = text.split('\n\n')
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if para and len(para) > 20:
                    # Extract potential title from first sentence
                    first_sentence = para.split('.')[0] if '.' in para else para[:50]
                    if len(first_sentence) < 60:
                        title = first_sentence
                        content = [para]
                    else:
                        title = f"Section {i + 1}"
                        content = [para]
                    
                    sections.append({
                        'title': title,
                        'content': content
                    })
        
        # If still no sections, create one with all content
        if not sections:
            sections.append({
                'title': 'Company Profile',
                'content': lines
            })
        
        return sections

