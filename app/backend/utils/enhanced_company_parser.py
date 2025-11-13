"""Enhanced Company Profile Parser to extract all sections from brochure"""
import re
from typing import Dict, List, Any


class EnhancedCompanyParser:
    """Parse comprehensive company profile/brochure with all sections"""
    
    @staticmethod
    def parse_brochure(text: str, llm_service=None) -> Dict[str, Any]:
        """
        Parse company brochure to extract ALL sections and information - DYNAMIC & GENERALIZED
        Works with any brochure format, structure, or language
        
        Args:
            text: Raw brochure content
            llm_service: Optional LLM service for intelligent extraction (HIGHLY RECOMMENDED)
            
        Returns:
            Dictionary with comprehensive company information
        """
        data = {
            'company_name': '',
            'tagline': '',
            'industry': '',
            'founded': '',
            'ceo_message': '',
            'about_us': '',
            'mission': '',
            'vision': '',
            'values': [],
            'history': '',
            'products_services': [],
            'product_categories': [],
            'certifications': [],
            'markets': [],
            'locations': [],
            'manufacturing': '',
            'leadership': [],
            'major_projects': [],
            'clients': [],
            'clients_text': '',
            'usps': [],
            'corporate_structure': '',
            'key_facts': [],
            'contact_info': {},
            'raw_sections': []  # Store all identified sections dynamically
        }
        
        # Use LLM for intelligent extraction if available (PRIMARY METHOD)
        if llm_service and text:
            try:
                enhanced_data = EnhancedCompanyParser._extract_with_llm(text, llm_service)
                # Use LLM-extracted data as primary source
                for key, value in enhanced_data.items():
                    if key in data and value:
                        data[key] = value
            except Exception as e:
                print(f"LLM extraction failed, falling back to pattern matching: {e}")
        
        # Fallback: Pattern-based extraction (if LLM fails or not available)
        # This is now a backup, not the primary method
        if not data.get('company_name') or not data.get('about_us'):
            sections = EnhancedCompanyParser._identify_sections_dynamic(text)
            data['raw_sections'] = sections
            
            # Try to intelligently map sections
            for section in sections:
                title = section.get('title', '').lower()
                content = section.get('content', '')
                
                # Be flexible with matching - use multiple keywords
                if not data['company_name']:
                    data['company_name'] = EnhancedCompanyParser._extract_company_name(text)
                
                if not data['about_us'] and any(kw in title for kw in ['about', 'overview', 'introduction', 'profile', 'who we are']):
                    data['about_us'] = content
                
                if not data['ceo_message'] and any(kw in title for kw in ['message', 'ceo', 'chairman', 'president', 'director', 'founder']):
                    data['ceo_message'] = content
                
                if not data['mission'] and 'mission' in title:
                    data['mission'] = content
                
                if not data['vision'] and 'vision' in title:
                    data['vision'] = content
                
                if not data['history'] and any(kw in title for kw in ['history', 'heritage', 'background', 'story', 'journey']):
                    data['history'] = content
                
                if any(kw in title for kw in ['product', 'service', 'offering', 'solution', 'what we do', 'our work']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['products_services'].extend(items)
                
                if any(kw in title for kw in ['market', 'industry', 'sector', 'serve']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['markets'].extend(items)
                
                if any(kw in title for kw in ['location', 'office', 'presence', 'branch', 'where we are']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['locations'].extend(items)
                
                if any(kw in title for kw in ['team', 'leadership', 'management', 'people', 'executive']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['leadership'].extend(items)
                
                if any(kw in title for kw in ['project', 'work', 'portfolio', 'experience', 'case']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['major_projects'].extend(items)
                
                if any(kw in title for kw in ['client', 'customer', 'partner', 'who we serve', 'our clients', 'clientele']):
                    items = EnhancedCompanyParser._extract_list_items(content)
                    if items:
                        data['clients'].extend(items)
                    # Also store full text if it's substantial
                    if len(content) > 50 and not data.get('clients_text'):
                        data['clients_text'] = content
        
        # Extract founding year if not found
        if not data.get('founded'):
            year_match = re.search(r'\b(19|20)\d{2}\b', text[:2000])
            if year_match:
                data['founded'] = year_match.group(0)
        
        # Extract industry if not found
        if not data.get('industry'):
            data['industry'] = EnhancedCompanyParser._infer_industry(text)
        
        # Generate key facts from all available data
        data['key_facts'] = EnhancedCompanyParser._generate_key_facts(data)
        
        # Clean up duplicates in lists
        for key in ['products_services', 'markets', 'locations', 'leadership', 'major_projects', 'clients', 'values', 'usps']:
            if isinstance(data[key], list):
                data[key] = list(dict.fromkeys(data[key]))  # Remove duplicates while preserving order
        
        return data
    
    @staticmethod
    def _identify_sections_dynamic(text: str) -> List[Dict[str, str]]:
        """
        Dynamically identify sections from any brochure format
        Uses heuristics to detect headers without assuming specific keywords
        """
        sections = []
        current_section = {'title': 'Introduction', 'content': ''}
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            is_likely_header = False
            
            # Heuristics for detecting headers (GENERALIZED):
            # 1. Short line (< 80 chars)
            # 2. All uppercase OR Title Case
            # 3. No punctuation at end (no . or ,)
            # 4. Not too short (> 3 chars)
            # 5. Followed by longer text OR blank line
            
            if 3 < len(line) < 80:
                has_end_punctuation = line.endswith(('.', ',', ';', ':', '!', '?'))
                is_uppercase = line.isupper()
                is_title_case = line.istitle() or (line[0].isupper() and len(line.split()) <= 8)
                
                # Check next line context
                next_line_longer = (i + 1 < len(lines) and len(lines[i + 1]) > len(line))
                
                if not has_end_punctuation and (is_uppercase or is_title_case) and (next_line_longer or i == 0):
                    is_likely_header = True
            
            if is_likely_header:
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section)
                # Start new section
                current_section = {'title': line, 'content': ''}
            else:
                # Add to current section content
                current_section['content'] += line + '\n'
        
        # Add last section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    @staticmethod
    def _extract_list_items(text: str) -> List[str]:
        """Extract list items from text (bullets, numbers, or sentences)"""
        items = []
        
        # Try to find bullet points or numbered lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove common list markers
            line = re.sub(r'^[•\-\*\d+\.]\s*', '', line)
            
            if len(line) > 10 and len(line) < 500:  # Reasonable length
                items.append(line)
        
        # If no items found, split by sentences
        if not items:
            sentences = re.split(r'[.!?]\s+', text)
            items = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return items[:10]  # Limit to 10 items
    
    @staticmethod
    def _extract_company_name(text: str) -> str:
        """Extract company name from text"""
        # Look for patterns like "Company Name", "[Name] is", "[Name] has been"
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            # All caps line might be company name
            if line.isupper() and 3 < len(line.split()) < 6:
                return line.strip()
            
            # Pattern: "X is a company" or "X was founded"
            match = re.search(r'^([A-Z][A-Za-z\s&]+?)\s+(is|was|has been)', line)
            if match:
                return match.group(1).strip()
        
        return ''
    
    @staticmethod
    def _extract_with_llm(text: str, llm_service) -> Dict:
        """
        Use LLM to intelligently extract company information from ANY format
        This is the PRIMARY method - it understands context and structure dynamically
        """
        import json
        
        # Use first 8000 chars for better coverage (clients might be later in doc)
        text_sample = text[:8000] if len(text) > 8000 else text
        
        prompt = f"""You are an intelligent document analyzer. Extract ALL relevant company information from this document.

IMPORTANT: 
- Extract WHATEVER information is actually present in the document
- Don't assume specific sections exist
- Be flexible with what you find
- If a field is not present, use empty string or empty array
- Extract the ACTUAL content, don't make up information

Document Text:
{text_sample}

Return a JSON object with these fields (only include what you actually find):
{{
    "company_name": "Exact company name from document",
    "tagline": "Tagline/slogan if present",
    "industry": "Industry/sector (infer from context if not explicit)",
    "founded": "Year founded (just the year)",
    "ceo_message": "CEO/leadership message content (NOT just heading)",
    "about_us": "Company description/overview content",
    "mission": "Mission statement (full text)",
    "vision": "Vision statement (full text)",
    "values": ["value 1", "value 2", ...],
    "history": "Historical information or company story",
    "products_services": ["product 1", "service 1", ...],
    "product_categories": ["category 1", "category 2", ...],
    "certifications": ["cert 1", "cert 2", ...],
    "markets": ["market/industry served 1", "market 2", ...],
    "locations": ["location 1", "location 2", ...],
    "manufacturing": "Manufacturing/operations details",
    "leadership": ["name/role 1", "name/role 2", ...],
    "major_projects": ["project 1", "project 2", ...],
    "clients": ["client 1", "client 2", ...],
    "clients_text": "Full text description of clients, partnerships, customer base, client testimonials, etc. Extract ALL client-related information even if it's in paragraph form.",
    "usps": ["unique point 1", "advantage 1", ...]
}}

Remember: Extract what's ACTUALLY there, not what you think should be there."""

        try:
            from config import Config
            response = llm_service.client.chat.completions.create(
                model=Config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyzer. Extract information dynamically based on what's present in the document. Work with any format, structure, or style. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Lower temperature for accuracy
                max_tokens=2000  # More tokens for comprehensive extraction
            )
            
            content = response.choices[0].message.content.strip()
            # Clean any markdown formatting
            content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {}
    
    @staticmethod
    def _infer_industry(text: str) -> str:
        """Infer industry from text content using keywords"""
        text_lower = text.lower()
        
        # Industry keyword mapping
        industries = {
            'Technology': ['software', 'tech', 'ai', 'digital', 'cloud', 'saas', 'platform'],
            'Manufacturing': ['manufacturing', 'production', 'factory', 'assembly', 'industrial'],
            'Healthcare': ['healthcare', 'medical', 'hospital', 'pharma', 'clinic', 'health'],
            'Finance': ['financial', 'banking', 'investment', 'insurance', 'fintech'],
            'Retail': ['retail', 'store', 'shop', 'ecommerce', 'merchandise'],
            'Construction': ['construction', 'building', 'infrastructure', 'contractor'],
            'Energy': ['energy', 'power', 'oil', 'gas', 'renewable', 'solar', 'utility'],
            'Automotive': ['automotive', 'vehicle', 'car', 'automobile', 'motor'],
            'Telecommunications': ['telecom', 'network', 'connectivity', 'wireless'],
            'Education': ['education', 'learning', 'training', 'school', 'university'],
            'Consulting': ['consulting', 'advisory', 'consulting services', 'professional services']
        }
        
        # Count matches for each industry
        matches = {}
        for industry, keywords in industries.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                matches[industry] = count
        
        # Return industry with most matches
        if matches:
            return max(matches, key=matches.get)
        
        return ''
    
    @staticmethod
    def _generate_key_facts(data: Dict) -> List[str]:
        """Generate key facts list dynamically from available data"""
        facts = []
        
        # Add facts based on what's available
        if data.get('founded'):
            facts.append(f"Established in {data['founded']}")
        
        if data.get('industry'):
            facts.append(f"Specializing in {data['industry']}")
        
        if data.get('locations') and len(data['locations']) > 0:
            loc_count = len(data['locations'])
            if loc_count == 1:
                facts.append(f"Located in {data['locations'][0]}")
            else:
                facts.append(f"Operating across {loc_count} locations")
        
        if data.get('products_services') and len(data['products_services']) > 0:
            count = len(data['products_services'])
            facts.append(f"{count}+ products and services")
        
        if data.get('clients') and len(data['clients']) > 2:
            facts.append(f"Trusted by {len(data['clients'])}+ clients")
        
        if data.get('certifications') and len(data['certifications']) > 0:
            facts.append(f"{len(data['certifications'])} industry certifications")
        
        if data.get('markets') and len(data['markets']) > 0:
            facts.append(f"Serving {len(data['markets'])} market sectors")
        
        # Add top 2-3 USPs if available
        if data.get('usps'):
            for usp in data['usps'][:3]:
                if usp and len(usp) < 100:  # Only short USPs
                    facts.append(usp)
        
        # Add top 2 values if available
        if data.get('values'):
            for value in data['values'][:2]:
                if value and len(value) < 100:
                    facts.append(f"Core value: {value}")
        
        return facts[:10]  # Return top 10 facts

