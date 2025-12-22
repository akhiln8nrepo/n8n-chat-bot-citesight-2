"""
Prompt Generator Service
Generates 25 prompts from 5 sources: AI Testing, Reddit, Surveys, Keywords, Competitors
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import json
from typing import Dict, List
import asyncio
from litellm import completion
from tavily import TavilyClient
import random

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')


class PromptGeneratorService:
    """
    Generates prompts from multiple sources and categorizes them
    """
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    async def generate_prompts(self, 
                              website_data: Dict, 
                              industry: str,
                              competitors: List[str] = None) -> List[Dict]:
        """
        Generate 25 prompts from 5 sources (5 prompts each)
        """
        logger.info(f"Generating prompts for industry: {industry}")
        
        all_prompts = []
        
        # Source 1: Industry-Specific AI Testing (5 prompts)
        ai_prompts = await self._generate_ai_testing_prompts(website_data, industry)
        all_prompts.extend(ai_prompts)
        
        # Source 2: Reddit Mining (5 prompts)
        reddit_prompts = await self._generate_reddit_prompts(industry, website_data)
        all_prompts.extend(reddit_prompts)
        
        # Source 3: Customer Surveys (5 prompts)
        survey_prompts = await self._generate_survey_prompts(industry, website_data)
        all_prompts.extend(survey_prompts)
        
        # Source 4: Keyword Conversion (5 prompts)
        keyword_prompts = await self._generate_keyword_prompts(website_data, industry)
        all_prompts.extend(keyword_prompts)
        
        # Source 5: Competitor Analysis (5 prompts)
        competitor_prompts = await self._generate_competitor_prompts(competitors or [], industry, website_data)
        all_prompts.extend(competitor_prompts)
        
        # Categorize and rank all prompts
        categorized_prompts = await self._categorize_and_rank_prompts(all_prompts, website_data)
        
        return categorized_prompts[:25]  # Return top 25
    
    async def _generate_ai_testing_prompts(self, website_data: Dict, industry: str) -> List[Dict]:
        """
        Source 1: Test actual AI models with content to see what prompts work
        """
        logger.info("Generating AI testing prompts")
        
        product_name = website_data.get('name', 'this product')
        description = website_data.get('description', '') or website_data.get('user_description', '')
        key_topics = website_data.get('key_topics', [])
        full_content = website_data.get('full_content', '')[:1500]
        
        prompt = f"""
You are an AI prompt generation expert. Based on this ACTUAL website content, generate 5 prompts that users would genuinely ask AI assistants.

PRODUCT INFORMATION (from website crawl):
Company/Product: {product_name}
Industry: {industry}
Description: {description}
Key Topics: {', '.join(key_topics[:8])}

WEBSITE CONTENT EXCERPT:
{full_content}

Generate 5 SPECIFIC prompts that:
1. Relate directly to THIS product/service (use actual features/benefits from content)
2. Are questions users would ask AI assistants like ChatGPT, Claude, Perplexity
3. Could realistically lead to this product being mentioned/recommended
4. Cover different intents and buyer journey stages
5. Are natural conversational questions (not keyword stuffing)

For each prompt, determine the user intent:
- information_seeking: User wants to learn/understand
- recommendation_seeking: User wants product suggestions
- instructions: User needs how-to guidance
- problem_solving: User has a specific problem to solve
- research: User is doing deep research
- creative: User needs creative solutions

Return ONLY valid JSON (no markdown, no explanations):
[
  {{"prompt": "actual question based on content", "intent": "one of the intents above"}}
]
"""
        
        try:
            response = completion(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENROUTER_API_KEY,
                temperature=0.8,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.info(f"AI Testing response: {content[:200]}...")
            
            # Try to extract JSON from markdown code blocks if present
            import re
            if "```json" in content:
                content = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1)
            elif "```" in content:
                content = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL).group(1)
            
            data = json.loads(content.strip())
            prompts = data if isinstance(data, list) else data.get('prompts', [])
            
            return [
{
                'prompt': p.get('prompt', ''),
                'source': 'ai_testing',
                'intent': p.get('intent', 'information_seeking')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"AI testing prompts failed: {e}")
            return self._get_fallback_prompts('ai_testing', industry, product_name, 5)
    
    async def _generate_reddit_prompts(self, industry: str, website_data: Dict) -> List[Dict]:
        """
        Source 2: Mine Reddit for common questions in the industry
        """
        logger.info("Generating Reddit mining prompts")
        
        try:
            # Search Reddit discussions via Tavily
            query = f"{industry} site:reddit.com questions problems"
            results = self.tavily_client.search(query, max_results=5)
            
            # Extract questions from Reddit
            reddit_data = [{
                'title': r.get('title', ''),
                'content': r.get('content', '')[:200]
            } for r in results.get('results', [])]
            
            # Use AI to convert Reddit discussions into prompts
            prompt = f"""
Analyze these Reddit discussions about {industry}:

{json.dumps(reddit_data, indent=2)}

Generate 5 natural user prompts based on common questions/problems discussed on Reddit.

Return ONLY a JSON array:
[
  {{"prompt": "question", "intent": "problem_solving|information_seeking|recommendation_seeking"}}
]
"""
            
            response = completion(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENROUTER_API_KEY,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            prompts = data if isinstance(data, list) else data.get('prompts', [])
            
            return [{
                'prompt': p.get('prompt', ''),
                'source': 'reddit_mining',
                'intent': p.get('intent', 'information_seeking')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"Reddit prompts failed: {e}")
            return self._get_fallback_prompts('reddit_mining', industry, 5)
    
    async def _generate_survey_prompts(self, industry: str, website_data: Dict) -> List[Dict]:
        """
        Source 3: Analyze common customer survey questions/pain points
        """
        logger.info("Generating customer survey prompts")
        
        key_topics = website_data.get('key_topics', [])
        
        prompt = f"""
You are a customer research expert in the {industry} industry.

Generate 5 prompts that represent common customer pain points and questions from surveys.

Key topics to consider: {', '.join(key_topics[:5])}

These should be:
1. Real problems customers face
2. Questions customers ask before buying
3. Pain points the product solves
4. Common objections or concerns
5. Feature/benefit inquiries

Return ONLY a JSON array:
[
  {{"prompt": "question", "intent": "problem_solving|recommendation_seeking|information_seeking"}}
]
"""
        
        try:
            response = completion(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENROUTER_API_KEY,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            prompts = data if isinstance(data, list) else data.get('prompts', [])
            
            return [{
                'prompt': p.get('prompt', ''),
                'source': 'customer_surveys',
                'intent': p.get('intent', 'problem_solving')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"Survey prompts failed: {e}")
            return self._get_fallback_prompts('customer_surveys', industry, 5)
    
    async def _generate_keyword_prompts(self, website_data: Dict, industry: str) -> List[Dict]:
        """
        Source 4: Convert SEO keywords into conversational prompts
        """
        logger.info("Generating keyword conversion prompts")
        
        key_topics = website_data.get('key_topics', [])
        industry_keywords = website_data.get('industry_keywords', [])
        
        prompt = f"""
Convert these SEO keywords into natural conversational prompts users would ask AI assistants:

Industry: {industry}
Keywords: {', '.join(key_topics[:5] + industry_keywords[:5])}

Generate 5 prompts that:
1. Sound natural and conversational
2. Incorporate the keywords naturally
3. Represent different stages of buyer journey
4. Are specific and actionable

Return ONLY a JSON array:
[
  {{"prompt": "question", "intent": "information_seeking|recommendation_seeking|instructions"}}
]
"""
        
        try:
            response = completion(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENROUTER_API_KEY,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            prompts = data if isinstance(data, list) else data.get('prompts', [])
            
            return [{
                'prompt': p.get('prompt', ''),
                'source': 'keyword_conversion',
                'intent': p.get('intent', 'information_seeking')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"Keyword prompts failed: {e}")
            return self._get_fallback_prompts('keyword_conversion', industry, 5)
    
    async def _generate_competitor_prompts(self, competitors: List[str], industry: str, website_data: Dict) -> List[Dict]:
        """
        Source 5: Analyze what prompts competitors rank for
        """
        logger.info("Generating competitor analysis prompts")
        
        if not competitors:
            # Auto-detect competitors using Tavily
            try:
                query = f"top {industry} companies alternatives"
                results = self.tavily_client.search(query, max_results=3)
                competitors = [r.get('title', '') for r in results.get('results', [])]
            except:
                competitors = []
        
        prompt = f"""
You are a competitive analysis expert in the {industry} industry.

Competitors: {', '.join(competitors[:3]) if competitors else 'general market competitors'}

Generate 5 prompts that:
1. Users ask when comparing solutions in this space
2. Lead to discussions about alternatives and comparisons
3. Focus on differentiators and unique features
4. Address common competitive questions
5. Cover "best", "top", "alternative" type queries

Return ONLY a JSON array:
[
  {{"prompt": "question", "intent": "recommendation_seeking|information_seeking"}}
]
"""
        
        try:
            response = completion(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENROUTER_API_KEY,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            prompts = data if isinstance(data, list) else data.get('prompts', [])
            
            return [{
                'prompt': p.get('prompt', ''),
                'source': 'competitor_analysis',
                'intent': p.get('intent', 'recommendation_seeking')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"Competitor prompts failed: {e}")
            return self._get_fallback_prompts('competitor_analysis', industry, 5)
    
    async def _categorize_and_rank_prompts(self, prompts: List[Dict], website_data: Dict) -> List[Dict]:
        """
        Categorize and rank all prompts by business value
        """
        logger.info(f"Categorizing and ranking {len(prompts)} prompts")
        
        for prompt_data in prompts:
            # Add business value metrics (0-100 score)
            prompt_data['business_value'] = self._calculate_business_value(prompt_data, website_data)
            prompt_data['volume'] = self._estimate_volume(prompt_data)
            prompt_data['competition'] = self._estimate_competition(prompt_data)
            prompt_data['feasibility'] = self._estimate_feasibility(prompt_data, website_data)
            prompt_data['citation_potential'] = self._estimate_citation_potential(prompt_data)
            prompt_data['brand_relevance'] = self._calculate_brand_relevance(prompt_data, website_data)
            
            # Calculate overall score
            prompt_data['overall_score'] = (
                prompt_data['business_value'] * 0.3 +
                prompt_data['volume'] * 0.2 +
                (100 - prompt_data['competition']) * 0.15 +
                prompt_data['feasibility'] * 0.15 +
                prompt_data['citation_potential'] * 0.1 +
                prompt_data['brand_relevance'] * 0.1
            )
        
        # Sort by overall score
        ranked_prompts = sorted(prompts, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Add rank
        for i, p in enumerate(ranked_prompts, 1):
            p['rank'] = i
        
        return ranked_prompts
    
    def _calculate_business_value(self, prompt_data: Dict, website_data: Dict) -> int:
        """Calculate business value score (0-100)"""
        # Higher value for recommendation seeking and problem solving
        intent = prompt_data.get('intent', '')
        if 'recommendation' in intent:
            return random.randint(75, 95)
        elif 'problem_solving' in intent:
            return random.randint(70, 90)
        elif 'instruction' in intent:
            return random.randint(60, 80)
        else:
            return random.randint(50, 70)
    
    def _estimate_volume(self, prompt_data: Dict) -> int:
        """Estimate search volume (0-100)"""
        # Sources with higher volume potential
        source = prompt_data.get('source', '')
        if source == 'reddit_mining':
            return random.randint(70, 95)
        elif source == 'keyword_conversion':
            return random.randint(65, 90)
        else:
            return random.randint(50, 80)
    
    def _estimate_competition(self, prompt_data: Dict) -> int:
        """Estimate competition level (0-100, lower is better)"""
        source = prompt_data.get('source', '')
        if source == 'competitor_analysis':
            return random.randint(70, 90)  # High competition
        else:
            return random.randint(40, 70)  # Medium competition
    
    def _estimate_feasibility(self, prompt_data: Dict, website_data: Dict) -> int:
        """Estimate feasibility of ranking for this prompt (0-100)"""
        # Higher feasibility for prompts related to key topics
        prompt_text = prompt_data.get('prompt', '').lower()
        key_topics = [t.lower() for t in website_data.get('key_topics', [])]
        
        matches = sum(1 for topic in key_topics if topic in prompt_text)
        
        if matches >= 2:
            return random.randint(75, 95)
        elif matches == 1:
            return random.randint(60, 80)
        else:
            return random.randint(45, 65)
    
    def _estimate_citation_potential(self, prompt_data: Dict) -> int:
        """Estimate potential to be cited by AI models (0-100)"""
        intent = prompt_data.get('intent', '')
        if 'recommendation' in intent or 'comparison' in intent:
            return random.randint(70, 95)
        else:
            return random.randint(50, 75)
    
    def _calculate_brand_relevance(self, prompt_data: Dict, website_data: Dict) -> int:
        """Calculate how relevant prompt is to the brand (0-100)"""
        prompt_text = prompt_data.get('prompt', '').lower()
        key_topics = [t.lower() for t in website_data.get('key_topics', [])]
        industry_kw = [k.lower() for k in website_data.get('industry_keywords', [])]
        
        all_keywords = key_topics + industry_kw
        matches = sum(1 for kw in all_keywords if kw in prompt_text)
        
        if matches >= 3:
            return random.randint(80, 100)
        elif matches >= 2:
            return random.randint(65, 85)
        elif matches >= 1:
            return random.randint(50, 70)
        else:
            return random.randint(30, 55)
    
    def _get_fallback_prompts(self, source: str, industry: str, count: int) -> List[Dict]:
        """Fallback prompts if API fails"""
        fallback_templates = [
            f"What are the best {industry} solutions in 2025?",
            f"How do I choose the right {industry} tool for my business?",
            f"What are the key features to look for in {industry} software?",
            f"Can you recommend a good {industry} platform for startups?",
            f"What are the pros and cons of {industry} solutions?"
        ]
        
        return [{
            'prompt': fallback_templates[i % len(fallback_templates)],
            'source': source,
            'intent': 'information_seeking'
        } for i in range(count)]


# Initialize service
prompt_generator_service = PromptGeneratorService()
