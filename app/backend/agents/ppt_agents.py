"""Agents for PPT generation pipeline"""
from typing import Dict, Any, List, Optional
from agents.ppt_tools import (
    FinancialAnalyzerTool, ContentStructurerTool, 
    DataVisualizationTool, SlideTemplateSelector
)
from services.llm_service import LLMService
from config import Config
import json


class SlideContentAgent:
    """Agent for generating slide content using context and tools"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.analyzer = FinancialAnalyzerTool()
        self.structurer = ContentStructurerTool()
        self.viz_tool = DataVisualizationTool()
        self.template_selector = SlideTemplateSelector()
    
    def generate_slide_content(self, slide_type: str, balance_data: Dict, 
                               company_data: Dict, metrics: Dict,
                               enhanced_context: str = None,
                               company_profile_text: str = None) -> Dict[str, Any]:
        """
        Generate content for a specific slide type using tools and LLM
        
        Args:
            slide_type: Type of slide to generate
            balance_data: Parsed balance sheet data
            company_data: Parsed company profile data
            metrics: Calculated financial metrics
            enhanced_context: Optional enhanced context from agentic pipeline
            company_profile_text: Raw company profile/brochure text for LLM fallback
            
        Returns:
            Structured slide content
        """
        # Select appropriate template
        template = self.template_selector.select_template(slide_type)
        
        # Use tools to structure content based on slide type
        if slide_type == 'title':
            return self._generate_title_slide(company_data, template)
        elif slide_type == 'executive':
            return self._generate_executive_summary(balance_data, metrics, enhanced_context, template)
        elif slide_type == 'financials':
            return self._generate_financial_overview(metrics, enhanced_context, template)
        elif slide_type == 'assets':
            return self._generate_assets_slide(balance_data, metrics, enhanced_context, template)
        elif slide_type == 'liabilities':
            return self._generate_liabilities_slide(balance_data, metrics, enhanced_context, template)
        elif slide_type == 'ratios':
            return self._generate_ratios_slide(metrics, enhanced_context, template)
        elif slide_type == 'trends':
            return self._generate_trends_slide(balance_data, metrics, enhanced_context, template)
        elif slide_type == 'company':
            return self._generate_company_profile_slide(company_data, enhanced_context, template)
        elif slide_type == 'products_services':
            return self._generate_products_services_slide(company_data, enhanced_context, template, company_profile_text)
        elif slide_type == 'markets_locations':
            return self._generate_markets_locations_slide(company_data, enhanced_context, template, company_profile_text)
        elif slide_type == 'leadership':
            return self._generate_leadership_slide(company_data, enhanced_context, template, company_profile_text)
        elif slide_type == 'major_projects':
            return self._generate_major_projects_slide(company_data, enhanced_context, template, company_profile_text)
        elif slide_type == 'vision_mission':
            return self._generate_vision_mission_slide(company_data, enhanced_context, template, company_profile_text)
        elif slide_type == 'conclusion':
            return self._generate_conclusion_slide(balance_data, metrics, enhanced_context, template)
        else:
            return {'error': f'Unknown slide type: {slide_type}'}
    
    def _generate_title_slide(self, company_data: Dict, template: Dict) -> Dict[str, Any]:
        """Generate title slide"""
        return {
            'type': 'title',
            'template': template,
            'title': 'Financial Analysis Presentation',
            'subtitle': f"{company_data.get('company_name', 'Company Overview')}",
            'company_name': company_data.get('company_name', 'Company Name'),
            'date': 'Financial Year Analysis'
        }
    
    def _generate_executive_summary(self, balance_data: Dict, metrics: Dict, 
                                     context: str, template: Dict) -> Dict[str, Any]:
        """Generate executive summary slide using tools and LLM"""
        # Use analyzer tool to get insights
        analysis = self.analyzer.analyze_balance_sheet(balance_data, metrics)
        
        # Structure content using tool
        base_content = self.structurer.structure_executive_summary(analysis, context or '')
        
        # Enhance with LLM if context available
        if context:
            enhanced_highlights = self._enhance_with_llm(
                slide_type='executive',
                base_content=base_content,
                context=context
            )
            base_content['highlights'] = enhanced_highlights.get('highlights', base_content['highlights'])
        
        base_content['template'] = template
        base_content['type'] = 'executive'
        return base_content
    
    def _generate_financial_overview(self, metrics: Dict, context: str, template: Dict) -> Dict[str, Any]:
        """Generate financial overview slide"""
        base_content = self.structurer.structure_financial_overview(metrics, context or '')
        
        # Add visualization spec
        metric_data = [
            {'label': m['label'], 'value': m['value']} 
            for m in base_content['metrics'][:4]
        ]
        
        base_content['template'] = template
        base_content['type'] = 'financials'
        return base_content
    
    def _generate_assets_slide(self, balance_data: Dict, metrics: Dict, 
                                context: str, template: Dict) -> Dict[str, Any]:
        """Generate assets breakdown slide"""
        base_content = self.structurer.structure_assets_breakdown(
            balance_data, metrics, context or ''
        )
        
        # Add pie chart specification
        if base_content.get('breakdown'):
            chart_data = [
                {'label': item['category'], 'value': float(item['percentage'].rstrip('%'))}
                for item in base_content['breakdown']
            ]
            base_content['chart'] = self.viz_tool.create_pie_chart_spec(
                chart_data, 'Asset Distribution'
            )
        
        base_content['template'] = template
        base_content['type'] = 'assets'
        return base_content
    
    def _generate_liabilities_slide(self, balance_data: Dict, metrics: Dict, 
                                     context: str, template: Dict) -> Dict[str, Any]:
        """Generate liabilities analysis slide"""
        base_content = self.structurer.structure_liabilities_analysis(
            balance_data, metrics, context or ''
        )
        
        # Add comparison chart
        chart_data = [
            {'label': 'Current', 'value': metrics.get('current_liabilities', 0)},
            {'label': 'Long-term', 'value': metrics.get('long_term_liabilities', 0)}
        ]
        base_content['chart'] = self.viz_tool.create_comparison_chart(
            ['Current Liabilities', 'Long-term Liabilities'],
            [metrics.get('current_liabilities', 0), metrics.get('long_term_liabilities', 0)],
            'Liabilities Breakdown'
        )
        
        base_content['template'] = template
        base_content['type'] = 'liabilities'
        return base_content
    
    def _generate_ratios_slide(self, metrics: Dict, context: str, template: Dict) -> Dict[str, Any]:
        """Generate financial ratios slide"""
        ratios = [
            {
                'name': 'Current Ratio',
                'value': f"{metrics.get('current_ratio', 0):.2f}",
                'interpretation': self._interpret_current_ratio(metrics.get('current_ratio', 0)),
                'benchmark': '> 1.5 (Good)'
            },
            {
                'name': 'Debt-to-Equity',
                'value': f"{metrics.get('debt_to_equity', 0):.2f}",
                'interpretation': self._interpret_debt_to_equity(metrics.get('debt_to_equity', 0)),
                'benchmark': '< 1.0 (Conservative)'
            }
        ]
        
        # Enhance with LLM if context available
        if context:
            enhanced = self._enhance_ratios_with_llm(ratios, context)
            ratios = enhanced.get('ratios', ratios)
        
        return {
            'type': 'ratios',
            'template': template,
            'title': 'Financial Ratios',
            'ratios': ratios,
            'context': context or ''
        }
    
    def _generate_trends_slide(self, balance_data: Dict, metrics: Dict, 
                                context: str, template: Dict) -> Dict[str, Any]:
        """Generate trends and insights slide"""
        # Get analysis insights
        analysis = self.analyzer.analyze_balance_sheet(balance_data, metrics)
        
        insights = analysis.get('strengths', []) + analysis.get('concerns', [])
        
        # Generate recommendations based on analysis
        recommendations = self._generate_recommendations(analysis, context)
        
        return {
            'type': 'trends',
            'template': template,
            'title': 'Trends & Insights',
            'insights': insights[:4],
            'recommendations': recommendations[:3],
            'context': context or ''
        }
    
    def _generate_company_profile_slide(self, company_data: Dict, context: str, template: Dict) -> Dict[str, Any]:
        """Generate company profile slide"""
        base_content = self.structurer.structure_company_profile(company_data, context or '')
        base_content['template'] = template
        base_content['type'] = 'company'
        return base_content
    
    def _generate_products_services_slide(self, company_data: Dict, context: str, template: Dict, brochure_text: str = None) -> Dict[str, Any]:
        """Generate products & services slide - enhanced with LLM if data is sparse"""
        products = company_data.get('products_services', []) or []
        categories = company_data.get('product_categories', []) or []
        certifications = company_data.get('certifications', []) or []
        
        # Helper to ensure we have strings, not dicts
        def _ensure_strings(items):
            result = []
            for item in items:
                if isinstance(item, dict):
                    # Extract name or title if it's a dict
                    result.append(item.get('name') or item.get('title') or item.get('product') or str(item))
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        
        # If data is sparse, use LLM with full brochure text to generate comprehensive content
        if (not products or len(products) < 2) and brochure_text:
            enhanced_data = self._generate_slide_content_from_brochure(
                brochure_text,
                "products_services",
                "Generate comprehensive content for a Products & Services slide. Extract all products, services, product categories, and certifications. Return as JSON with 'products', 'categories', and 'certifications' arrays of strings. Be thorough and extract everything relevant."
            )
            if enhanced_data.get('products'):
                products.extend(_ensure_strings(enhanced_data['products']))
            if enhanced_data.get('categories'):
                categories.extend(_ensure_strings(enhanced_data['categories']))
            if enhanced_data.get('certifications'):
                certifications.extend(_ensure_strings(enhanced_data['certifications']))
        
        # Fallback to context if brochure_text not available
        elif (not products or len(products) < 2) and context:
            enhanced_data = self._extract_with_llm(
                context, 
                "Extract all products, services, and product categories mentioned. Return as JSON with 'products' and 'categories' arrays of strings."
            )
            if enhanced_data.get('products'):
                products.extend(_ensure_strings(enhanced_data['products']))
            if enhanced_data.get('categories'):
                categories.extend(_ensure_strings(enhanced_data['categories']))
        
        return {
            'type': 'products_services',
            'template': template,
            'title': 'Products & Services',
            'products': list(set([p for p in _ensure_strings(products) if p]))[:12],  # Remove duplicates and empty
            'categories': list(set([c for c in _ensure_strings(categories) if c]))[:10],
            'certifications': list(set([cert for cert in _ensure_strings(certifications) if cert]))[:10],
            'context': context or ''
        }
    
    def _generate_markets_locations_slide(self, company_data: Dict, context: str, template: Dict, brochure_text: str = None) -> Dict[str, Any]:
        """Generate markets & locations slide - enhanced with LLM if data is sparse"""
        markets = company_data.get('markets', []) or []
        locations = company_data.get('locations', []) or []
        manufacturing = company_data.get('manufacturing', '') or ''
        
        # Helper to ensure we have strings, not dicts
        def _ensure_strings(items):
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(item.get('name') or item.get('location') or item.get('market') or str(item))
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        
        # If data is sparse, use LLM with full brochure text
        if (not markets or len(markets) < 2) and brochure_text:
            enhanced_data = self._generate_slide_content_from_brochure(
                brochure_text,
                "markets_locations",
                "Generate comprehensive content for a Markets & Locations slide. Extract all markets served, industries, geographic locations, offices, and manufacturing details. Return as JSON with 'markets' and 'locations' as arrays of strings, and 'manufacturing' as a string. Be thorough."
            )
            if enhanced_data.get('markets'):
                markets.extend(_ensure_strings(enhanced_data['markets']))
            if enhanced_data.get('locations'):
                locations.extend(_ensure_strings(enhanced_data['locations']))
            if enhanced_data.get('manufacturing') and not manufacturing:
                manufacturing = enhanced_data['manufacturing'] if isinstance(enhanced_data['manufacturing'], str) else str(enhanced_data['manufacturing'])
        
        # Fallback to context
        elif (not markets or len(markets) < 2) and context:
            enhanced_data = self._extract_with_llm(
                context,
                "Extract all markets, industries, and geographic locations mentioned. Return as JSON with 'markets' and 'locations' arrays of strings."
            )
            if enhanced_data.get('markets'):
                markets.extend(_ensure_strings(enhanced_data['markets']))
            if enhanced_data.get('locations'):
                locations.extend(_ensure_strings(enhanced_data['locations']))
        
        return {
            'type': 'markets_locations',
            'template': template,
            'title': 'Markets & Locations',
            'markets': list(set([m for m in _ensure_strings(markets) if m]))[:12],
            'locations': list(set([l for l in _ensure_strings(locations) if l]))[:12],
            'manufacturing': manufacturing or company_data.get('about_us', '')[:400] or 'Manufacturing and operations details',
            'context': context or ''
        }
    
    def _generate_leadership_slide(self, company_data: Dict, context: str, template: Dict, brochure_text: str = None) -> Dict[str, Any]:
        """Generate leadership & team slide - enhanced with LLM if data is sparse"""
        leadership = company_data.get('leadership', []) or []
        ceo_message = company_data.get('ceo_message', '') or ''
        
        # Helper to ensure we have strings, not dicts
        def _ensure_strings(items):
            result = []
            for item in items:
                if isinstance(item, dict):
                    # Format as "Name - Role" if it's a dict
                    name = item.get('name') or item.get('Name') or ''
                    role = item.get('role') or item.get('Role') or item.get('title') or ''
                    if name and role:
                        result.append(f"{name} - {role}")
                    elif name:
                        result.append(name)
                    else:
                        result.append(str(item))
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        
        # If data is sparse, use LLM with full brochure text
        if (not leadership or len(leadership) < 2 or not ceo_message) and brochure_text:
            enhanced_data = self._generate_slide_content_from_brochure(
                brochure_text,
                "leadership",
                "Generate comprehensive content for a Leadership & Team slide. Extract all leadership team members with their roles (format: 'Name - Role'), executives, management, and the CEO's message. Return as JSON with 'leadership' as an array of strings and 'ceo_message' as a string. Be thorough and extract all leadership information."
            )
            if enhanced_data.get('leadership'):
                leadership.extend(_ensure_strings(enhanced_data['leadership']))
            if enhanced_data.get('ceo_message') and not ceo_message:
                ceo_message = enhanced_data['ceo_message'] if isinstance(enhanced_data['ceo_message'], str) else str(enhanced_data['ceo_message'])
        
        # Fallback to context
        elif (not leadership or len(leadership) < 2) and context:
            enhanced_data = self._extract_with_llm(
                context,
                "Extract all leadership team members, executives, and management names with their roles. Return as JSON with 'leadership' array of strings like 'Name - Role'."
            )
            if enhanced_data.get('leadership'):
                leadership.extend(_ensure_strings(enhanced_data['leadership']))
            if enhanced_data.get('ceo_message') and not ceo_message:
                msg = enhanced_data.get('ceo_message', '')
                ceo_message = msg if isinstance(msg, str) else str(msg)
        
        return {
            'type': 'leadership',
            'template': template,
            'title': 'Leadership & Team',
            'leadership': list(set([l for l in _ensure_strings(leadership) if l]))[:12],
            'ceo_message_summary': ceo_message[:600] + '...' if len(ceo_message) > 600 else (ceo_message or 'Leadership message and team information'),
            'context': context or ''
        }
    
    def _generate_major_projects_slide(self, company_data: Dict, context: str, template: Dict, brochure_text: str = None) -> Dict[str, Any]:
        """Generate major projects slide - enhanced with LLM if data is sparse"""
        projects = company_data.get('major_projects', []) or []
        clients = company_data.get('clients', []) or []
        clients_text = company_data.get('clients_text', '') or ''
        
        # Helper to ensure we have strings, not dicts
        def _ensure_strings(items):
            result = []
            for item in items:
                if isinstance(item, dict):
                    # Extract name, title, or project/client name from dict
                    result.append(item.get('name') or item.get('title') or item.get('project') or item.get('client') or str(item))
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        
        # If data is sparse, use LLM with full brochure text
        if (not projects or len(projects) < 2 or not clients or len(clients) < 2) and brochure_text:
            enhanced_data = self._generate_slide_content_from_brochure(
                brochure_text,
                "major_projects",
                "Generate comprehensive content for a Major Projects & Clients slide. Extract all major projects, notable work, case studies, client names, customer names, and partners mentioned. Return as JSON with 'projects' and 'clients' as arrays of strings. Be thorough and extract everything relevant."
            )
            if enhanced_data.get('projects'):
                projects.extend(_ensure_strings(enhanced_data['projects']))
            if enhanced_data.get('clients'):
                clients.extend(_ensure_strings(enhanced_data['clients']))
        
        # Fallback to context
        elif (not projects or len(projects) < 2) and context:
            enhanced_data = self._extract_with_llm(
                context,
                "Extract all major projects, notable work, and case studies mentioned. Return as JSON with 'projects' array of strings."
            )
            if enhanced_data.get('projects'):
                projects.extend(_ensure_strings(enhanced_data['projects']))
        
        # Extract clients from clients_text if available
        if (not clients or len(clients) < 2) and clients_text:
            enhanced_data = self._extract_with_llm(
                clients_text,
                "Extract all client names, customer names, and partners mentioned. Return as JSON with 'clients' array of strings."
            )
            if enhanced_data.get('clients'):
                clients.extend(_ensure_strings(enhanced_data['clients']))
        
        return {
            'type': 'major_projects',
            'template': template,
            'title': 'Major Projects & Clients',
            'projects': list(set([p for p in _ensure_strings(projects) if p]))[:12],
            'clients': list(set([c for c in _ensure_strings(clients) if c]))[:15],
            'context': context or ''
        }
    
    def _generate_vision_mission_slide(self, company_data: Dict, context: str, template: Dict, brochure_text: str = None) -> Dict[str, Any]:
        """Generate vision & mission slide - enhanced with LLM if data is sparse"""
        vision = company_data.get('vision', '') or ''
        mission = company_data.get('mission', '') or ''
        values = company_data.get('values', []) or []
        usps = company_data.get('usps', []) or []
        
        # Helper to ensure we have strings, not dicts
        def _ensure_strings(items):
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(item.get('value') or item.get('name') or item.get('usp') or str(item))
                elif isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        
        # If data is sparse, use LLM with full brochure text
        if (not vision and not mission and (not values or len(values) < 2)) and brochure_text:
            enhanced_data = self._generate_slide_content_from_brochure(
                brochure_text,
                "vision_mission",
                "Generate comprehensive content for a Vision, Mission & Values slide. Extract the company's vision statement, mission statement, core values, and unique selling points (USPs). Return as JSON with 'vision' (string), 'mission' (string), 'values' (array of strings), and 'usps' (array of strings) fields. Be thorough and extract all relevant information."
            )
            if enhanced_data.get('vision') and not vision:
                vision = enhanced_data['vision'] if isinstance(enhanced_data['vision'], str) else str(enhanced_data['vision'])
            if enhanced_data.get('mission') and not mission:
                mission = enhanced_data['mission'] if isinstance(enhanced_data['mission'], str) else str(enhanced_data['mission'])
            if enhanced_data.get('values'):
                values.extend(_ensure_strings(enhanced_data['values']))
            if enhanced_data.get('usps'):
                usps.extend(_ensure_strings(enhanced_data['usps']))
        
        # Fallback to context
        elif (not vision and not mission) and context:
            enhanced_data = self._extract_with_llm(
                context,
                "Extract the company vision statement and mission statement. Return as JSON with 'vision' and 'mission' strings."
            )
            if enhanced_data.get('vision') and not vision:
                vision = enhanced_data['vision'] if isinstance(enhanced_data['vision'], str) else str(enhanced_data['vision'])
            if enhanced_data.get('mission') and not mission:
                mission = enhanced_data['mission'] if isinstance(enhanced_data['mission'], str) else str(enhanced_data['mission'])
        
        return {
            'type': 'vision_mission',
            'template': template,
            'title': 'Vision, Mission & Values',
            'vision': vision or 'Our vision drives us forward',
            'mission': mission or 'Our mission guides our actions',
            'values': list(set([v for v in _ensure_strings(values) if v]))[:10],
            'usps': list(set([u for u in _ensure_strings(usps) if u]))[:8],
            'context': context or ''
        }
    
    def _generate_conclusion_slide(self, balance_data: Dict, metrics: Dict, 
                                    context: str, template: Dict) -> Dict[str, Any]:
        """Generate conclusion slide"""
        analysis = self.analyzer.analyze_balance_sheet(balance_data, metrics)
        
        # Generate summary
        summary = f"Financial analysis reveals {analysis.get('overall_health', 'moderate')} financial health with {len(analysis.get('strengths', []))} key strengths."
        
        # Key takeaways
        takeaways = [
            f"Overall Health: {analysis.get('overall_health', 'Moderate')}",
            f"Total Assets: ${metrics.get('total_assets', 0):,.2f}",
            f"Debt-to-Equity: {metrics.get('debt_to_equity', 0):.2f}"
        ]
        
        # Next steps
        next_steps = self._generate_next_steps(analysis, context)
        
        return {
            'type': 'conclusion',
            'template': template,
            'title': 'Conclusion & Next Steps',
            'summary': summary,
            'key_takeaways': takeaways,
            'next_steps': next_steps,
            'context': context or ''
        }
    
    def _extract_with_llm(self, text: str, instruction: str) -> Dict[str, Any]:
        """
        Extract structured data from text using LLM
        
        Args:
            text: Text to extract from
            instruction: Instruction for what to extract
            
        Returns:
            Dictionary with extracted data
        """
        try:
            prompt = f"""{instruction}

Text:
{text[:2000]}

Return ONLY valid JSON, no explanation:"""

            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from text. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            import json
            return json.loads(content)
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            return {}
    
    def _generate_slide_content_from_brochure(self, brochure_text: str, slide_type: str, instruction: str) -> Dict[str, Any]:
        """
        Generate comprehensive slide content from full brochure text using LLM
        This is similar to DocumentAnalysisTool but specialized for PPT slides
        
        Args:
            brochure_text: Full company brochure/profile text
            slide_type: Type of slide being generated
            instruction: Specific instruction for what to extract/generate
            
        Returns:
            Generated content as dictionary
        """
        try:
            # Use a larger chunk of text for comprehensive extraction (up to 8000 chars)
            text_chunk = brochure_text[:8000] if len(brochure_text) > 8000 else brochure_text
            
            prompt = f"""You are creating content for a PowerPoint slide about a company.

Slide Type: {slide_type}

{instruction}

Company Brochure/Profile Text:
{text_chunk}

Analyze the entire document and extract/generate comprehensive, meaningful content for this slide. 
Be thorough and extract ALL relevant information. If information is not explicitly stated, infer reasonable content based on the context.
Return ONLY valid JSON with the requested fields."""
            
            response = self.llm_service.client.chat.completions.create(
                model=Config.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing company documents and generating comprehensive, meaningful content for business presentations. Extract and generate all relevant information. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            import json
            return json.loads(content)
        except Exception as e:
            print(f"Warning: LLM slide content generation failed for {slide_type}: {e}")
            return {}
    
    def _enhance_with_llm(self, slide_type: str, base_content: Dict, context: str) -> Dict[str, Any]:
        """Use LLM to enhance content with context"""
        prompt = f"""Based on the following context and base content, enhance the highlights for a {slide_type} slide.
Make them more specific, actionable, and data-driven.

Context:
{context}

Base Highlights:
{json.dumps(base_content.get('highlights', []), indent=2)}

Return ONLY a JSON object with an array of 4-5 enhanced highlights:
{{
    "highlights": ["highlight 1", "highlight 2", "highlight 3", "highlight 4"]
}}"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating compelling presentation content. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
            return base_content
    
    def _enhance_ratios_with_llm(self, ratios: List[Dict], context: str) -> Dict[str, Any]:
        """Enhance ratio interpretations with context"""
        prompt = f"""Enhance the interpretation of these financial ratios based on the context.

Context:
{context}

Ratios:
{json.dumps(ratios, indent=2)}

Return ONLY a JSON object with enhanced ratios:
{{
    "ratios": [
        {{"name": "...", "value": "...", "interpretation": "enhanced interpretation", "benchmark": "..."}},
        ...
    ]
}}"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            print(f"Ratio enhancement failed: {e}")
            return {'ratios': ratios}
    
    def _generate_recommendations(self, analysis: Dict, context: str) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        concerns = analysis.get('concerns', [])
        if concerns:
            recommendations.append(f"Address {len(concerns)} identified areas of concern")
        
        if analysis.get('overall_health') == 'Strong':
            recommendations.append("Continue current financial management strategy")
            recommendations.append("Explore growth opportunities")
        elif analysis.get('overall_health') == 'Needs Attention':
            recommendations.append("Implement cost control measures")
            recommendations.append("Review debt management strategy")
        
        return recommendations
    
    def _generate_next_steps(self, analysis: Dict, context: str) -> List[str]:
        """Generate next steps based on analysis"""
        next_steps = [
            "Review quarterly financial performance",
            "Monitor key financial ratios",
            "Implement recommended actions"
        ]
        
        if analysis.get('concerns'):
            next_steps.append("Develop action plans for identified concerns")
        
        return next_steps
    
    def _interpret_current_ratio(self, ratio: float) -> str:
        """Interpret current ratio"""
        if ratio > 2:
            return "Excellent liquidity position"
        elif ratio > 1.5:
            return "Good short-term financial health"
        elif ratio > 1:
            return "Adequate liquidity"
        else:
            return "Potential liquidity concerns"
    
    def _interpret_debt_to_equity(self, ratio: float) -> str:
        """Interpret debt-to-equity ratio"""
        if ratio < 0.5:
            return "Conservative capital structure"
        elif ratio < 1:
            return "Balanced leverage"
        elif ratio < 2:
            return "Moderate leverage"
        else:
            return "High leverage - monitor closely"


class DataExtractionAgent:
    """Agent for extracting specific data for slides"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def extract_key_figures(self, context: str, slide_type: str) -> Dict[str, Any]:
        """Extract key figures from context for specific slide type"""
        prompt = f"""Extract key financial figures from the context for a {slide_type} slide.

Context:
{context}

Return ONLY a JSON object with relevant figures:
{{
    "figures": [
        {{"label": "figure name", "value": "numeric value with units"}},
        ...
    ]
}}"""
        
        try:
            response = self.llm_service.client.chat.completions.create(
                model=Config.SUMMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            print(f"Data extraction failed: {e}")
            return {'figures': []}


class QualityAssuranceAgent:
    """Agent for validating and improving slide quality"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def validate_slide_content(self, slide_content: Dict) -> Dict[str, Any]:
        """Validate slide content for completeness and quality"""
        issues = []
        suggestions = []
        
        # Check for required fields
        required_fields = ['type', 'title']
        for field in required_fields:
            if not slide_content.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Check content length
        if slide_content.get('type') == 'executive':
            highlights = slide_content.get('highlights', [])
            if len(highlights) < 3:
                suggestions.append("Add more highlights for comprehensive executive summary")
            elif len(highlights) > 6:
                suggestions.append("Consider reducing highlights for better readability")
        
        # Check for data validity
        if 'metrics' in slide_content:
            for metric in slide_content['metrics']:
                if metric.get('value') == 'N/A':
                    suggestions.append(f"Missing data for metric: {metric.get('label')}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions,
            'quality_score': self._calculate_quality_score(slide_content, issues, suggestions)
        }
    
    def _calculate_quality_score(self, content: Dict, issues: List, suggestions: List) -> float:
        """Calculate quality score for slide"""
        base_score = 100
        base_score -= len(issues) * 20  # Deduct for issues
        base_score -= len(suggestions) * 5  # Minor deduct for suggestions
        
        # Bonus for rich content
        if content.get('context'):
            base_score += 10
        if content.get('chart'):
            base_score += 10
        
        return max(0, min(100, base_score))

