import re
from typing import Dict, List

class FinancialDataParser:
    """Parse financial documents and extract key information"""
    
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
    def parse_company_profile(text: str) -> Dict:
        """Parse company profile and extract key information"""
        profile = {
            'company_name': '',
            'industry': '',
            'founded': '',
            'mission': '',
            'vision': '',
            'key_facts': [],
            'raw_text': text
        }
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Extract company name (usually first line or contains "company")
            if i == 0 or 'company' in line_lower:
                if not profile['company_name']:
                    profile['company_name'] = line.split(':')[-1].strip()
            
            # Extract mission
            if 'mission' in line_lower:
                if i + 1 < len(lines):
                    profile['mission'] = lines[i + 1]
                elif ':' in line:
                    profile['mission'] = line.split(':', 1)[1].strip()
            
            # Extract vision
            if 'vision' in line_lower:
                if i + 1 < len(lines):
                    profile['vision'] = lines[i + 1]
                elif ':' in line:
                    profile['vision'] = line.split(':', 1)[1].strip()
            
            # Extract industry
            if 'industry' in line_lower:
                profile['industry'] = line.split(':')[-1].strip()
            
            # Extract founded year
            if 'founded' in line_lower or 'established' in line_lower:
                years = re.findall(r'\b(19|20)\d{2}\b', line)
                if years:
                    profile['founded'] = years[0]
        
        # Extract key facts (numbered or bulleted items)
        for line in lines:
            if re.match(r'^[\d\-\•\*]\s', line):
                fact = re.sub(r'^[\d\-\•\*]\s+', '', line)
                profile['key_facts'].append(fact)
        
        return profile
    
    @staticmethod
    def extract_financial_metrics(balance_data: Dict) -> Dict:
        """Calculate key financial metrics"""
        metrics = {}
        
        assets = balance_data.get('assets', {})
        liabilities = balance_data.get('liabilities', {})
        equity = balance_data.get('equity', {})
        
        # Calculate totals
        total_assets = sum(assets.values()) if assets else 0
        total_liabilities = sum(liabilities.values()) if liabilities else 0
        total_equity = sum(equity.values()) if equity else 0
        
        metrics['total_assets'] = total_assets
        metrics['total_liabilities'] = total_liabilities
        metrics['total_equity'] = total_equity
        
        # Calculate ratios
        if total_assets > 0:
            metrics['debt_to_asset_ratio'] = total_liabilities / total_assets
            metrics['equity_ratio'] = total_equity / total_assets
        
        if total_equity > 0:
            metrics['debt_to_equity_ratio'] = total_liabilities / total_equity
        
        # Categorize assets (simple heuristic)
        current_assets = sum(v for k, v in assets.items() 
                           if any(term in k.lower() for term in ['cash', 'receivable', 'inventory']))
        metrics['current_assets'] = current_assets
        metrics['non_current_assets'] = total_assets - current_assets
        
        # Categorize liabilities
        current_liabilities = sum(v for k, v in liabilities.items() 
                                if any(term in k.lower() for term in ['payable', 'short']))
        metrics['current_liabilities'] = current_liabilities
        metrics['long_term_liabilities'] = total_liabilities - current_liabilities
        
        # Current ratio
        if current_liabilities > 0:
            metrics['current_ratio'] = current_assets / current_liabilities
        
        return metrics