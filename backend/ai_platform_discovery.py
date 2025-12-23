"""
Layer 8: Real-World AI Platform Discovery
Query multiple AI models to discover actual prompts and track brand visibility
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json
import re

logger = logging.getLogger(__name__)

# ==========================================
# AI PLATFORM SERVICES
# ==========================================

class OpenAIPlatformService:
    """Query OpenAI/ChatGPT for prompt discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.platform_name = "chatgpt"
        self.model = "gpt-4o-mini"
    
    async def discover_prompts(self, company_context: Dict, seed_topics: List[str]) -> Dict:
        """
        Query ChatGPT to discover what prompts users ask about this industry
        """
        from litellm import acompletion
        
        brand = company_context.get('companyName', '')
        industry = company_context.get('industry', '')
        categories = company_context.get('productCategories', [])
        competitors = company_context.get('competitors', [])
        
        results = {
            'platform': self.platform_name,
            'model': self.model,
            'discovered_prompts': [],
            'brand_mentions': [],
            'competitor_mentions': {},
            'follow_up_suggestions': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Query 1: Discover common industry prompts
            industry_prompt = f"""
You are a market research analyst. List the 20 most common questions that real users ask AI assistants about {industry} products and brands like {brand}.

Include questions about:
1. Product recommendations ("Best X for Y")
2. Brand comparisons ("{brand} vs competitors")  
3. Purchase decisions ("Is X worth it")
4. Product information ("What is X")
5. How-to questions ("How to choose X")

Format: Return ONLY a numbered list of exact questions users would type. Make them realistic and conversational.
"""
            
            response = await acompletion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[{"role": "user", "content": industry_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=1500
            )
            
            prompts = self._parse_prompt_list(response.choices[0].message.content)
            results['discovered_prompts'].extend([{
                'text': p,
                'source': 'industry_discovery',
                'platform': self.platform_name
            } for p in prompts])
            
            # Query 2: Test seed prompts and check brand mentions
            for seed in seed_topics[:3]:
                seed_response = await acompletion(
                    model="openrouter/openai/gpt-4o-mini",
                    messages=[{"role": "user", "content": seed}],
                    api_base="https://openrouter.ai/api/v1",
                    api_key=os.environ.get('OPENROUTER_API_KEY'),
                    temperature=0.3,
                    max_tokens=1000
                )
                
                response_text = seed_response.choices[0].message.content
                
                # Check brand mention
                brand_mentioned = brand.lower() in response_text.lower() if brand else False
                position = self._get_brand_position(response_text, brand) if brand_mentioned else None
                
                results['brand_mentions'].append({
                    'seed_prompt': seed,
                    'mentioned': brand_mentioned,
                    'position': position,
                    'context': self._extract_mention_context(response_text, brand) if brand_mentioned else None
                })
                
                # Check competitor mentions
                for competitor in competitors:
                    if competitor.lower() in response_text.lower():
                        if competitor not in results['competitor_mentions']:
                            results['competitor_mentions'][competitor] = []
                        results['competitor_mentions'][competitor].append({
                            'seed_prompt': seed,
                            'position': self._get_brand_position(response_text, competitor),
                            'context': self._extract_mention_context(response_text, competitor)
                        })
            
            # Query 3: Get follow-up suggestions
            followup_prompt = f"""
For someone researching {industry} products like {brand}, what are 10 follow-up questions they typically ask after getting initial recommendations?

Just list the questions, one per line.
"""
            
            followup_response = await acompletion(
                model="openrouter/openai/gpt-4o-mini",
                messages=[{"role": "user", "content": followup_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=800
            )
            
            followups = self._parse_prompt_list(followup_response.choices[0].message.content)
            results['follow_up_suggestions'].extend([{
                'text': p,
                'source': 'follow_up',
                'platform': self.platform_name
            } for p in followups])
            
        except Exception as e:
            logger.error(f"OpenAI platform discovery error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _parse_prompt_list(self, response: str) -> List[str]:
        """Parse numbered list from AI response"""
        prompts = []
        lines = response.split('\n')
        
        for line in lines:
            # Match patterns like "1.", "1)", "- ", "• "
            match = re.match(r'^(?:\d+[\.\)]\s*|[-•*]\s*)[""]?(.+?)[""]?\s*$', line.strip())
            if match and len(match.group(1).strip()) > 10:
                prompts.append(match.group(1).strip())
        
        return prompts
    
    def _get_brand_position(self, response: str, brand: str) -> Optional[int]:
        """Find brand's position in a list response"""
        lines = response.split('\n')
        position = 0
        
        for line in lines:
            if re.match(r'^(?:\d+[\.\)]|\*|-)\s', line):
                position += 1
                if brand.lower() in line.lower():
                    return position
        
        return None
    
    def _extract_mention_context(self, response: str, brand: str) -> str:
        """Extract sentence containing brand mention"""
        sentences = re.split(r'[.!?]+', response)
        for sentence in sentences:
            if brand.lower() in sentence.lower():
                return sentence.strip()[:200]
        return ""


class ClaudePlatformService:
    """Query Claude/Anthropic for prompt discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.platform_name = "claude"
        self.model = "claude-sonnet-4-20250514"
    
    async def discover_prompts(self, company_context: Dict, seed_topics: List[str]) -> Dict:
        """Query Claude to discover prompts"""
        from litellm import acompletion
        
        brand = company_context.get('companyName', '')
        industry = company_context.get('industry', '')
        competitors = company_context.get('competitors', [])
        
        results = {
            'platform': self.platform_name,
            'model': self.model,
            'discovered_prompts': [],
            'brand_mentions': [],
            'competitor_mentions': {},
            'follow_up_suggestions': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Query 1: Industry prompts discovery
            industry_prompt = f"""
I'm researching what questions people commonly ask AI assistants about {industry} products, specifically related to companies like {brand}.

Please provide 20 realistic prompts/questions that consumers would actually type into an AI assistant when:
1. Researching products in this category
2. Comparing brands
3. Making purchase decisions
4. Seeking recommendations
5. Looking for reviews or opinions

Make them specific and realistic - the way actual users would phrase them.
"""
            
            response = await acompletion(
                model="openrouter/anthropic/claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": industry_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=1500
            )
            
            prompts = self._parse_prompt_list(response.choices[0].message.content)
            results['discovered_prompts'].extend([{
                'text': p,
                'source': 'industry_discovery',
                'platform': self.platform_name
            } for p in prompts])
            
            # Query 2: Test seed prompts
            for seed in seed_topics[:3]:
                seed_response = await acompletion(
                    model="openrouter/anthropic/claude-sonnet-4-20250514",
                    messages=[{"role": "user", "content": seed}],
                    api_base="https://openrouter.ai/api/v1",
                    api_key=os.environ.get('OPENROUTER_API_KEY'),
                    temperature=0.3,
                    max_tokens=1000
                )
                
                response_text = seed_response.choices[0].message.content
                
                # Check brand mention
                brand_mentioned = brand.lower() in response_text.lower() if brand else False
                
                results['brand_mentions'].append({
                    'seed_prompt': seed,
                    'mentioned': brand_mentioned,
                    'position': self._get_brand_position(response_text, brand) if brand_mentioned else None,
                    'context': self._extract_mention_context(response_text, brand) if brand_mentioned else None
                })
                
                # Check competitor mentions
                for competitor in competitors:
                    if competitor.lower() in response_text.lower():
                        if competitor not in results['competitor_mentions']:
                            results['competitor_mentions'][competitor] = []
                        results['competitor_mentions'][competitor].append({
                            'seed_prompt': seed,
                            'position': self._get_brand_position(response_text, competitor)
                        })
            
            # Query 3: Related questions
            related_prompt = f"""
Based on the topic of {industry} products and brands like {brand}, what are 10 related questions someone might ask next?

Provide them as a simple numbered list.
"""
            
            related_response = await acompletion(
                model="openrouter/anthropic/claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": related_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=800
            )
            
            followups = self._parse_prompt_list(related_response.choices[0].message.content)
            results['follow_up_suggestions'].extend([{
                'text': p,
                'source': 'related_questions',
                'platform': self.platform_name
            } for p in followups])
            
        except Exception as e:
            logger.error(f"Claude platform discovery error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _parse_prompt_list(self, response: str) -> List[str]:
        prompts = []
        lines = response.split('\n')
        for line in lines:
            match = re.match(r'^(?:\d+[\.\)]\s*|[-•*]\s*)[""]?(.+?)[""]?\s*$', line.strip())
            if match and len(match.group(1).strip()) > 10:
                prompts.append(match.group(1).strip())
        return prompts
    
    def _get_brand_position(self, response: str, brand: str) -> Optional[int]:
        lines = response.split('\n')
        position = 0
        for line in lines:
            if re.match(r'^(?:\d+[\.\)]|\*|-)\s', line):
                position += 1
                if brand.lower() in line.lower():
                    return position
        return None
    
    def _extract_mention_context(self, response: str, brand: str) -> str:
        sentences = re.split(r'[.!?]+', response)
        for sentence in sentences:
            if brand.lower() in sentence.lower():
                return sentence.strip()[:200]
        return ""


class GeminiPlatformService:
    """Query Google Gemini for prompt discovery"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.platform_name = "gemini"
        self.model = "gemini-2.0-flash"
    
    async def discover_prompts(self, company_context: Dict, seed_topics: List[str]) -> Dict:
        """Query Gemini to discover prompts"""
        from litellm import acompletion
        
        brand = company_context.get('companyName', '')
        industry = company_context.get('industry', '')
        competitors = company_context.get('competitors', [])
        
        results = {
            'platform': self.platform_name,
            'model': self.model,
            'discovered_prompts': [],
            'brand_mentions': [],
            'competitor_mentions': {},
            'follow_up_suggestions': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Query 1: Common user queries
            discovery_prompt = f"""
As a market research analyst, identify the 20 most common questions that people ask AI assistants and search engines about {industry} products, particularly regarding brands like {brand}.

Include questions about:
- Product recommendations ("Best X for Y")
- Brand comparisons ("X vs Y")
- Purchase decisions ("Is X worth it")
- Product information ("What is X")
- Problem solving ("How to X")

Format: Numbered list of exact questions users would ask.
Make them realistic and conversational.
"""
            
            response = await acompletion(
                model="openrouter/google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": discovery_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=1500
            )
            
            prompts = self._parse_prompt_list(response.choices[0].message.content)
            results['discovered_prompts'].extend([{
                'text': p,
                'source': 'industry_discovery',
                'platform': self.platform_name
            } for p in prompts])
            
            # Query 2: Test seed prompts
            for seed in seed_topics[:3]:
                seed_response = await acompletion(
                    model="openrouter/google/gemini-2.0-flash-001",
                    messages=[{"role": "user", "content": seed}],
                    api_base="https://openrouter.ai/api/v1",
                    api_key=os.environ.get('OPENROUTER_API_KEY'),
                    temperature=0.3,
                    max_tokens=1000
                )
                
                response_text = seed_response.choices[0].message.content
                
                brand_mentioned = brand.lower() in response_text.lower() if brand else False
                
                results['brand_mentions'].append({
                    'seed_prompt': seed,
                    'mentioned': brand_mentioned,
                    'position': self._get_brand_position(response_text, brand) if brand_mentioned else None
                })
                
                for competitor in competitors:
                    if competitor.lower() in response_text.lower():
                        if competitor not in results['competitor_mentions']:
                            results['competitor_mentions'][competitor] = []
                        results['competitor_mentions'][competitor].append({
                            'seed_prompt': seed,
                            'position': self._get_brand_position(response_text, competitor)
                        })
            
            # Query 3: Related topics
            related_prompt = f"""
What are 10 related questions people commonly ask about {industry} products and brands like {brand}?

Just list the questions, one per line.
"""
            
            related_response = await acompletion(
                model="openrouter/google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": related_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.7,
                max_tokens=800
            )
            
            followups = self._parse_prompt_list(related_response.choices[0].message.content)
            results['follow_up_suggestions'].extend([{
                'text': p,
                'source': 'related_topics',
                'platform': self.platform_name
            } for p in followups])
            
        except Exception as e:
            logger.error(f"Gemini platform discovery error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _parse_prompt_list(self, response: str) -> List[str]:
        prompts = []
        lines = response.split('\n')
        for line in lines:
            match = re.match(r'^(?:\d+[\.\)]\s*|[-•*]\s*)[""]?(.+?)[""]?\s*$', line.strip())
            if match and len(match.group(1).strip()) > 10:
                prompts.append(match.group(1).strip())
        return prompts
    
    def _get_brand_position(self, response: str, brand: str) -> Optional[int]:
        lines = response.split('\n')
        position = 0
        for line in lines:
            if re.match(r'^(?:\d+[\.\)]|\*|-)\s', line):
                position += 1
                if brand.lower() in line.lower():
                    return position
        return None


class PerplexityPlatformService:
    """Query Perplexity AI for prompt discovery (has real-time web access)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.platform_name = "perplexity"
        self.model = "perplexity/llama-3.1-sonar-large-128k-online"
    
    async def discover_prompts(self, company_context: Dict, seed_topics: List[str]) -> Dict:
        """Query Perplexity to discover prompts (with web search)"""
        from litellm import acompletion
        
        brand = company_context.get('companyName', '')
        industry = company_context.get('industry', '')
        competitors = company_context.get('competitors', [])
        
        results = {
            'platform': self.platform_name,
            'model': self.model,
            'discovered_prompts': [],
            'brand_mentions': [],
            'competitor_mentions': {},
            'follow_up_suggestions': [],
            'citations': [],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Query 1: Industry research with web access
            research_prompt = f"""
What are the most common questions people search for and ask about {industry} brands like {brand}?

Provide 15-20 specific questions covering:
- Product recommendations
- Brand comparisons
- Pricing inquiries
- Reviews and opinions
- How-to questions

List them as exact questions users would type.
"""
            
            response = await acompletion(
                model="openrouter/perplexity/llama-3.1-sonar-large-128k-online",
                messages=[{"role": "user", "content": research_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.5,
                max_tokens=1500
            )
            
            prompts = self._parse_prompt_list(response.choices[0].message.content)
            results['discovered_prompts'].extend([{
                'text': p,
                'source': 'web_research',
                'platform': self.platform_name
            } for p in prompts])
            
            # Query 2: Test seed prompts with citations
            for seed in seed_topics[:3]:
                seed_response = await acompletion(
                    model="openrouter/perplexity/llama-3.1-sonar-large-128k-online",
                    messages=[{"role": "user", "content": seed}],
                    api_base="https://openrouter.ai/api/v1",
                    api_key=os.environ.get('OPENROUTER_API_KEY'),
                    temperature=0.3,
                    max_tokens=1000
                )
                
                response_text = seed_response.choices[0].message.content
                
                brand_mentioned = brand.lower() in response_text.lower() if brand else False
                
                results['brand_mentions'].append({
                    'seed_prompt': seed,
                    'mentioned': brand_mentioned,
                    'position': self._get_brand_position(response_text, brand) if brand_mentioned else None
                })
                
                for competitor in competitors:
                    if competitor.lower() in response_text.lower():
                        if competitor not in results['competitor_mentions']:
                            results['competitor_mentions'][competitor] = []
                        results['competitor_mentions'][competitor].append({
                            'seed_prompt': seed,
                            'position': self._get_brand_position(response_text, competitor)
                        })
            
            # Query 3: Related searches
            related_prompt = f"""
What are the related searches and follow-up questions for {industry} products and {brand}?

List 10 specific questions people commonly ask.
"""
            
            related_response = await acompletion(
                model="openrouter/perplexity/llama-3.1-sonar-large-128k-online",
                messages=[{"role": "user", "content": related_prompt}],
                api_base="https://openrouter.ai/api/v1",
                api_key=os.environ.get('OPENROUTER_API_KEY'),
                temperature=0.5,
                max_tokens=800
            )
            
            followups = self._parse_prompt_list(related_response.choices[0].message.content)
            results['follow_up_suggestions'].extend([{
                'text': p,
                'source': 'related_searches',
                'platform': self.platform_name
            } for p in followups])
            
        except Exception as e:
            logger.error(f"Perplexity platform discovery error: {e}")
            results['error'] = str(e)
        
        return results
    
    def _parse_prompt_list(self, response: str) -> List[str]:
        prompts = []
        lines = response.split('\n')
        for line in lines:
            match = re.match(r'^(?:\d+[\.\)]\s*|[-•*]\s*)[""]?(.+?)[""]?\s*$', line.strip())
            if match and len(match.group(1).strip()) > 10:
                prompts.append(match.group(1).strip())
        return prompts
    
    def _get_brand_position(self, response: str, brand: str) -> Optional[int]:
        lines = response.split('\n')
        position = 0
        for line in lines:
            if re.match(r'^(?:\d+[\.\)]|\*|-)\s', line):
                position += 1
                if brand.lower() in line.lower():
                    return position
        return None


# ==========================================
# LAYER 8: AI PLATFORM AGGREGATOR
# ==========================================

class Layer8AIDiscoveryService:
    """
    Layer 8: Real-World AI Platform Discovery
    Queries multiple AI platforms to discover actual prompts and track brand visibility
    """
    
    def __init__(self):
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.platforms = {
            'chatgpt': OpenAIPlatformService(api_key),
            'claude': ClaudePlatformService(api_key),
            'gemini': GeminiPlatformService(api_key),
            'perplexity': PerplexityPlatformService(api_key)
        }
    
    async def discover_from_all_platforms(self, company_intel: Dict) -> Dict:
        """
        Query all AI platforms to discover prompts and track visibility
        
        Returns:
        - Prompts discovered from each platform
        - Brand visibility per platform
        - Competitor mentions per platform
        - Aggregated analytics
        """
        logger.info("Layer 8: Starting AI Platform Discovery...")
        
        brand = company_intel.get('companyName', '')
        industry = company_intel.get('industry', '')
        categories = company_intel.get('productCategories', [])
        competitors = company_intel.get('competitors', [])
        
        # Generate seed topics for testing
        seed_topics = self._generate_seed_topics(brand, industry, categories, competitors)
        
        # Query each platform
        platform_results = {}
        
        for platform_name, service in self.platforms.items():
            logger.info(f"  Querying {platform_name}...")
            try:
                result = await service.discover_prompts(company_intel, seed_topics)
                platform_results[platform_name] = result
                logger.info(f"    ✓ {platform_name}: {len(result.get('discovered_prompts', []))} prompts discovered")
            except Exception as e:
                logger.error(f"    ✗ {platform_name} error: {e}")
                platform_results[platform_name] = {
                    'platform': platform_name,
                    'error': str(e),
                    'discovered_prompts': [],
                    'brand_mentions': [],
                    'competitor_mentions': {}
                }
        
        # Aggregate results
        aggregated = self._aggregate_platform_results(platform_results, brand, competitors)
        
        return {
            'platform_results': platform_results,
            'aggregated': aggregated,
            'analytics': self._calculate_analytics(platform_results, brand, competitors)
        }
    
    def _generate_seed_topics(self, brand: str, industry: str, categories: List[str], competitors: List[str]) -> List[str]:
        """Generate seed topics to test across platforms"""
        seeds = []
        
        # Category queries
        for cat in categories[:3]:
            seeds.append(f"Best {cat} 2024")
            seeds.append(f"Top {cat} brands")
        
        # Brand queries
        if brand:
            seeds.append(f"{brand} review")
            seeds.append(f"Is {brand} good?")
        
        # Competitor comparisons
        for comp in competitors[:2]:
            if brand:
                seeds.append(f"{brand} vs {comp}")
        
        # Industry queries
        seeds.append(f"Best {industry} brands")
        seeds.append(f"{industry} recommendations")
        
        return seeds[:10]  # Limit to 10 seeds
    
    def _aggregate_platform_results(self, platform_results: Dict, brand: str, competitors: List[str]) -> Dict:
        """Aggregate prompts from all platforms with deduplication"""
        all_prompts = {}
        
        for platform_name, result in platform_results.items():
            # Add discovered prompts
            for prompt_data in result.get('discovered_prompts', []):
                text = prompt_data.get('text', '').strip()
                normalized = text.lower()
                
                if len(normalized) < 15:
                    continue
                
                if normalized not in all_prompts:
                    all_prompts[normalized] = {
                        'text': text,
                        'platforms': [platform_name],
                        'sources': [prompt_data.get('source', 'discovery')],
                        'frequency': 1
                    }
                else:
                    if platform_name not in all_prompts[normalized]['platforms']:
                        all_prompts[normalized]['platforms'].append(platform_name)
                    all_prompts[normalized]['frequency'] += 1
            
            # Add follow-up suggestions
            for prompt_data in result.get('follow_up_suggestions', []):
                text = prompt_data.get('text', '').strip()
                normalized = text.lower()
                
                if len(normalized) < 15:
                    continue
                
                if normalized not in all_prompts:
                    all_prompts[normalized] = {
                        'text': text,
                        'platforms': [platform_name],
                        'sources': ['follow_up'],
                        'frequency': 1
                    }
                else:
                    if platform_name not in all_prompts[normalized]['platforms']:
                        all_prompts[normalized]['platforms'].append(platform_name)
                    all_prompts[normalized]['frequency'] += 1
        
        # Convert to list and sort by frequency/platform coverage
        prompt_list = list(all_prompts.values())
        prompt_list.sort(key=lambda x: (len(x['platforms']), x['frequency']), reverse=True)
        
        return {
            'unique_prompts': len(prompt_list),
            'prompts': prompt_list[:100]  # Top 100
        }
    
    def _calculate_analytics(self, platform_results: Dict, brand: str, competitors: List[str]) -> Dict:
        """Calculate visibility and competitive analytics per platform"""
        analytics = {
            'brand_visibility': {},
            'competitor_visibility': {},
            'platform_coverage': {},
            'overall_visibility_score': 0
        }
        
        total_mentions = 0
        total_tests = 0
        
        for platform_name, result in platform_results.items():
            brand_mentions = result.get('brand_mentions', [])
            competitor_mentions = result.get('competitor_mentions', {})
            
            # Calculate brand visibility for this platform
            mentioned_count = sum(1 for m in brand_mentions if m.get('mentioned'))
            total_count = len(brand_mentions)
            
            visibility_score = (mentioned_count / total_count * 100) if total_count > 0 else 0
            
            # Get average position when mentioned
            positions = [m.get('position') for m in brand_mentions if m.get('position')]
            avg_position = sum(positions) / len(positions) if positions else None
            
            analytics['brand_visibility'][platform_name] = {
                'visibility_score': round(visibility_score, 1),
                'mentions': mentioned_count,
                'tests': total_count,
                'average_position': round(avg_position, 1) if avg_position else None,
                'contexts': [m.get('context') for m in brand_mentions if m.get('context')]
            }
            
            total_mentions += mentioned_count
            total_tests += total_count
            
            # Calculate competitor visibility
            for competitor, mentions in competitor_mentions.items():
                if competitor not in analytics['competitor_visibility']:
                    analytics['competitor_visibility'][competitor] = {}
                
                analytics['competitor_visibility'][competitor][platform_name] = {
                    'mentions': len(mentions),
                    'positions': [m.get('position') for m in mentions if m.get('position')]
                }
            
            # Platform coverage (how many prompts discovered)
            analytics['platform_coverage'][platform_name] = {
                'prompts_discovered': len(result.get('discovered_prompts', [])),
                'follow_ups': len(result.get('follow_up_suggestions', [])),
                'has_error': 'error' in result
            }
        
        # Overall visibility score
        analytics['overall_visibility_score'] = round(
            (total_mentions / total_tests * 100) if total_tests > 0 else 0, 1
        )
        
        return analytics


# Initialize service
layer8_discovery_service = Layer8AIDiscoveryService()
