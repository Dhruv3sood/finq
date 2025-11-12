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


class FinancialDataParser:
    """Parse financial documents and extract key information for PPT generation"""
    
    @staticmethod
    def parse_balance_sheet(text: str) -> Dict:
        """Parse balance sheet and extract financial data"""
        data = {
            'assets': {},
            'liabilities': {},
            'equity': {},
            'raw_sections': []
        }
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect sections
            if 'asset' in line_lower:
                current_section = 'assets'
                data['raw_sections'].append({'type': 'assets', 'title': line, 'content': []})
            elif 'liabilit' in line_lower:
                current_section = 'liabilities'
                data['raw_sections'].append({'type': 'liabilities', 'title': line, 'content': []})
            elif 'equity' in line_lower or 'capital' in line_lower:
                current_section = 'equity'
                data['raw_sections'].append({'type': 'equity', 'title': line, 'content': []})
            elif current_section and data['raw_sections']:
                data['raw_sections'][-1]['content'].append(line)
            
            # Extract numerical values
            amounts = re.findall(r'\$?\s*([\d,]+\.?\d*)', line)
            if amounts and current_section:
                key = re.sub(r'[^\w\s]', '', line.split(amounts[0])[0]).strip()
                if key:
                    try:
                        value = float(amounts[0].replace(',', ''))
                        data[current_section][key] = value
                    except ValueError:
                        pass
        
        return data
    
    @staticmethod
    def parse_company_profile(text: str, llm_service=None) -> Dict:
        """
        Parse company profile text using LLM for better extraction
        
        Args:
            text: Raw company profile content
            llm_service: Optional LLM service for enhanced parsing
            
        Returns:
            Dictionary with structured company information
        """
        # Basic parsing first
        data = {
            'company_name': '',
            'industry': '',
            'founded': '',
            'mission': '',
            'vision': '',
            'description': '',
            'key_facts': [],
            'products_services': [],
            'market_position': '',
            'leadership': [],
            'locations': []
        }
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Basic keyword-based extraction
        for line in lines:
            line_lower = line.lower()
            if 'company' in line_lower and 'name' in line_lower:
                data['company_name'] = re.sub(r'company\s*name\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
            elif 'industry' in line_lower:
                data['industry'] = re.sub(r'industry\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
            elif 'founded' in line_lower or 'established' in line_lower:
                data['founded'] = re.sub(r'(founded|established)\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
            elif 'mission' in line_lower and 'vision' not in line_lower:
                data['mission'] = re.sub(r'mission\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
            elif 'vision' in line_lower:
                data['vision'] = re.sub(r'vision\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
            elif line and len(line) > 20:
                if not data['description']:
                    data['description'] = line
                else:
                    data['key_facts'].append(line)
        
        # Use LLM for enhanced extraction if available
        if llm_service and text:
            try:
                enhanced_data = FinancialDataParser._extract_with_llm(text, llm_service)
                # Merge LLM-extracted data with basic parsing
                for key, value in enhanced_data.items():
                    if value and (not data.get(key) or len(str(value)) > len(str(data.get(key, '')))):
                        data[key] = value
            except Exception as e:
                print(f"LLM extraction failed, using basic parsing: {e}")
        
        return data
    
    @staticmethod
    def _extract_with_llm(text: str, llm_service) -> Dict:
        """Use LLM to extract structured company information"""
        import json
        
        prompt = f"""Extract structured information from this company profile. Return ONLY a valid JSON object with no markdown formatting.

Company Profile Text:
{text[:2000]}  # Limit text length

Return a JSON object with these fields (use empty string or empty array if not found):
{{
    "company_name": "Company name",
    "industry": "Industry sector",
    "founded": "Year founded or established",
    "mission": "Mission statement",
    "vision": "Vision statement",
    "description": "Company description/overview",
    "key_facts": ["fact 1", "fact 2", "fact 3"],
    "products_services": ["product/service 1", "product/service 2"],
    "market_position": "Market position or competitive advantage",
    "leadership": ["Leader name 1", "Leader name 2"],
    "locations": ["Location 1", "Location 2"]
}}"""

        try:
            from config import Config
            response = llm_service.client.chat.completions.create(
                model=Config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from company profiles. Always return valid JSON only, no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            # Clean any markdown formatting
            content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return {}
    
    @staticmethod
    def extract_financial_metrics(balance_data: Dict) -> Dict:
        """Extract and calculate financial metrics"""
        assets = balance_data.get('assets', {})
        liabilities = balance_data.get('liabilities', {})
        equity = balance_data.get('equity', {})
        
        total_assets = sum(assets.values()) if assets else 0
        total_liabilities = sum(liabilities.values()) if liabilities else 0
        total_equity = sum(equity.values()) if equity else 0
        
        # Calculate current and non-current if available
        current_assets = sum(v for k, v in assets.items() if 'current' in k.lower()) or 0
        non_current_assets = total_assets - current_assets
        
        current_liabilities = sum(v for k, v in liabilities.items() if 'current' in k.lower()) or 0
        long_term_liabilities = total_liabilities - current_liabilities
        
        return {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'current_assets': current_assets,
            'non_current_assets': non_current_assets,
            'current_liabilities': current_liabilities,
            'long_term_liabilities': long_term_liabilities,
            'debt_to_equity': total_liabilities / total_equity if total_equity > 0 else 0,
            'current_ratio': current_assets / current_liabilities if current_liabilities > 0 else 0
        }