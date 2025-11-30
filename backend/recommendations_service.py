"""
Content Recommendations Generator for CiteSight
Generates comprehensive recommendations based on templates and keyword analysis
"""
import os
import json
import logging
from typing import Dict, List
from openai import OpenAI
from templates_service import BASE_TEMPLATE, get_template

logger = logging.getLogger(__name__)

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get('OPENROUTER_API_KEY')
)


async def generate_comprehensive_recommendations(
    content_text: str,
    title: str,
    keyword: str,
    template_id: str = "base",
    keyword_analysis: Dict = None
) -> Dict:
    """
    Generate comprehensive recommendations for content optimization
    Returns: header, subject_line, body_improvements, credibility_signals, faqs, schema, etc.
    """
    try:
        logger.info(f"Generating recommendations for content using template: {template_id}")
        
        template = get_template(template_id)
        
        # Prepare context
        keyword_context = ""
        if keyword_analysis:
            keyword_context = f"""
KEYWORD ANALYSIS INSIGHTS:
- Coverage Score: {keyword_analysis.get('coverage_score', 0)}%
- Missing Questions: {len(keyword_analysis.get('missing_questions', []))}
- Recommendations: {', '.join(keyword_analysis.get('recommendations', [])[:3])}
"""
        
        prompt = f"""You are a content optimization expert. Analyze the following content and provide comprehensive recommendations based on the {template['name']}.

CURRENT CONTENT:
Title: {title}
Keyword: {keyword}
Content: {content_text[:2000]}

{keyword_context}

TEMPLATE GUIDELINES:
{json.dumps(template.get('guidelines', {}), indent=2)}

Provide recommendations in the following JSON format:
{{
    "optimized_header": "Improved H1 header following guidelines",
    "subject_line": "SEO-optimized subject line",
    "body_improvements": [
        {{"section": "Introduction", "current": "...", "recommended": "...", "reason": "..."}},
        {{"section": "Main Content", "current": "...", "recommended": "...", "reason": "..."}}
    ],
    "credibility_signals": [
        {{"type": "Author Credentials", "recommendation": "Add author bio with expertise", "priority": "high"}},
        {{"type": "Citations", "recommendation": "Add 3-5 authoritative sources", "priority": "high"}}
    ],
    "faqs": [
        {{"question": "What is...", "answer": "Concise answer..."}},
        {{"question": "How to...", "answer": "Step-by-step answer..."}}
    ],
    "schema_markup": {{
        "article": {{"@type": "Article", "headline": "...", "author": "..."}},
        "faqpage": {{"@type": "FAQPage", "mainEntity": []}}
    }},
    "semantic_chunks": [
        {{"title": "Introduction to {keyword}", "content": "...", "keywords": []}},
        {{"title": "How {keyword} Works", "content": "...", "keywords": []}}
    ],
    "keyword_optimization": {{
        "primary_keyword_usage": "Current: X%, Recommended: 1-2%",
        "lsi_keywords": ["keyword1", "keyword2", "keyword3"],
        "placement_improvements": ["Add keyword to first paragraph", "Include in H2 tags"]
    }},
    "implementation_priority": [
        {{"item": "Add credibility signals", "impact": "high", "effort": "low"}},
        {{"item": "Optimize headers", "impact": "high", "effort": "low"}}
    ]
}}

Be specific and actionable. Focus on improvements that will increase AI visibility."""

        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert content optimizer specializing in AI visibility. Return ONLY valid JSON, no markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Clean up potential markdown formatting
        import re
        if "```json" in content:
            content = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1)
        elif "```" in content:
            content = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL).group(1)
        
        recommendations = json.loads(content.strip())
        
        logger.info("Comprehensive recommendations generated successfully")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        # Return fallback recommendations
        return {
            "optimized_header": f"Complete Guide to {keyword}: Everything You Need to Know",
            "subject_line": f"{keyword} 2025: Expert Recommendations and Guide",
            "body_improvements": [
                {"section": "Introduction", "current": "Generic intro", "recommended": "Add hook and problem statement", "reason": "Improve engagement"}
            ],
            "credibility_signals": [
                {"type": "Sources", "recommendation": "Add 3-5 authoritative citations", "priority": "high"}
            ],
            "faqs": [
                {"question": f"What is the best {keyword}?", "answer": "Provide expert recommendation based on research."}
            ],
            "schema_markup": {"article": {"@type": "Article"}},
            "semantic_chunks": [],
            "keyword_optimization": {
                "primary_keyword_usage": "Optimize to 1-2%",
                "lsi_keywords": [keyword, f"{keyword} guide", f"best {keyword}"],
                "placement_improvements": ["Add keyword to introduction"]
            },
            "implementation_priority": [
                {"item": "Add FAQs", "impact": "high", "effort": "low"}
            ]
        }


async def apply_recommendations(content_text: str, title: str, recommendations: Dict) -> Dict:
    """
    Apply all recommendations to the content automatically
    Returns optimized version of the content
    """
    try:
        logger.info("Applying recommendations to content")
        
        prompt = f"""Apply the following recommendations to improve this content:

CURRENT CONTENT:
Title: {title}
Content: {content_text}

RECOMMENDATIONS:
{json.dumps(recommendations, indent=2)}

Create an optimized version incorporating ALL recommendations. Return in JSON format:
{{
    "optimized_title": "New optimized title",
    "optimized_content": "Full optimized content with all improvements applied",
    "changes_summary": [
        "Added credibility signals",
        "Optimized headers",
        "Included FAQs",
        "Improved keyword placement"
    ]
}}

Make the content comprehensive, authoritative, and optimized for AI visibility."""

        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert content optimizer. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        logger.info(f"OpenRouter response: {content[:200]}...")
        
        # Try to extract JSON from markdown code blocks if present
        import re
        if "```json" in content:
            content = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1)
        elif "```" in content:
            content = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL).group(1)
        
        optimized = json.loads(content.strip())
        
        logger.info("Recommendations applied successfully")
        return optimized
        
    except Exception as e:
        logger.error(f"Error applying recommendations: {e}")
        return {
            "optimized_title": title,
            "optimized_content": content_text,
            "changes_summary": ["Error applying recommendations"]
        }


async def generate_model_specific_recommendations(
    content_text: str,
    title: str,
    keyword: str,
    model_id: str
) -> Dict:
    """
    Generate recommendations specific to an AI model
    """
    template = get_template(model_id)
    
    try:
        prompt = f"""Analyze this content specifically for optimization for {template['name']}:

CONTENT:
Title: {title}
Keyword: {keyword}
Content: {content_text[:1500]}

MODEL-SPECIFIC GUIDELINES:
{json.dumps(template.get('specific_guidelines', {}), indent=2)}

Provide model-specific recommendations in JSON format:
{{
    "model_name": "{template['name']}",
    "alignment_score": <0-100>,
    "key_improvements": [
        {{"area": "...", "current": "...", "recommendation": "...", "impact": "high/medium/low"}}
    ],
    "model_specific_tips": ["tip1", "tip2", "tip3"]
}}"""

        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an expert in optimizing content for {template['name']}. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Error generating model-specific recommendations: {e}")
        return {
            "model_name": template['name'],
            "alignment_score": 50,
            "key_improvements": [],
            "model_specific_tips": []
        }
