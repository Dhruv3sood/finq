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
        """Parse CSV format balance sheet into individual entries"""
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        
        if not rows:
            return []
        
        # First row contains dates/headers
        headers = rows[0]
        entries = []
        
        # Process each row as an individual entry
        for row in rows[1:]:
            if not row or not row[0]:
                continue
            
            entry_name = row[0].strip()
            if not entry_name:
                continue
            
            # Create a formatted representation of the entry with headers
            # Format: "Entry Name: Header1=Value1, Header2=Value2, ..."
            entry_data = []
            for i, value in enumerate(row[1:], start=1):
                if i < len(headers):
                    header = headers[i].strip()
                    entry_data.append(f"{header}={value}")
            
            # Create entry content string
            entry_content = f"{entry_name}: {', '.join(entry_data)}"
            
            entries.append({
                'title': entry_name,
                'content': [entry_content]
            })
        
        return entries
    
    @staticmethod
    def _parse_text(text: str) -> List[Dict[str, any]]:
        """Parse text format balance sheet into individual entries"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        entries = []
        
        # Pattern to match line items with values (e.g., "Cash: $1,000" or "Cash - $1,000")
        # Also matches entries with multiple values separated by commas or tabs
        pattern = r'^([A-Za-z\s&\-\(\)]+?)[\:\-\s]+(.+)$'
        
        for line in lines:
            # Skip lines that are clearly section headers (short lines with common section keywords)
            section_keywords = ['assets', 'liabilities', 'equity', 'current', 
                              'non-current', 'long-term', 'short-term', 
                              'revenue', 'expenses', 'income', 'total']
            
            line_lower = line.lower()
            is_section_header = (len(line) < 50 and 
                               any(keyword in line_lower for keyword in section_keywords) and
                               ':' not in line and '-' not in line[1:])
            
            if is_section_header:
                continue
            
            # Try to match entry pattern
            match = re.match(pattern, line)
            if match:
                entry_name = match.group(1).strip()
                entry_values = match.group(2).strip()
                
                entries.append({
                    'title': entry_name,
                    'content': [f"{entry_name}: {entry_values}"]
                })
            else:
                # If no pattern match, treat the whole line as an entry
                # Split by common delimiters
                parts = re.split(r'[\:\-\t]+', line, 1)
                if len(parts) == 2:
                    entry_name = parts[0].strip()
                    entry_values = parts[1].strip()
                    entries.append({
                        'title': entry_name,
                        'content': [f"{entry_name}: {entry_values}"]
                    })
                elif line:
                    # Last resort: use the line as both title and content
                    entries.append({
                        'title': line[:50],  # Truncate if too long
                        'content': [line]
                    })
        
        # If no entries found, create one with all data
        if not entries:
            entries.append({
                'title': 'Balance Sheet Data',
                'content': lines
            })
        
        return entries
    
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