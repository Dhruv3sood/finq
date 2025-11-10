import re
import csv
import io
from typing import List, Dict

class BalanceSheetParser:
    """Parse balance sheet text/CSV into structured sections"""
    
    @staticmethod
    def parse(text: str) -> List[Dict[str, any]]:
        """
        Parse balance sheet text/CSV into sections
        
        Args:
            text: Raw text content of balance sheet
            
        Returns:
            List of dictionaries containing section information
        """
        # Try to parse as CSV first
        try:
            return BalanceSheetParser._parse_csv(text)
        except Exception:
            # Fall back to text parsing
            return BalanceSheetParser._parse_text(text)
    
    @staticmethod
    def _parse_csv(text: str) -> List[Dict[str, any]]:
        """Parse CSV format balance sheet"""
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        
        if not rows:
            return []
        
        # First row contains dates/headers
        headers = rows[0]
        sections = []
        
        # Define section categories
        liability_keywords = ['equity', 'reserves', 'borrowings', 'liabilities', 'capital']
        asset_keywords = ['assets', 'investments', 'cwip', 'fixed']
        
        # Group rows by section type
        current_section = None
        section_content = []
        
        for row in rows[1:]:
            if not row or not row[0]:
                continue
            
            item_name = row[0].strip().lower()
            is_liability = any(keyword in item_name for keyword in liability_keywords)
            is_asset = any(keyword in item_name for keyword in asset_keywords)
            
            # Determine section
            if 'total liabilities' in item_name or 'total assets' in item_name:
                # Add current section if exists
                if current_section and section_content:
                    sections.append({
                        'title': current_section,
                        'content': section_content
                    })
                
                # Create new section for totals
                section_title = 'Total Liabilities' if 'liabilities' in item_name else 'Total Assets'
                sections.append({
                    'title': section_title,
                    'content': [','.join(row)]
                })
                current_section = None
                section_content = []
            elif is_liability and not is_asset:
                # Save previous section
                if current_section and section_content:
                    sections.append({
                        'title': current_section,
                        'content': section_content
                    })
                # Start liabilities section
                current_section = 'Liabilities'
                section_content = [','.join(row)]
            elif is_asset:
                # Save previous section
                if current_section and section_content:
                    sections.append({
                        'title': current_section,
                        'content': section_content
                    })
                # Start assets section
                current_section = 'Assets'
                section_content = [','.join(row)]
            else:
                # Add to current section or create overview
                if not current_section:
                    current_section = 'Overview'
                    section_content = []
                section_content.append(','.join(row))
        
        # Add last section
        if current_section and section_content:
            sections.append({
                'title': current_section,
                'content': section_content
            })
        
        # If no sections found, create one with all data
        if not sections:
            sections.append({
                'title': 'Balance Sheet Data',
                'content': [','.join(row) for row in rows[1:] if row]
            })
        
        return sections
    
    @staticmethod
    def _parse_text(text: str) -> List[Dict[str, any]]:
        """Parse text format balance sheet"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        sections = []
        current_section = {
            'title': 'Overview',
            'content': []
        }
        
        # Keywords that indicate new sections
        section_keywords = [
            'assets', 'liabilities', 'equity', 'current', 
            'non-current', 'long-term', 'short-term', 
            'revenue', 'expenses', 'income'
        ]
        
        for line in lines:
            # Check if line is a section header
            is_header = any(keyword in line.lower() for keyword in section_keywords)
            
            if is_header and len(line) < 100:
                # Save previous section if it has content
                if current_section['content']:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line,
                    'content': []
                }
            else:
                current_section['content'].append(line)
        
        # Add the last section
        if current_section['content']:
            sections.append(current_section)
        
        return sections
    
    @staticmethod
    def extract_financial_items(text: str) -> List[Dict[str, str]]:
        """Extract individual financial line items with values"""
        items = []
        # Pattern to match line items with values (e.g., "Cash: $1,000")
        pattern = r'([A-Za-z\s]+)[\:\-\s]+[\$]?([\d,]+\.?\d*)'
        
        matches = re.findall(pattern, text)
        for item, value in matches:
            items.append({
                'item': item.strip(),
                'value': value.replace(',', '')
            })
        
        return items