"""
GEO Prompt Generation Framework
A Systematic 7-Layer Approach to Generate Highly Relevant Prompts for Any Company
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import json
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timezone
from litellm import completion
from tavily import TavilyClient
import re
from json_parser import parse_llm_json, extract_prompts_from_response

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Configure litellm for OpenRouter
os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY or ''

import litellm
litellm.set_verbose = False
litellm.drop_params = True


# ==========================================
# LAYER 1: COMPANY INTELLIGENCE
# ==========================================

class CompanyIntelligence:
    """Extract and structure company information from crawled data"""
    
    @staticmethod
    async def extract(crawl_data: Dict, user_input: Dict) -> Dict:
        """
        Extract comprehensive company intelligence from website crawl + user input
        
        Returns structured data about:
        - Basic company info
        - Business classification
        - Product categories
        - Key technologies/features
        - Competitors
        - Target markets
        """
        
        content = crawl_data.get('content', '')[:8000]
        title = crawl_data.get('title', '')
        description = crawl_data.get('metadata', {}).get('description', '')
        
        # Use LLM to extract structured company intelligence
        prompt = f"""
You are a business analyst extracting company intelligence from a website.

WEBSITE CONTENT:
Title: {title}
Description: {description}
Content excerpt:
{content[:4000]}

USER PROVIDED INFO:
- Industry: {user_input.get('industry', 'Unknown')}
- Product Description: {user_input.get('product_description', 'Not provided')}
- Competitors: {', '.join(user_input.get('competitors', []))}

Extract and return this JSON structure (be specific to THIS company):

{{
    "companyName": "extracted company name",
    "tagline": "company tagline or value proposition",
    "industry": "primary industry category",
    "secondaryIndustries": ["list of related industries"],
    "businessModel": "B2B, B2C, or both",
    "positioning": "how they position themselves (premium, budget, innovative, etc.)",
    
    "productCategories": [
        "main product/service category 1",
        "main product/service category 2"
    ],
    
    "specificProducts": [
        {{"name": "product name", "category": "category", "description": "brief description"}}
    ],
    
    "keyFeatures": [
        "unique feature or technology 1",
        "unique feature or technology 2"
    ],
    
    "uniqueSellingPoints": [
        "what makes them different 1",
        "what makes them different 2"
    ],
    
    "targetAudiences": [
        {{"persona": "audience name", "description": "who they are", "needs": "what they want"}}
    ],
    
    "competitiveAdvantages": [
        "advantage 1",
        "advantage 2"
    ],
    
    "useCases": [
        "use case 1",
        "use case 2"
    ],
    
    "pricePositioning": "budget/mid-range/premium/enterprise",
    
    "knownFor": [
        "what they're famous for"
    ]
}}

Return ONLY valid JSON, no markdown or explanation.
"""
        
        try:
            response = completion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            intel = parse_llm_json(content)
            
            if intel:
                # Merge with user-provided data
                intel['competitors'] = user_input.get('competitors', [])
                intel['userProvidedDescription'] = user_input.get('product_description', '')
                intel['userProvidedIndustry'] = user_input.get('industry', '')
                return intel
                
        except Exception as e:
            logger.error(f"Company intelligence extraction failed: {e}")
        
        # Fallback: basic structure from available data
        return {
            "companyName": title.split('|')[0].split('-')[0].strip() if title else "Company",
            "industry": user_input.get('industry', 'Technology'),
            "productCategories": [],
            "competitors": user_input.get('competitors', []),
            "userProvidedDescription": user_input.get('product_description', ''),
            "keyFeatures": [],
            "targetAudiences": [],
            "useCases": []
        }


# ==========================================
# LAYER 2: PRODUCT DECOMPOSITION  
# ==========================================

class ProductDecomposer:
    """Break down company products into searchable categories"""
    
    @staticmethod
    async def decompose(company_intel: Dict) -> Dict:
        """
        Create product hierarchy:
        - Categories
        - Sub-categories  
        - Specific products
        - Features/Technologies
        """
        
        prompt = f"""
Based on this company intelligence, create a product decomposition:

Company: {company_intel.get('companyName')}
Industry: {company_intel.get('industry')}
Products: {json.dumps(company_intel.get('specificProducts', []))}
Categories: {json.dumps(company_intel.get('productCategories', []))}
Features: {json.dumps(company_intel.get('keyFeatures', []))}
Description: {company_intel.get('userProvidedDescription', '')}

Return a JSON object with product hierarchy that customers would search for:

{{
    "mainCategories": ["category1", "category2"],
    "subCategories": {{
        "category1": ["subcategory1a", "subcategory1b"],
        "category2": ["subcategory2a", "subcategory2b"]
    }},
    "searchableProducts": [
        {{"name": "product", "category": "cat", "searchTerms": ["term1", "term2"]}}
    ],
    "technologies": ["tech1", "tech2"],
    "features": ["feature1", "feature2"],
    "useCases": ["use case 1", "use case 2"],
    "problemsSolved": ["problem1", "problem2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = completion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.3
            )
            
            return parse_llm_json(response.choices[0].message.content) or {}
            
        except Exception as e:
            logger.error(f"Product decomposition failed: {e}")
            return {}


# ==========================================
# LAYER 3: AUDIENCE MAPPING
# ==========================================

class AudienceMapper:
    """Identify customer personas and their search patterns"""
    
    @staticmethod
    async def map_audiences(company_intel: Dict) -> List[Dict]:
        """
        Create customer personas with their:
        - Demographics
        - Needs/Pain points
        - Search behavior
        - Prompt patterns
        """
        
        prompt = f"""
Create 4-5 customer personas for this company:

Company: {company_intel.get('companyName')}
Industry: {company_intel.get('industry')}
Products: {json.dumps(company_intel.get('productCategories', []))}
Target Audiences: {json.dumps(company_intel.get('targetAudiences', []))}
Use Cases: {json.dumps(company_intel.get('useCases', []))}

For each persona, think about how they would ask AI chatbots about products in this industry.

Return a JSON array:
[
    {{
        "personaName": "The Professional User",
        "description": "Who they are",
        "demographics": "age, role, income level",
        "needs": ["need1", "need2"],
        "painPoints": ["pain1", "pain2"],
        "searchBehavior": "how they search",
        "typicalQuestions": [
            "What is the best X for Y?",
            "How do I choose X?"
        ],
        "buyingStage": "awareness/consideration/decision",
        "priceIsSensitive": true/false
    }}
]

Return ONLY valid JSON array.
"""
        
        try:
            response = completion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.5
            )
            
            result = parse_llm_json(response.choices[0].message.content)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Audience mapping failed: {e}")
            return []


# ==========================================
# LAYER 4: INTENT CLASSIFICATION
# ==========================================

class IntentClassifier:
    """Classify prompts by search intent"""
    
    INTENT_TYPES = {
        'informational': {
            'signals': ['what is', 'how does', 'why', 'explain', 'meaning', 'definition'],
            'businessValue': 3,
            'stage': 'awareness'
        },
        'navigational': {
            'signals': ['official', 'website', 'login', 'contact'],
            'businessValue': 5,
            'stage': 'varies'
        },
        'commercial_investigation': {
            'signals': ['best', 'top', 'review', 'vs', 'compare', 'recommend', 'worth'],
            'businessValue': 8,
            'stage': 'consideration'
        },
        'transactional': {
            'signals': ['buy', 'purchase', 'price', 'cost', 'discount', 'sale', 'coupon', 'deal', 'order'],
            'businessValue': 10,
            'stage': 'decision'
        },
        'local': {
            'signals': ['near me', 'in my area', 'local', 'store'],
            'businessValue': 8,
            'stage': 'decision'
        },
        'support': {
            'signals': ['how to use', 'fix', 'problem', 'not working', 'return', 'warranty'],
            'businessValue': 4,
            'stage': 'retention'
        }
    }
    
    @classmethod
    def classify(cls, prompt_text: str) -> Dict:
        """Classify a prompt by intent"""
        text = prompt_text.lower()
        
        for intent_type, config in cls.INTENT_TYPES.items():
            if any(signal in text for signal in config['signals']):
                return {
                    'intent': intent_type,
                    'businessValue': config['businessValue'],
                    'stage': config['stage']
                }
        
        # Default to informational
        return {
            'intent': 'informational',
            'businessValue': 3,
            'stage': 'awareness'
        }


# ==========================================
# LAYER 5: PROMPT PATTERN MATCHING
# ==========================================

class PromptPatternGenerator:
    """Generate prompts using universal and industry-specific patterns"""
    
    # Universal prompt patterns that work for ANY company
    UNIVERSAL_PATTERNS = [
        # Pattern 1: Best + Category + Qualifier
        "Best {category} for {qualifier}",
        "Best {category} {year}",
        "Top {category} for {use_case}",
        
        # Pattern 2: Brand + Product + Question
        "{brand} {product} review",
        "Is {brand} {product} worth it?",
        "{brand} {product} good for {use_case}?",
        
        # Pattern 3: Product A vs Product B
        "{brand} vs {competitor}",
        "{brand} {product} vs {competitor_product}",
        "{brand} or {competitor} for {use_case}?",
        "Is {brand} better than {competitor}?",
        
        # Pattern 4: How to + Action
        "How to choose {category}",
        "How to use {brand} {product}",
        "How to {action} with {category}",
        
        # Pattern 5: Is/Are + Product + Qualifier
        "Are {brand} {category} good?",
        "Is {brand} {product} comfortable?",
        "Is {brand} reliable?",
        
        # Pattern 6: What + Question
        "What is the best {category}?",
        "What {category} should I buy?",
        "What is {brand} known for?",
        
        # Pattern 7: Category + for + Use Case
        "{category} for {use_case}",
        "{category} for {audience}",
        "Best {category} for {specific_need}",
        
        # Pattern 8: Why + Observation
        "Why is {brand} so popular?",
        "Why choose {brand} over {competitor}?",
        "Why are {brand} {category} expensive?",
        
        # Pattern 9: Where + Action
        "Where to buy {brand} {product}",
        "Where to find {category} on sale",
        "{brand} {product} discount code",
        
        # Pattern 10: Problem-focused
        "Best {category} for {problem}",
        "{category} that solves {problem}",
        "Help with {problem} - what {category} to use?"
    ]
    
    @classmethod
    async def generate_prompts(cls, company_intel: Dict, products: Dict, audiences: List[Dict]) -> List[Dict]:
        """Generate prompts using all patterns"""
        
        prompts = []
        brand = company_intel.get('companyName', 'Brand')
        industry = company_intel.get('industry', 'Industry')
        categories = products.get('mainCategories', []) or company_intel.get('productCategories', [])
        competitors = company_intel.get('competitors', [])
        features = products.get('features', []) or company_intel.get('keyFeatures', [])
        use_cases = products.get('useCases', []) or company_intel.get('useCases', [])
        problems = products.get('problemsSolved', [])
        
        year = "2024"
        
        # ============================================
        # SOURCE 1: CATEGORY SEARCH (Industry-level queries)
        # What customers ask about the INDUSTRY in general
        # ============================================
        for category in categories[:8]:
            prompts.extend([
                # Discovery patterns
                {"prompt": f"Best {category} {year}", "source": "category_search", "category": category},
                {"prompt": f"Top rated {category}", "source": "category_search", "category": category},
                {"prompt": f"What is the best {category}?", "source": "category_search", "category": category},
                {"prompt": f"Top 10 {category} {year}", "source": "category_search", "category": category},
                # Buying patterns
                {"prompt": f"How to choose {category}", "source": "category_search", "category": category},
                {"prompt": f"{category} buying guide", "source": "category_search", "category": category},
                {"prompt": f"What to look for in {category}", "source": "category_search", "category": category},
                # Comparison patterns
                {"prompt": f"Best {category} brands", "source": "category_search", "category": category},
                {"prompt": f"{category} comparison {year}", "source": "category_search", "category": category},
            ])
        
        # ============================================
        # SOURCE 2: PRODUCT DISCOVERY (Brand + Product specific)
        # Queries about specific products the brand offers
        # ============================================
        specific_products = products.get('searchableProducts', [])
        for prod in specific_products[:10]:
            prod_name = prod.get('name', '')
            if prod_name:
                prompts.extend([
                    {"prompt": f"{brand} {prod_name} review", "source": "product_discovery", "product": prod_name},
                    {"prompt": f"Is {brand} {prod_name} worth it?", "source": "product_discovery", "product": prod_name},
                    {"prompt": f"{brand} {prod_name} pros and cons", "source": "product_discovery", "product": prod_name},
                    {"prompt": f"{brand} {prod_name} {year} review", "source": "product_discovery", "product": prod_name},
                    {"prompt": f"Should I buy {brand} {prod_name}?", "source": "product_discovery", "product": prod_name},
                ])
        
        # Brand-level discovery
        prompts.extend([
            {"prompt": f"{brand} review", "source": "product_discovery", "product": "brand"},
            {"prompt": f"Is {brand} a good brand?", "source": "product_discovery", "product": "brand"},
            {"prompt": f"{brand} quality review", "source": "product_discovery", "product": "brand"},
            {"prompt": f"Best {brand} products {year}", "source": "product_discovery", "product": "brand"},
            {"prompt": f"{brand} {year} lineup", "source": "product_discovery", "product": "brand"},
            {"prompt": f"What is {brand} known for?", "source": "product_discovery", "product": "brand"},
        ])
        
        # ============================================
        # SOURCE 3: COMPETITOR COMPARISON
        # Brand vs Competitor queries (high business value)
        # ============================================
        for competitor in competitors[:5]:
            prompts.extend([
                # Direct comparisons
                {"prompt": f"{brand} vs {competitor}", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"{brand} vs {competitor} {year}", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"Is {brand} better than {competitor}?", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"{brand} or {competitor} - which is better?", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"{brand} vs {competitor} comparison", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"Why choose {brand} over {competitor}?", "source": "competitor_comparison", "competitor": competitor},
                {"prompt": f"{competitor} alternative", "source": "competitor_comparison", "competitor": competitor},
            ])
            
            # Category-specific comparisons
            for category in categories[:3]:
                prompts.extend([
                    {"prompt": f"{brand} vs {competitor} {category}", "source": "competitor_comparison", "competitor": competitor},
                    {"prompt": f"Best {category}: {brand} or {competitor}?", "source": "competitor_comparison", "competitor": competitor},
                ])
        
        # ============================================
        # SOURCE 4: USE CASE QUERIES
        # Queries for specific activities/needs
        # ============================================
        for use_case in use_cases[:10]:
            prompts.extend([
                {"prompt": f"Best {categories[0] if categories else 'product'} for {use_case}", "source": "use_case", "use_case": use_case},
                {"prompt": f"{categories[0] if categories else 'product'} for {use_case}", "source": "use_case", "use_case": use_case},
                {"prompt": f"What {categories[0] if categories else 'product'} for {use_case}?", "source": "use_case", "use_case": use_case},
            ])
            
            # Cross with multiple categories
            for category in categories[1:4]:
                prompts.append({
                    "prompt": f"Best {category} for {use_case}",
                    "source": "use_case",
                    "use_case": use_case
                })
        
        # ============================================
        # SOURCE 5: PERSONA-BASED QUERIES
        # Questions different customer types ask
        # ============================================
        for audience in audiences[:5]:
            persona = audience.get('personaName', '')
            needs = audience.get('needs', [])
            questions = audience.get('typicalQuestions', [])
            pain_points = audience.get('painPoints', [])
            
            # Persona questions
            for question in questions[:5]:
                prompts.append({
                    "prompt": question.replace('X', categories[0] if categories else 'product'),
                    "source": "persona_based",
                    "persona": persona
                })
            
            # Need-based queries
            for need in needs[:3]:
                prompts.extend([
                    {"prompt": f"Best {categories[0] if categories else 'solution'} for {need}", "source": "persona_based", "persona": persona},
                    {"prompt": f"{categories[0] if categories else 'product'} that helps with {need}", "source": "persona_based", "persona": persona},
                ])
            
            # Pain point queries
            for pain in pain_points[:3]:
                prompts.append({
                    "prompt": f"Best {categories[0] if categories else 'solution'} for {pain}",
                    "source": "persona_based",
                    "persona": persona
                })
        
        # ============================================
        # SOURCE 6: PROBLEM/SOLUTION QUERIES
        # Pain point and solution-focused queries
        # ============================================
        for problem in problems[:8]:
            prompts.extend([
                {"prompt": f"How to solve {problem}", "source": "problem_solution", "problem": problem},
                {"prompt": f"Best solution for {problem}", "source": "problem_solution", "problem": problem},
                {"prompt": f"Help with {problem}", "source": "problem_solution", "problem": problem},
                {"prompt": f"{problem} solutions {year}", "source": "problem_solution", "problem": problem},
            ])
        
        # ============================================
        # SOURCE 7: FEATURE/TECHNOLOGY QUERIES
        # Queries about specific features or technologies
        # ============================================
        for feature in features[:8]:
            prompts.extend([
                {"prompt": f"What is {feature}?", "source": "feature_discovery", "feature": feature},
                {"prompt": f"{feature} explained", "source": "feature_discovery", "feature": feature},
                {"prompt": f"Is {feature} worth it?", "source": "feature_discovery", "feature": feature},
                {"prompt": f"Best {categories[0] if categories else 'product'} with {feature}", "source": "feature_discovery", "feature": feature},
            ])
        
        # ============================================
        # SOURCE 8: TRANSACTIONAL QUERIES
        # High-intent purchase queries
        # ============================================
        prompts.extend([
            {"prompt": f"Where to buy {brand}", "source": "transactional", "type": "purchase"},
            {"prompt": f"{brand} discount code {year}", "source": "transactional", "type": "discount"},
            {"prompt": f"{brand} sale {year}", "source": "transactional", "type": "sale"},
            {"prompt": f"{brand} price", "source": "transactional", "type": "price"},
            {"prompt": f"Best {brand} deals", "source": "transactional", "type": "deals"},
            {"prompt": f"{brand} coupon code", "source": "transactional", "type": "coupon"},
            {"prompt": f"Cheapest place to buy {brand}", "source": "transactional", "type": "price"},
        ])
        
        for category in categories[:3]:
            prompts.extend([
                {"prompt": f"Where to buy {category}", "source": "transactional", "type": "purchase"},
                {"prompt": f"{category} on sale", "source": "transactional", "type": "sale"},
                {"prompt": f"Cheap {category}", "source": "transactional", "type": "budget"},
                {"prompt": f"Best {category} under $100", "source": "transactional", "type": "budget"},
            ])
        
        # ============================================
        # SOURCE 9: SUPPORT/HOW-TO QUERIES
        # Customer support and usage queries
        # ============================================
        prompts.extend([
            {"prompt": f"How to use {brand}", "source": "support", "type": "usage"},
            {"prompt": f"{brand} return policy", "source": "support", "type": "returns"},
            {"prompt": f"{brand} warranty", "source": "support", "type": "warranty"},
            {"prompt": f"{brand} customer service", "source": "support", "type": "service"},
            {"prompt": f"How to contact {brand}", "source": "support", "type": "contact"},
        ])
        
        for category in categories[:3]:
            prompts.extend([
                {"prompt": f"How to clean {category}", "source": "support", "type": "care"},
                {"prompt": f"How to maintain {category}", "source": "support", "type": "care"},
                {"prompt": f"{category} sizing guide", "source": "support", "type": "sizing"},
            ])
        
        # Remove duplicates
        seen = set()
        unique_prompts = []
        for p in prompts:
            if p['prompt'].lower() not in seen:
                seen.add(p['prompt'].lower())
                unique_prompts.append(p)
        
        return unique_prompts[:150]  # Return up to 150 for scoring, top 100 will be kept


# ==========================================
# LAYER 6: COMPETITIVE CONTEXT
# ==========================================

class CompetitiveAnalyzer:
    """Analyze competitive context for prompts"""
    
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    async def analyze_competition(self, prompt_text: str, brand: str) -> Dict:
        """
        Analyze who else answers this prompt in AI/search results
        Returns competition level and opportunity assessment
        """
        # Simple heuristic-based analysis
        text = prompt_text.lower()
        
        competition_score = 50  # Base
        
        # Brand-specific queries have less competition
        if brand.lower() in text:
            competition_score -= 20
        
        # "Best" queries are highly competitive
        if text.startswith('best'):
            competition_score += 25
        
        # Comparison queries are moderately competitive
        if ' vs ' in text or 'compare' in text:
            competition_score += 15
        
        # Long-tail queries have less competition
        word_count = len(text.split())
        if word_count > 8:
            competition_score -= 15
        
        return {
            'competitionScore': min(100, max(0, competition_score)),
            'difficulty': 'high' if competition_score > 70 else 'medium' if competition_score > 40 else 'low'
        }


# ==========================================
# LAYER 7: RELEVANCE SCORING
# ==========================================

class RelevanceScorer:
    """
    Score prompts using the 7-factor model:
    - Brand Relevance (20%)
    - Business Value (25%)
    - Search Volume (15%)
    - Competition Difficulty (10%)
    - Feasibility (10%)
    - Citation Potential (15%)
    - Conversion Intent (5%)
    """
    
    WEIGHTS = {
        'brandRelevance': 0.20,
        'businessValue': 0.25,
        'searchVolume': 0.15,
        'competitionDifficulty': 0.10,
        'feasibility': 0.10,
        'citationPotential': 0.15,
        'conversionIntent': 0.05
    }
    
    def __init__(self, company_intel: Dict):
        self.company = company_intel
        self.brand = company_intel.get('companyName', '').lower()
        self.categories = [c.lower() for c in company_intel.get('productCategories', [])]
        self.features = [f.lower() for f in company_intel.get('keyFeatures', [])]
        self.competitors = [c.lower() for c in company_intel.get('competitors', [])]
    
    def score_prompt(self, prompt_data: Dict) -> Dict:
        """Score a single prompt"""
        text = prompt_data.get('prompt', '').lower()
        
        scores = {
            'brandRelevance': self._score_brand_relevance(text),
            'businessValue': self._score_business_value(text),
            'searchVolume': self._score_search_volume(text),
            'competitionDifficulty': self._score_competition(text),
            'feasibility': self._score_feasibility(text),
            'citationPotential': self._score_citation_potential(text),
            'conversionIntent': self._score_conversion_intent(text)
        }
        
        # Calculate weighted composite score (0-100)
        composite = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        
        # Classify intent
        intent_info = IntentClassifier.classify(text)
        
        return {
            **prompt_data,
            'scores': scores,
            'overall_score': round(composite, 1),
            'intent': intent_info['intent'],
            'buyerStage': intent_info['stage'],
            'tier': self._get_tier(composite)
        }
    
    def _score_brand_relevance(self, text: str) -> int:
        """Score 0-100: How relevant is this prompt to the brand?"""
        score = 30  # Base
        
        # Direct brand mention
        if self.brand and self.brand in text:
            score += 40
        
        # Category match
        for cat in self.categories:
            if cat in text:
                score += 15
                break
        
        # Feature mention
        for feat in self.features:
            if feat in text:
                score += 10
                break
        
        # Competitor mention (still relevant for comparison)
        for comp in self.competitors:
            if comp in text:
                score += 5
                break
        
        return min(100, score)
    
    def _score_business_value(self, text: str) -> int:
        """Score 0-100: How valuable is this prompt for business?"""
        score = 40  # Base
        
        # Transactional signals (highest value)
        if any(w in text for w in ['buy', 'purchase', 'price', 'cost', 'discount', 'order']):
            score += 40
        
        # Commercial investigation signals
        elif any(w in text for w in ['best', 'top', 'review', 'recommend', 'worth it']):
            score += 30
        
        # Comparison signals
        elif any(w in text for w in ['vs', 'compare', 'better than', 'or']):
            score += 25
        
        # Low value signals
        if any(w in text for w in ['what is', 'history', 'meaning', 'definition']):
            score -= 20
        
        # Brand-specific adds value
        if self.brand and self.brand in text:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_search_volume(self, text: str) -> int:
        """Score 0-100: Estimated search volume"""
        score = 50  # Base
        
        # Generic high-volume patterns
        if any(w in text for w in ['best', 'top', 'how to']):
            score += 25
        
        # Category queries have good volume
        for cat in self.categories:
            if cat in text:
                score += 15
                break
        
        # Long-tail = lower volume
        word_count = len(text.split())
        if word_count > 10:
            score -= 20
        elif word_count > 7:
            score -= 10
        elif word_count < 4:
            score += 10
        
        return min(100, max(0, score))
    
    def _score_competition(self, text: str) -> int:
        """Score 0-100: Inverted competition (higher = easier to win)"""
        score = 50  # Base
        
        # Brand-specific = easier
        if self.brand and self.brand in text:
            score += 25
        
        # Generic "best" = harder
        if text.startswith('best') and self.brand not in text:
            score -= 20
        
        # Long-tail = easier
        word_count = len(text.split())
        if word_count > 7:
            score += 15
        
        # Competitor mention = moderate
        for comp in self.competitors:
            if comp in text:
                score -= 5
                break
        
        return min(100, max(0, score))
    
    def _score_feasibility(self, text: str) -> int:
        """Score 0-100: How feasible is it for this brand to rank?"""
        score = 50  # Base
        
        # Brand has authority on brand queries
        if self.brand and self.brand in text:
            score += 30
        
        # Feature expertise
        for feat in self.features:
            if feat in text:
                score += 15
                break
        
        # Category expertise
        for cat in self.categories:
            if cat in text:
                score += 15
                break
        
        return min(100, max(0, score))
    
    def _score_citation_potential(self, text: str) -> int:
        """Score 0-100: How likely is AI to cite the brand?"""
        score = 40  # Base
        
        # Brand is THE authority
        if self.brand and self.brand in text:
            score += 35
        
        # Feature/technology ownership
        for feat in self.features:
            if feat in text:
                score += 20
                break
        
        # Category expertise
        for cat in self.categories:
            if cat in text:
                score += 10
                break
        
        # Review/comparison queries drive citations
        if any(w in text for w in ['review', 'vs', 'compare', 'recommend']):
            score += 10
        
        return min(100, max(0, score))
    
    def _score_conversion_intent(self, text: str) -> int:
        """Score 0-100: Conversion intent"""
        # Decision stage
        if any(w in text for w in ['buy', 'purchase', 'order', 'where to get', 'price']):
            return 95
        
        # Consideration stage
        if any(w in text for w in ['best', 'vs', 'compare', 'review', 'worth', 'recommend']):
            return 70
        
        # Retention stage
        if any(w in text for w in ['how to use', 'clean', 'fix', 'return']):
            return 50
        
        # Awareness stage
        return 35
    
    def _get_tier(self, score: float) -> str:
        """Assign tier based on composite score"""
        if score >= 75:
            return 'TIER_1_CRITICAL'
        elif score >= 60:
            return 'TIER_2_HIGH'
        elif score >= 45:
            return 'TIER_3_MEDIUM'
        return 'TIER_4_LOW'


# ==========================================
# MAIN PROMPT GENERATOR SERVICE
# ==========================================

class GEOPromptGeneratorService:
    """
    Main service implementing the 7-Layer GEO Prompt Generation Framework
    """
    
    def __init__(self):
        self.competitive_analyzer = CompetitiveAnalyzer()
    
    async def generate_prompts(self, website_data: Dict, industry: str, competitors: List[str] = None) -> List[Dict]:
        """
        Generate 25 highly relevant prompts using the 7-layer framework
        
        Args:
            website_data: Crawled website content
            industry: Industry category
            competitors: List of competitor names
        
        Returns:
            List of 25 scored and ranked prompts
        """
        
        logger.info(f"Starting 7-Layer GEO Prompt Generation for industry: {industry}")
        
        # Prepare user input
        user_input = {
            'industry': industry,
            'product_description': website_data.get('user_description', ''),
            'competitors': competitors or []
        }
        
        crawl_data = {
            'content': website_data.get('full_content', '') or website_data.get('description', ''),
            'title': website_data.get('name', ''),
            'metadata': {
                'description': website_data.get('description', '')
            }
        }
        
        # LAYER 1: Extract Company Intelligence
        logger.info("Layer 1: Extracting company intelligence...")
        company_intel = await CompanyIntelligence.extract(crawl_data, user_input)
        logger.info(f"Company: {company_intel.get('companyName')}, Industry: {company_intel.get('industry')}")
        
        # LAYER 2: Decompose Products
        logger.info("Layer 2: Decomposing products...")
        products = await ProductDecomposer.decompose(company_intel)
        
        # LAYER 3: Map Audiences
        logger.info("Layer 3: Mapping audiences...")
        audiences = await AudienceMapper.map_audiences(company_intel)
        
        # LAYER 4 & 5: Generate Prompts using Patterns
        logger.info("Layer 4 & 5: Generating prompts using patterns...")
        raw_prompts = await PromptPatternGenerator.generate_prompts(company_intel, products, audiences)
        
        # Add Reddit-mined prompts
        logger.info("Adding Reddit-mined prompts...")
        reddit_prompts = await self._mine_reddit_prompts(industry, company_intel)
        raw_prompts.extend(reddit_prompts)
        
        # LAYER 6: Analyze Competition (simplified)
        logger.info("Layer 6: Analyzing competitive context...")
        # Competition analysis is embedded in scoring
        
        # LAYER 7: Score and Rank
        logger.info("Layer 7: Scoring and ranking prompts...")
        scorer = RelevanceScorer(company_intel)
        scored_prompts = [scorer.score_prompt(p) for p in raw_prompts]
        
        # Sort by overall score
        scored_prompts.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Take top 25 and format for database
        top_prompts = scored_prompts[:25]
        
        # Add rank
        for i, prompt in enumerate(top_prompts, 1):
            prompt['rank'] = i
            
            # Extract individual scores for DB
            scores = prompt.get('scores', {})
            prompt['business_value'] = scores.get('businessValue', 50)
            prompt['volume'] = scores.get('searchVolume', 50)
            prompt['competition'] = 100 - scores.get('competitionDifficulty', 50)  # Invert back
            prompt['feasibility'] = scores.get('feasibility', 50)
            prompt['intent_score'] = scores.get('conversionIntent', 50)
            prompt['citation_potential'] = scores.get('citationPotential', 50)
            prompt['brand_relevance'] = scores.get('brandRelevance', 50)
        
        logger.info(f"Generated {len(top_prompts)} prompts")
        return top_prompts
    
    async def _mine_reddit_prompts(self, industry: str, company_intel: Dict) -> List[Dict]:
        """Mine Reddit for real questions people ask"""
        try:
            queries = [
                f"{industry} recommendations site:reddit.com",
                f"best {industry} site:reddit.com",
                f"{company_intel.get('companyName', '')} review site:reddit.com"
            ]
            
            prompts = []
            
            for query in queries[:2]:  # Limit API calls
                try:
                    results = self.competitive_analyzer.tavily_client.search(query, max_results=3)
                    
                    for result in results.get('results', []):
                        title = result.get('title', '')
                        if title and len(title) > 10:
                            # Convert Reddit title to question format
                            if '?' not in title:
                                title = f"What are the best options for: {title}?"
                            
                            prompts.append({
                                'prompt': title[:150],
                                'source': 'reddit_mining'
                            })
                except Exception as e:
                    logger.error(f"Reddit search failed for {query}: {e}")
            
            return prompts[:8]  # Limit Reddit prompts
            
        except Exception as e:
            logger.error(f"Reddit mining failed: {e}")
            return []


# Initialize service
prompt_generator_service = GEOPromptGeneratorService()
