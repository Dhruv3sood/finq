"""Tools for PPT generation pipeline"""
from typing import Dict, Any, List, Optional
import json
import re
from config import Config


class FinancialAnalyzerTool:
    """Tool for analyzing financial data and extracting insights"""
    
    @staticmethod
    def analyze_balance_sheet(balance_data: Dict, metrics: Dict) -> Dict[str, Any]:
        """
        Analyze balance sheet and extract key insights
        
        Args:
            balance_data: Parsed balance sheet data
            metrics: Calculated financial metrics
            
        Returns:
            Dictionary with analysis results
        """
        insights = {
            'strengths': [],
            'concerns': [],
            'key_metrics': {},
            'trends': []
        }
        
        # Analyze asset distribution
        total_assets = metrics.get('total_assets', 0)
        current_assets = metrics.get('current_assets', 0)
        
        if total_assets > 0:
            current_ratio_pct = (current_assets / total_assets) * 100
            insights['key_metrics']['current_assets_percentage'] = current_ratio_pct
            
            if current_ratio_pct > 50:
                insights['strengths'].append(f"Strong liquidity with {current_ratio_pct:.1f}% current assets")
            elif current_ratio_pct < 30:
                insights['concerns'].append(f"Low liquidity at {current_ratio_pct:.1f}% current assets")
        
        # Analyze debt levels
        debt_to_equity = metrics.get('debt_to_equity', 0)
        if debt_to_equity > 0:
            insights['key_metrics']['debt_to_equity'] = debt_to_equity
            
            if debt_to_equity < 1:
                insights['strengths'].append(f"Conservative debt levels (D/E: {debt_to_equity:.2f})")
            elif debt_to_equity > 2:
                insights['concerns'].append(f"High leverage (D/E: {debt_to_equity:.2f})")
        
        # Analyze current ratio
        current_ratio = metrics.get('current_ratio', 0)
        if current_ratio > 0:
            insights['key_metrics']['current_ratio'] = current_ratio
            
            if current_ratio > 2:
                insights['strengths'].append(f"Excellent short-term solvency (Current Ratio: {current_ratio:.2f})")
            elif current_ratio < 1:
                insights['concerns'].append(f"Potential liquidity issues (Current Ratio: {current_ratio:.2f})")
        
        # Overall health assessment
        strength_count = len(insights['strengths'])
        concern_count = len(insights['concerns'])
        
        if strength_count > concern_count:
            insights['overall_health'] = 'Strong'
        elif concern_count > strength_count:
            insights['overall_health'] = 'Needs Attention'
        else:
            insights['overall_health'] = 'Moderate'
        
        return insights


class ContentStructurerTool:
    """Tool for structuring slide content"""
    
    @staticmethod
    def structure_executive_summary(analysis: Dict, context: str) -> Dict[str, Any]:
        """Structure executive summary content"""
        return {
            'title': 'Executive Summary',
            'highlights': [
                f"Overall Financial Health: {analysis.get('overall_health', 'Moderate')}",
                f"Key Strengths: {len(analysis.get('strengths', []))} identified",
                f"Areas of Focus: {len(analysis.get('concerns', []))} items",
                "Comprehensive financial position reviewed"
            ],
            'key_points': analysis.get('strengths', [])[:3],
            'context': context
        }
    
    @staticmethod
    def structure_financial_overview(metrics: Dict, context: str) -> Dict[str, Any]:
        """Structure financial overview content"""
        formatted_metrics = []
        
        metric_labels = {
            'total_assets': ('Total Assets', '$'),
            'total_liabilities': ('Total Liabilities', '$'),
            'total_equity': ('Total Equity', '$'),
            'current_ratio': ('Current Ratio', ''),
            'debt_to_equity': ('Debt-to-Equity Ratio', '')
        }
        
        for key, (label, prefix) in metric_labels.items():
            value = metrics.get(key, 0)
            if key in ['current_ratio', 'debt_to_equity']:
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = f"{prefix}{value:,.2f}" if value else "N/A"
            
            formatted_metrics.append({
                'label': label,
                'value': formatted_value,
                'trend': FinancialAnalyzerTool._determine_trend(key, value)
            })
        
        return {
            'title': 'Financial Overview',
            'metrics': formatted_metrics,
            'context': context
        }
    
    @staticmethod
    def structure_assets_breakdown(balance_data: Dict, metrics: Dict, context: str) -> Dict[str, Any]:
        """Structure assets breakdown content"""
        assets = balance_data.get('assets', {})
        total_assets = metrics.get('total_assets', 0)
        
        breakdown = []
        for key, value in sorted(assets.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (value / total_assets * 100) if total_assets > 0 else 0
            breakdown.append({
                'category': key.replace('_', ' ').title(),
                'amount': f"${value:,.2f}",
                'percentage': f"{percentage:.1f}%"
            })
        
        return {
            'title': 'Assets Breakdown',
            'total': f"${total_assets:,.2f}",
            'current': f"${metrics.get('current_assets', 0):,.2f}",
            'non_current': f"${metrics.get('non_current_assets', 0):,.2f}",
            'breakdown': breakdown,
            'insight': f"Assets are primarily composed of {breakdown[0]['category'].lower() if breakdown else 'various categories'}",
            'context': context
        }
    
    @staticmethod
    def structure_liabilities_analysis(balance_data: Dict, metrics: Dict, context: str) -> Dict[str, Any]:
        """Structure liabilities analysis content"""
        liabilities = balance_data.get('liabilities', {})
        total_liabilities = metrics.get('total_liabilities', 0)
        
        return {
            'title': 'Liabilities Analysis',
            'total': f"${total_liabilities:,.2f}",
            'current': f"${metrics.get('current_liabilities', 0):,.2f}",
            'long_term': f"${metrics.get('long_term_liabilities', 0):,.2f}",
            'debt_ratio': f"{metrics.get('debt_to_equity', 0):.2f}",
            'insight': FinancialAnalyzerTool._generate_debt_insight(metrics),
            'context': context
        }
    
    @staticmethod
    def structure_company_profile(company_data: Dict, context: str) -> Dict[str, Any]:
        """Structure company profile content"""
        return {
            'title': 'Company Profile',
            'company_name': company_data.get('company_name', 'Company Name'),
            'industry': company_data.get('industry', 'N/A'),
            'founded': company_data.get('founded', 'N/A'),
            'mission': company_data.get('mission', ''),
            'key_facts': company_data.get('key_facts', [])[:4],
            'context': context
        }


class DataVisualizationTool:
    """Tool for generating data visualization specifications"""
    
    @staticmethod
    def create_pie_chart_spec(data: List[Dict], title: str) -> Dict[str, Any]:
        """Create specification for pie chart"""
        return {
            'type': 'pie',
            'title': title,
            'data': data,
            'config': {
                'show_percentages': True,
                'show_legend': True
            }
        }
    
    @staticmethod
    def create_bar_chart_spec(data: List[Dict], title: str, x_label: str, y_label: str) -> Dict[str, Any]:
        """Create specification for bar chart"""
        return {
            'type': 'bar',
            'title': title,
            'data': data,
            'config': {
                'x_label': x_label,
                'y_label': y_label,
                'show_values': True
            }
        }
    
    @staticmethod
    def create_comparison_chart(categories: List[str], values: List[float], title: str) -> Dict[str, Any]:
        """Create comparison chart specification"""
        data = [{'category': cat, 'value': val} for cat, val in zip(categories, values)]
        return {
            'type': 'comparison',
            'title': title,
            'data': data,
            'config': {
                'orientation': 'horizontal',
                'show_values': True
            }
        }


class SlideTemplateSelector:
    """Tool for selecting appropriate slide templates"""
    
    @staticmethod
    def select_template(slide_type: str, data_complexity: str = 'medium') -> Dict[str, Any]:
        """
        Select appropriate template based on slide type and data complexity
        
        Args:
            slide_type: Type of slide (executive, financials, etc.)
            data_complexity: low, medium, high
            
        Returns:
            Template specification
        """
        templates = {
            'title': {
                'layout': 'title_only',
                'sections': ['title', 'subtitle', 'metadata']
            },
            'executive': {
                'layout': 'bullet_points',
                'sections': ['title', 'highlights', 'key_points']
            },
            'financials': {
                'layout': 'two_column',
                'sections': ['title', 'metrics', 'chart']
            },
            'assets': {
                'layout': 'data_visualization',
                'sections': ['title', 'summary', 'breakdown', 'chart']
            },
            'liabilities': {
                'layout': 'comparison',
                'sections': ['title', 'metrics', 'comparison']
            },
            'company': {
                'layout': 'info_panel',
                'sections': ['title', 'overview', 'key_facts']
            },
            'ratios': {
                'layout': 'metric_cards',
                'sections': ['title', 'ratio_cards', 'interpretation']
            },
            'trends': {
                'layout': 'insight_focused',
                'sections': ['title', 'insights', 'recommendations']
            },
            'conclusion': {
                'layout': 'summary',
                'sections': ['title', 'summary', 'takeaways', 'next_steps']
            }
        }
        
        return templates.get(slide_type, templates['executive'])


# Helper methods for FinancialAnalyzerTool
def _determine_trend(metric_name: str, value: float) -> str:
    """Determine trend indicator for a metric"""
    if metric_name in ['total_assets', 'total_equity']:
        return 'positive' if value > 0 else 'neutral'
    elif metric_name == 'current_ratio':
        if value > 2:
            return 'positive'
        elif value < 1:
            return 'negative'
        else:
            return 'neutral'
    elif metric_name == 'debt_to_equity':
        if value < 1:
            return 'positive'
        elif value > 2:
            return 'negative'
        else:
            return 'neutral'
    return 'neutral'

def _generate_debt_insight(metrics: Dict) -> str:
    """Generate insight about debt structure"""
    debt_to_equity = metrics.get('debt_to_equity', 0)
    
    if debt_to_equity < 0.5:
        return "Strong equity position with minimal debt leverage"
    elif debt_to_equity < 1.0:
        return "Balanced capital structure with moderate debt levels"
    elif debt_to_equity < 2.0:
        return "Higher leverage - monitor debt service capacity"
    else:
        return "Significant leverage - debt management critical"

# Attach helper methods to FinancialAnalyzerTool
FinancialAnalyzerTool._determine_trend = staticmethod(_determine_trend)
FinancialAnalyzerTool._generate_debt_insight = staticmethod(_generate_debt_insight)

