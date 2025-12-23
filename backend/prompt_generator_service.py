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
# LAYER 8: REAL-WORLD AI PLATFORM DISCOVERY
# ==========================================

class AIplatformDiscovery:
    """
    Layer 8: Query multiple AI platforms (ChatGPT, Claude, Gemini, Perplexity)
    to discover real-world questions users are asking.
    
    This provides:
    1. Real prompts users actually ask AI chatbots
    2. Platform-specific data for analytics (visibility, mentions, etc.)
    3. Foundation for tracking brand presence across AI platforms
    """
    
    # OpenRouter model mappings for each AI platform
    PLATFORM_MODELS = {
        'chatgpt': {
            'model': 'openrouter/openai/gpt-4o-mini',
            'display_name': 'ChatGPT (OpenAI)',
            'has_web_search': False
        },
        'claude': {
            'model': 'openrouter/anthropic/claude-3.5-haiku-20241022',
            'display_name': 'Claude (Anthropic)',
            'has_web_search': False
        },
        'gemini': {
            'model': 'openrouter/google/gemini-2.5-flash',
            'display_name': 'Gemini (Google)',
            'has_web_search': False
        },
        'perplexity': {
            'model': 'openrouter/perplexity/sonar',
            'display_name': 'Perplexity AI',
            'has_web_search': True  # Perplexity has built-in web search
        }
    }
    
    @classmethod
    async def discover_prompts_from_all_platforms(
        cls, 
        company_intel: Dict, 
        products: Dict,
        audiences: List[Dict]
    ) -> Dict:
        """
        Query all AI platforms to discover real-world prompts.
        
        Returns:
            {
                'discovered_prompts': List[Dict],  # New prompts discovered
                'platform_responses': Dict,  # Raw responses per platform
                'platform_analytics': Dict   # Analytics data per platform
            }
        """
        brand = company_intel.get('companyName', 'Company')
        industry = company_intel.get('industry', 'Business')
        categories = products.get('mainCategories', []) or company_intel.get('productCategories', [])
        competitors = company_intel.get('competitors', [])
        
        all_discovered_prompts = []
        platform_responses = {}
        platform_analytics = {}
        
        # Query each platform concurrently
        tasks = []
        for platform_key, platform_config in cls.PLATFORM_MODELS.items():
            task = cls._query_platform(
                platform_key=platform_key,
                platform_config=platform_config,
                brand=brand,
                industry=industry,
                categories=categories,
                competitors=competitors
            )
            tasks.append(task)
        
        # Execute all platform queries
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for platform_key, result in zip(cls.PLATFORM_MODELS.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Platform {platform_key} query failed: {result}")
                platform_responses[platform_key] = {'error': str(result)}
                platform_analytics[platform_key] = cls._create_error_analytics(platform_key)
                continue
            
            platform_responses[platform_key] = result.get('raw_response', {})
            platform_analytics[platform_key] = result.get('analytics', {})
            
            # Add discovered prompts with platform attribution
            for prompt_data in result.get('prompts', []):
                prompt_data['ai_discovery_platform'] = platform_key
                prompt_data['ai_platform_display'] = cls.PLATFORM_MODELS[platform_key]['display_name']
                all_discovered_prompts.append(prompt_data)
        
        # Deduplicate discovered prompts
        seen = set()
        unique_prompts = []
        for p in all_discovered_prompts:
            prompt_lower = p.get('prompt', '').lower().strip()
            if prompt_lower and prompt_lower not in seen:
                seen.add(prompt_lower)
                unique_prompts.append(p)
        
        logger.info(f"Layer 8: Discovered {len(unique_prompts)} unique prompts from {len(cls.PLATFORM_MODELS)} AI platforms")
        
        return {
            'discovered_prompts': unique_prompts,
            'platform_responses': platform_responses,
            'platform_analytics': platform_analytics
        }
    
    @classmethod
    async def _query_platform(
        cls,
        platform_key: str,
        platform_config: Dict,
        brand: str,
        industry: str,
        categories: List[str],
        competitors: List[str]
    ) -> Dict:
        """
        Query a single AI platform to discover prompts users ask.
        """
        model = platform_config['model']
        display_name = platform_config['display_name']
        
        # Build discovery prompt
        categories_str = ', '.join(categories[:5]) if categories else industry
        competitors_str = ', '.join(competitors[:3]) if competitors else 'major brands'
        
        discovery_prompt = f"""You are a market research analyst. I need to understand what questions real users are asking AI chatbots about {industry} products and services.

CONTEXT:
- Industry: {industry}
- Product Categories: {categories_str}
- Key Competitors: {competitors_str}
- Brand to analyze: {brand}

TASK:
Generate 15-20 realistic questions that users would actually type into an AI chatbot when:
1. Researching {industry} products
2. Comparing options and brands
3. Looking for recommendations
4. Trying to make a purchase decision
5. Seeking help with {industry}-related problems

For each question, indicate:
- The user's likely intent (informational, comparison, purchase, support)
- Whether it's brand-specific, category-generic, or competitor-focused
- The likely buyer stage (awareness, consideration, decision)

Return a JSON array:
[
    {{
        "prompt": "the actual question users would ask",
        "intent": "informational|comparison|transactional|support",
        "focus": "brand|category|competitor",
        "buyer_stage": "awareness|consideration|decision",
        "search_volume_estimate": "high|medium|low"
    }}
]

Generate diverse, realistic questions that cover different user needs and stages.
Return ONLY valid JSON array, no markdown or explanation."""

        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": discovery_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            parsed = parse_llm_json(content)
            
            prompts = []
            if isinstance(parsed, list):
                prompts = parsed
            elif isinstance(parsed, dict) and 'prompts' in parsed:
                prompts = parsed['prompts']
            
            # Standardize prompt format
            standardized_prompts = []
            for p in prompts:
                if isinstance(p, dict) and p.get('prompt'):
                    standardized_prompts.append({
                        'prompt': p.get('prompt', ''),
                        'source': 'ai_platform_discovery',
                        'intent': cls._map_intent(p.get('intent', 'informational')),
                        'focus': p.get('focus', 'category'),
                        'buyer_stage': p.get('buyer_stage', 'awareness'),
                        'volume_estimate': p.get('search_volume_estimate', 'medium')
                    })
                elif isinstance(p, str):
                    standardized_prompts.append({
                        'prompt': p,
                        'source': 'ai_platform_discovery',
                        'intent': 'informational',
                        'focus': 'category',
                        'buyer_stage': 'awareness',
                        'volume_estimate': 'medium'
                    })
            
            # Build analytics data
            analytics = cls._build_platform_analytics(
                platform_key=platform_key,
                brand=brand,
                competitors=competitors,
                prompts=standardized_prompts,
                raw_content=content
            )
            
            logger.info(f"Platform {display_name}: Discovered {len(standardized_prompts)} prompts")
            
            return {
                'prompts': standardized_prompts,
                'raw_response': {'content_length': len(content)},
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error querying {display_name}: {e}")
            raise
    
    @classmethod
    def _map_intent(cls, intent: str) -> str:
        """Map various intent labels to standard classification"""
        intent = intent.lower() if intent else 'informational'
        
        mapping = {
            'informational': 'informational',
            'information': 'informational',
            'info': 'informational',
            'comparison': 'commercial_investigation',
            'compare': 'commercial_investigation',
            'research': 'commercial_investigation',
            'commercial': 'commercial_investigation',
            'transactional': 'transactional',
            'purchase': 'transactional',
            'buy': 'transactional',
            'support': 'support',
            'help': 'support',
            'navigational': 'navigational'
        }
        
        return mapping.get(intent, 'informational')
    
    @classmethod
    def _build_platform_analytics(
        cls,
        platform_key: str,
        brand: str,
        competitors: List[str],
        prompts: List[Dict],
        raw_content: str
    ) -> Dict:
        """
        Build analytics data for a platform's response.
        This data will be used for visibility scores and competitor tracking.
        """
        brand_lower = brand.lower() if brand else ''
        content_lower = raw_content.lower()
        
        # Check brand mentions
        brand_mentioned = brand_lower in content_lower if brand_lower else False
        brand_mention_count = content_lower.count(brand_lower) if brand_lower else 0
        
        # Check competitor mentions
        competitor_mentions = {}
        for comp in competitors:
            comp_lower = comp.lower()
            mentioned = comp_lower in content_lower
            count = content_lower.count(comp_lower)
            competitor_mentions[comp] = {
                'mentioned': mentioned,
                'count': count
            }
        
        # Analyze prompt types
        intent_distribution = {}
        focus_distribution = {}
        stage_distribution = {}
        
        for p in prompts:
            intent = p.get('intent', 'informational')
            focus = p.get('focus', 'category')
            stage = p.get('buyer_stage', 'awareness')
            
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            focus_distribution[focus] = focus_distribution.get(focus, 0) + 1
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
        
        # Calculate visibility indicators
        total_prompts = len(prompts)
        brand_focused_prompts = sum(1 for p in prompts if p.get('focus') == 'brand')
        
        visibility_score = 0
        if total_prompts > 0:
            # Base score on brand focus ratio
            visibility_score = (brand_focused_prompts / total_prompts) * 50
            # Add bonus for brand mentions
            if brand_mentioned:
                visibility_score += 25
            # Add bonus for mention frequency
            visibility_score += min(25, brand_mention_count * 5)
        
        return {
            'platform': platform_key,
            'platform_display': cls.PLATFORM_MODELS[platform_key]['display_name'],
            'total_prompts_discovered': total_prompts,
            'brand_visibility': {
                'mentioned': brand_mentioned,
                'mention_count': brand_mention_count,
                'visibility_score': round(visibility_score, 1)
            },
            'competitor_visibility': competitor_mentions,
            'intent_distribution': intent_distribution,
            'focus_distribution': focus_distribution,
            'stage_distribution': stage_distribution,
            'has_web_search': cls.PLATFORM_MODELS[platform_key]['has_web_search']
        }
    
    @classmethod
    def _create_error_analytics(cls, platform_key: str) -> Dict:
        """Create error analytics when platform query fails"""
        return {
            'platform': platform_key,
            'platform_display': cls.PLATFORM_MODELS[platform_key]['display_name'],
            'total_prompts_discovered': 0,
            'brand_visibility': {
                'mentioned': False,
                'mention_count': 0,
                'visibility_score': 0
            },
            'competitor_visibility': {},
            'intent_distribution': {},
            'focus_distribution': {},
            'stage_distribution': {},
            'error': True,
            'has_web_search': cls.PLATFORM_MODELS[platform_key]['has_web_search']
        }


# ==========================================
# MAIN PROMPT GENERATOR SERVICE
# ==========================================

class GEOPromptGeneratorService:
    """
    Main service implementing the 8-Layer GEO Prompt Generation Framework
    
    Layers 1-7: Pattern-based prompt generation with scoring
    Layer 8: Real-world AI platform discovery (ChatGPT, Claude, Gemini, Perplexity)
    """
    
    def __init__(self):
        self.competitive_analyzer = CompetitiveAnalyzer()
    
    async def generate_prompts(
        self, 
        website_data: Dict, 
        industry: str, 
        competitors: List[str] = None,
        include_layer8: bool = True
    ) -> Dict:
        """
        Generate 100 highly relevant prompts using the 8-layer framework
        
        Args:
            website_data: Crawled website content
            industry: Industry category
            competitors: List of competitor names
            include_layer8: Whether to run AI platform discovery (default True)
        
        Returns:
            {
                'prompts': List of 100 scored and ranked prompts,
                'platform_analytics': Dict of analytics per AI platform (if Layer 8 enabled),
                'generation_metadata': Dict of generation statistics
            }
        """
        
        logger.info(f"Starting 8-Layer GEO Prompt Generation for industry: {industry}")
        
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
        
        # Initialize analytics
        platform_analytics = {}
        layer8_prompts_count = 0
        
        # LAYER 8: AI Platform Discovery (NEW)
        if include_layer8:
            logger.info("Layer 8: Discovering prompts from AI platforms (ChatGPT, Claude, Gemini, Perplexity)...")
            try:
                layer8_result = await AIplatformDiscovery.discover_prompts_from_all_platforms(
                    company_intel=company_intel,
                    products=products,
                    audiences=audiences
                )
                
                # Add discovered prompts to raw_prompts
                discovered_prompts = layer8_result.get('discovered_prompts', [])
                raw_prompts.extend(discovered_prompts)
                layer8_prompts_count = len(discovered_prompts)
                
                # Store platform analytics
                platform_analytics = layer8_result.get('platform_analytics', {})
                
                logger.info(f"Layer 8: Added {layer8_prompts_count} prompts from AI platforms")
                
            except Exception as e:
                logger.error(f"Layer 8 failed: {e}")
                # Continue without Layer 8 data
        
        # LAYER 7: Score and Rank ALL prompts (including Layer 8)
        logger.info("Layer 7: Scoring and ranking all prompts...")
        scorer = RelevanceScorer(company_intel)
        scored_prompts = [scorer.score_prompt(p) for p in raw_prompts]
        
        # Sort by overall score
        scored_prompts.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Take top 100 prompts and format for database
        top_prompts = scored_prompts[:100]
        
        # Track source distribution
        source_distribution = {}
        ai_platform_distribution = {}
        
        # Add rank and extract scores
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
            
            # Track source distribution
            source = prompt.get('source', 'unknown')
            source_distribution[source] = source_distribution.get(source, 0) + 1
            
            # Track AI platform distribution (for Layer 8 prompts)
            if source == 'ai_platform_discovery':
                platform = prompt.get('ai_discovery_platform', 'unknown')
                ai_platform_distribution[platform] = ai_platform_distribution.get(platform, 0) + 1
        
        # Build generation metadata
        generation_metadata = {
            'total_raw_prompts': len(raw_prompts),
            'total_scored_prompts': len(scored_prompts),
            'final_prompts': len(top_prompts),
            'layer8_enabled': include_layer8,
            'layer8_prompts_discovered': layer8_prompts_count,
            'layer8_prompts_in_top100': sum(ai_platform_distribution.values()),
            'source_distribution': source_distribution,
            'ai_platform_distribution': ai_platform_distribution,
            'company_name': company_intel.get('companyName', 'Unknown'),
            'industry': industry
        }
        
        logger.info(f"Generated {len(top_prompts)} prompts (Top 100 by score)")
        logger.info(f"Source distribution: {source_distribution}")
        if ai_platform_distribution:
            logger.info(f"AI Platform distribution in top 100: {ai_platform_distribution}")
        
        return {
            'prompts': top_prompts,
            'platform_analytics': platform_analytics,
            'generation_metadata': generation_metadata
        }
    
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
