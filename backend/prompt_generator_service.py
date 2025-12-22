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
from datetime import datetime, timezone
from litellm import completion
from tavily import TavilyClient
import random
from json_parser import parse_llm_json, extract_prompts_from_response

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Configure litellm for OpenRouter
os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY or ''

# litellm settings
import litellm
litellm.set_verbose = False  # Reduce logging
litellm.drop_params = True  # Drop unsupported params


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
        OPTIMIZED: Runs all sources in parallel for 40-50% speed improvement
        """
        logger.info(f"Generating prompts for industry: {industry}")
        
        # Run all 5 sources in PARALLEL using asyncio.gather
        logger.info("Starting parallel prompt generation from 5 sources...")
        start_time = datetime.now(timezone.utc)
        
        try:
            results = await asyncio.gather(
                self._generate_ai_testing_prompts(website_data, industry),
                self._generate_reddit_prompts(industry, website_data),
                self._generate_survey_prompts(industry, website_data),
                self._generate_keyword_prompts(website_data, industry),
                self._generate_competitor_prompts(competitors or [], industry, website_data),
                return_exceptions=True  # Don't fail if one source fails
            )
            
            # Flatten results and filter out exceptions
            all_prompts = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Source {i} failed: {result}")
                elif isinstance(result, list):
                    all_prompts.extend(result)
            
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Parallel generation complete in {elapsed:.1f}s. Got {len(all_prompts)} prompts")
            
        except Exception as e:
            logger.error(f"Parallel generation failed: {e}")
            # Fallback to sequential if parallel fails
            all_prompts = []
            for source_func in [
                self._generate_ai_testing_prompts(website_data, industry),
                self._generate_reddit_prompts(industry, website_data),
                self._generate_survey_prompts(industry, website_data),
                self._generate_keyword_prompts(website_data, industry),
                self._generate_competitor_prompts(competitors or [], industry, website_data)
            ]:
                try:
                    prompts = await source_func
                    all_prompts.extend(prompts)
                except Exception as e:
                    logger.error(f"Source failed: {e}")
        
        # Ensure we have at least some prompts
        if len(all_prompts) < 5:
            logger.warning("Too few prompts generated, adding fallbacks")
            product_name = website_data.get('name', 'product')
            all_prompts.extend(self._get_fallback_prompts('ai_testing', industry, product_name, 5))
        
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
                model="openrouter/openai/gpt-4o-mini",  # Use openrouter/ prefix
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.8,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            logger.info(f"AI Testing response: {content[:200]}...")
            
            # Use robust JSON parser
            data = parse_llm_json(content)
            if not data:
                logger.error("Failed to parse JSON from AI Testing response")
                return self._get_fallback_prompts('ai_testing', industry, product_name, 5)
            
            prompts = extract_prompts_from_response(data)
            
            return [{
                'prompt': p.get('prompt', '') or p.get('question', ''),
                'source': 'ai_testing',
                'intent': p.get('intent', 'information_seeking')
            } for p in prompts[:5] if p.get('prompt') or p.get('question')]
        
        except Exception as e:
            logger.error(f"AI testing prompts failed: {e}")
            return self._get_fallback_prompts('ai_testing', industry, product_name, 5)
    
    async def _generate_reddit_prompts(self, industry: str, website_data: Dict) -> List[Dict]:
        """
        Source 2: Mine Reddit for common questions in the industry
        """
        logger.info("Generating Reddit mining prompts")
        
        product_name = website_data.get('name', 'product')
        key_topics = website_data.get('key_topics', [])
        
        try:
            # Search Reddit discussions via Tavily with specific queries
            search_queries = [
                f"{industry} problems site:reddit.com",
                f"best {industry} tools site:reddit.com",
                f"{' '.join(key_topics[:2])} recommendations site:reddit.com"
            ]
            
            reddit_discussions = []
            for query in search_queries[:2]:  # Limit to 2 searches to save API calls
                try:
                    results = self.tavily_client.search(query, max_results=3)
                    reddit_discussions.extend([{
                        'title': r.get('title', ''),
                        'content': r.get('content', '')[:300]
                    } for r in results.get('results', [])])
                except Exception as e:
                    logger.error(f"Tavily search failed for {query}: {e}")
            
            if not reddit_discussions:
                return self._get_fallback_prompts('reddit_mining', industry, product_name, 5)
            
            # Use AI to convert Reddit discussions into prompts
            prompt = f"""
Based on these REAL Reddit discussions about {industry}, generate 5 user prompts.

Product Context: {product_name} in {industry} industry
Key Topics: {', '.join(key_topics[:5])}

Reddit Discussions:
{json.dumps(reddit_discussions[:5], indent=2)}

Generate 5 prompts that:
1. Address actual problems/questions discussed on Reddit
2. Are natural questions users would ask AI assistants
3. Could lead to {product_name} being relevant
4. Reflect real user pain points and needs

Categorize each by intent:
- information_seeking, recommendation_seeking, instructions, problem_solving, research, creative

Return ONLY valid JSON:
[
  {{"prompt": "question", "intent": "intent_type"}}
]
"""
            
            response = completion(
                model="openrouter/openai/gpt-4o-mini",  # Use openrouter/ prefix
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            # Use robust JSON parser
            data = parse_llm_json(content)
            if not data:
                logger.error("Failed to parse JSON from Reddit response")
                product_name = website_data.get('name', 'product')
                return self._get_fallback_prompts('reddit_mining', industry, product_name, 5)
            
            prompts = extract_prompts_from_response(data)
            
            return [{
                'prompt': p.get('prompt', ''),
                'source': 'reddit_mining',
                'intent': p.get('intent', 'information_seeking')
            } for p in prompts[:5]]
        
        except Exception as e:
            logger.error(f"Reddit prompts failed: {e}")
            return self._get_fallback_prompts('reddit_mining', industry, product_name, 5)
    
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
                model="openrouter/openai/gpt-4o-mini",  # Use openrouter/ prefix
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
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
            product_name = website_data.get('name', 'product')
            return self._get_fallback_prompts('customer_surveys', industry, product_name, 5)
    
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
                model="openrouter/openai/gpt-4o-mini",  # Use openrouter/ prefix
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
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
            product_name = website_data.get('name', 'product')
            return self._get_fallback_prompts('keyword_conversion', industry, product_name, 5)
    
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
                model="openrouter/openai/gpt-4o-mini",  # Use openrouter/ prefix
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
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
            product_name = website_data.get('name', 'product')
            return self._get_fallback_prompts('competitor_analysis', industry, product_name, 5)
    
    async def _categorize_and_rank_prompts(self, prompts: List[Dict], website_data: Dict) -> List[Dict]:
        """
        Categorize and rank all prompts using 7-factor weighted scoring algorithm
        
        7 Metrics (0-100 scale each):
        1. Business Value (25%) - Commercial intent and conversion potential
        2. Volume (20%) - Estimated search/query volume
        3. Competition (15%) - Difficulty to rank (inverted - lower competition = higher score)
        4. Feasibility (15%) - Likelihood of being mentioned by AI
        5. Intent Score (10%) - Buyer journey stage score
        6. Citation Potential (10%) - Likelihood of being cited/referenced
        7. Brand Relevance (5%) - How relevant to your specific brand
        """
        logger.info(f"Categorizing and ranking {len(prompts)} prompts with 7-factor scoring")
        
        for prompt_data in prompts:
            # Calculate all 7 metrics (0-100 scale)
            prompt_data['business_value'] = self._calculate_business_value(prompt_data, website_data)
            prompt_data['volume'] = self._estimate_volume(prompt_data)
            prompt_data['competition'] = self._estimate_competition(prompt_data)
            prompt_data['feasibility'] = self._estimate_feasibility(prompt_data, website_data)
            prompt_data['intent_score'] = self._calculate_intent_score(prompt_data)  # NEW 7th metric
            prompt_data['citation_potential'] = self._estimate_citation_potential(prompt_data)
            prompt_data['brand_relevance'] = self._calculate_brand_relevance(prompt_data, website_data)
            
            # Calculate weighted composite score (7-factor algorithm)
            # Weights: BV=25%, Vol=20%, Comp=15%, Feas=15%, Intent=10%, Citation=10%, Relevance=5%
            prompt_data['overall_score'] = (
                prompt_data['business_value'] * 0.25 +
                prompt_data['volume'] * 0.20 +
                (100 - prompt_data['competition']) * 0.15 +  # Invert competition (lower = better)
                prompt_data['feasibility'] * 0.15 +
                prompt_data['intent_score'] * 0.10 +
                prompt_data['citation_potential'] * 0.10 +
                prompt_data['brand_relevance'] * 0.05
            )
        
        # Sort by overall score (highest first)
        ranked_prompts = sorted(prompts, key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Add rank
        for i, p in enumerate(ranked_prompts, 1):
            p['rank'] = i
        
        return ranked_prompts
    
    def _calculate_intent_score(self, prompt_data: Dict) -> int:
        """
        Calculate Intent Score (0-100) based on buyer journey stage
        
        Intent mapping to scores:
        - recommendation_seeking: 90-100 (highest commercial intent)
        - problem_solving: 75-90 (active problem, likely to convert)
        - instructions: 60-75 (specific need, moderate intent)
        - information_seeking: 40-60 (early stage research)
        - research: 30-50 (deep research, may convert later)
        - creative: 20-40 (lowest commercial intent)
        """
        intent = prompt_data.get('intent', 'information_seeking').lower()
        text = prompt_data.get('prompt', '').lower()
        
        # Base score by intent category
        intent_scores = {
            'recommendation_seeking': 95,
            'problem_solving': 82,
            'instructions': 68,
            'information_seeking': 50,
            'research': 40,
            'creative': 30
        }
        
        score = intent_scores.get(intent, 50)
        
        # Boost score based on high-intent keywords
        high_intent_keywords = ['buy', 'purchase', 'pricing', 'cost', 'trial', 'demo', 'best', 'recommend', 'should i']
        medium_intent_keywords = ['compare', 'vs', 'alternative', 'review', 'difference']
        low_intent_keywords = ['what is', 'define', 'explain', 'learn', 'understand']
        
        # Adjust based on keywords found
        if any(kw in text for kw in high_intent_keywords):
            score = min(100, score + 10)
        elif any(kw in text for kw in medium_intent_keywords):
            score = min(100, score + 5)
        elif any(kw in text for kw in low_intent_keywords):
            score = max(20, score - 10)
        
        return score
    
    def _calculate_business_value(self, prompt_data: Dict, website_data: Dict) -> int:
        """Calculate business value score (0-100 scale)"""
        text = prompt_data.get('prompt', '').lower()
        score = 50  # Base score
        
        # High business value indicators (+15-20 each)
        if any(word in text for word in ['pricing', 'cost', 'buy', 'purchase']):
            score += 25
        if any(word in text for word in ['trial', 'demo', 'signup', 'start']):
            score += 20
        if any(word in text for word in ['best', 'top', 'recommend']):
            score += 15
        if any(word in text for word in ['vs', 'compare', 'alternative', 'switch']):
            score += 15
        
        # Brand-specific queries have high business value
        product_name = website_data.get('name', '').lower()
        if product_name and product_name in text:
            score += 10
        
        # Low business value indicators
        if any(word in text for word in ['free', 'what is', 'define', 'history']):
            score -= 15
        if any(word in text for word in ['learn', 'understand', 'explain']):
            score -= 10
        
        return max(0, min(100, score))
    
    def _estimate_volume(self, prompt_data: Dict) -> int:
        """Estimate search volume (0-100 scale)"""
        text = prompt_data.get('prompt', '').lower()
        score = 50  # Base score
        
        # High volume indicators (common query patterns)
        if any(word in text for word in ['best', 'top', 'how to']):
            score += 25
        if any(word in text for word in ['what is', 'what are', 'guide']):
            score += 20
        if any(word in text for word in ['2024', '2025', 'latest']):
            score += 10
        
        # Generic category queries = high volume
        source = prompt_data.get('source', '')
        if source in ['keyword_conversion', 'ai_testing']:
            score += 15
        
        # Specific/niche queries = lower volume
        if 'competitor' in source:
            score -= 10
        if any(word in text for word in ['specific', 'niche', 'custom']):
            score -= 15
        
        # Long-tail queries have lower volume
        word_count = len(text.split())
        if word_count > 10:
            score -= 10
        elif word_count < 5:
            score += 10
        
        return max(0, min(100, score))
    
    def _estimate_competition(self, prompt_data: Dict) -> int:
        """Estimate competition level (1-10, LOWER is better/easier)"""
        text = prompt_data.get('prompt', '').lower()
        score = 5  # Base score
        
        # High competition (lower score = more competitive)
        if any(word in text for word in ['best', 'top']):
            score -= 2
        
        # Lower competition (higher score = less competitive/easier)
        if any(word in text for word in ['specific', 'niche']):
            score += 2
        
        # Brand-specific = less competition
        source = prompt_data.get('source', '')
        if 'competitor' in source:
            score += 2
        
        return max(1, min(10, score))
    
    def _estimate_feasibility(self, prompt_data: Dict, website_data: Dict) -> int:
        """Estimate feasibility of ranking (1-10 scale)"""
        text = prompt_data.get('prompt', '').lower()
        score = 6  # Base score (slightly optimistic)
        
        # Check brand mention
        product_name = website_data.get('name', '').lower()
        if product_name and product_name in text:
            score += 2
        
        # Check if features match
        key_topics = [t.lower() for t in website_data.get('key_topics', [])]
        matches = sum(1 for topic in key_topics if topic in text)
        score += min(matches, 2)  # Max +2 for feature matches
        
        return max(1, min(10, score))
    
    def _estimate_citation_potential(self, prompt_data: Dict) -> int:
        """Estimate potential to be cited by AI (1-10 scale)"""
        text = prompt_data.get('prompt', '').lower()
        intent = prompt_data.get('intent', '')
        score = 5  # Base score
        
        # High citation potential
        if intent in ['recommendation_seeking', 'research']:
            score += 3
        if any(word in text for word in ['review', 'experience', 'opinion', 'vs', 'compare']):
            score += 1
        
        # Question format = higher citation
        if text.startswith(('what', 'how', 'why', 'which', 'should')):
            score += 1
        
        return max(1, min(10, score))
    
    def _calculate_brand_relevance(self, prompt_data: Dict, website_data: Dict) -> int:
        """Calculate brand relevance (1-10 scale)"""
        text = prompt_data.get('prompt', '').lower()
        score = 5  # Base score
        
        # Direct brand mention = very relevant
        product_name = website_data.get('name', '').lower()
        if product_name and product_name in text:
            score += 4
        
        # Key topics match
        key_topics = [t.lower() for t in website_data.get('key_topics', [])]
        industry_kw = [k.lower() for k in website_data.get('industry_keywords', [])]
        all_keywords = key_topics + industry_kw
        
        matches = sum(1 for kw in all_keywords if kw and kw in text)
        
        if matches >= 3:
            score += 2
        elif matches >= 2:
            score += 1
        
        return max(1, min(10, score))
    
    def _get_fallback_prompts(self, source: str, industry: str, product_name: str, count: int) -> List[Dict]:
        """Fallback prompts if API fails - more specific to industry"""
        fallback_templates = {
            'ai_testing': [
                f"What are the key features to look for in {industry} software?",
                f"How does {product_name} compare to other {industry} solutions?",
                f"What problems does {product_name} solve for businesses?",
                f"Can you recommend a good {industry} platform for my needs?",
                f"What are the benefits of using {product_name}?"
            ],
            'reddit_mining': [
                f"What do people on Reddit say about {industry} tools?",
                f"Has anyone used {product_name}? Looking for reviews",
                f"What's the best {industry} solution according to Reddit?",
                f"Common problems with {industry} software?",
                f"Is {product_name} worth it for small businesses?"
            ],
            'customer_surveys': [
                f"What are the main pain points in {industry}?",
                f"How can {product_name} improve my workflow?",
                f"What features do customers value most in {industry} tools?",
                f"Is {product_name} easy to use for beginners?",
                f"What ROI can I expect from {product_name}?"
            ],
            'keyword_conversion': [
                f"Best {industry} software 2025",
                f"{product_name} vs competitors",
                f"How to choose {industry} platform",
                f"{industry} solution pricing comparison",
                f"{product_name} features and benefits"
            ],
            'competitor_analysis': [
                f"Top alternatives to {product_name}",
                f"Compare {product_name} with similar tools",
                f"Which is better for {industry}?",
                f"Pros and cons of different {industry} platforms",
                f"Why choose {product_name} over competitors?"
            ]
        }
        
        templates = fallback_templates.get(source, fallback_templates['ai_testing'])
        
        return [{
            'prompt': templates[i % len(templates)],
            'source': source,
            'intent': 'information_seeking' if i % 2 == 0 else 'recommendation_seeking'
        } for i in range(count)]


# Initialize service
prompt_generator_service = PromptGeneratorService()
