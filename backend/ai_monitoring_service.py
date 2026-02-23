"""
AI Platform Monitoring Service
Queries AI platforms (ChatGPT, Claude, Gemini, Perplexity) to check brand visibility
"""
import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from litellm import completion

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

class AIMonitoringService:
    """
    Service to run monitoring checks against AI platforms
    Checks if brand is mentioned when prompts are asked to AI chatbots
    """
    
    PLATFORM_MODELS = {
        'chatgpt': {
            'model': 'openrouter/openai/gpt-4o-mini',
            'display_name': 'ChatGPT (OpenAI)'
        },
        'claude': {
            'model': 'openrouter/anthropic/claude-3.5-haiku',
            'display_name': 'Claude (Anthropic)'
        },
        'gemini': {
            'model': 'openrouter/google/gemini-2.5-flash',
            'display_name': 'Gemini (Google)'
        },
        'perplexity': {
            'model': 'openrouter/perplexity/sonar',
            'display_name': 'Perplexity AI'
        }
    }
    
    @classmethod
    async def run_monitoring_check(
        cls,
        prompt_text: str,
        brand_name: str,
        competitors: List[str],
        platforms: List[str] = None
    ) -> Dict:
        """
        Run a monitoring check for a single prompt across specified platforms.
        
        Args:
            prompt_text: The actual prompt/question to ask AI platforms
            brand_name: Brand name to check for mentions
            competitors: List of competitor names to track
            platforms: List of platforms to check (default: all)
        
        Returns:
            Dict with results per platform including mentions, positions, sentiment
        """
        if platforms is None:
            platforms = list(cls.PLATFORM_MODELS.keys())
        
        results = {
            'prompt_text': prompt_text,
            'brand_name': brand_name,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'platforms': {}
        }
        
        # Run checks in parallel
        tasks = []
        for platform in platforms:
            if platform in cls.PLATFORM_MODELS:
                task = cls._check_platform(
                    platform=platform,
                    prompt_text=prompt_text,
                    brand_name=brand_name,
                    competitors=competitors
                )
                tasks.append((platform, task))
        
        # Execute all platform checks
        for platform, task in tasks:
            try:
                platform_result = await task
                results['platforms'][platform] = platform_result
            except Exception as e:
                logger.error(f"Error checking {platform}: {e}")
                results['platforms'][platform] = {
                    'error': str(e),
                    'brand_mentioned': False,
                    'position': None
                }
        
        # Calculate aggregate metrics
        results['summary'] = cls._calculate_summary(results['platforms'], brand_name)
        
        return results
    
    @classmethod
    async def _check_platform(
        cls,
        platform: str,
        prompt_text: str,
        brand_name: str,
        competitors: List[str]
    ) -> Dict:
        """Check a single platform for brand mentions"""
        
        model_config = cls.PLATFORM_MODELS[platform]
        model = model_config['model']
        
        try:
            # Make the actual API call to the AI platform
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                api_base="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Analyze the response
            analysis = cls._analyze_response(
                content=content,
                brand_name=brand_name,
                competitors=competitors
            )
            
            return {
                'success': True,
                'response_content': content[:2000],  # Store first 2000 chars
                'response_length': len(content),
                **analysis
            }
            
        except Exception as e:
            logger.error(f"Platform {platform} check failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'brand_mentioned': False,
                'position': None,
                'sentiment': 'neutral',
                'sentiment_score': 0
            }
    
    @classmethod
    def _analyze_response(
        cls,
        content: str,
        brand_name: str,
        competitors: List[str]
    ) -> Dict:
        """Analyze AI response for brand mentions, position, sentiment"""
        
        content_lower = content.lower()
        brand_lower = brand_name.lower()
        
        # Check brand mention
        brand_mentioned = brand_lower in content_lower
        brand_mention_count = content_lower.count(brand_lower)
        
        # Find position in any list
        position = cls._find_list_position(content, brand_name)
        
        # Analyze sentiment around brand mention
        sentiment_result = cls._analyze_sentiment(content, brand_name)
        
        # Check competitor mentions
        competitor_mentions = {}
        for competitor in competitors:
            comp_lower = competitor.lower()
            if comp_lower in content_lower:
                comp_position = cls._find_list_position(content, competitor)
                competitor_mentions[competitor] = {
                    'mentioned': True,
                    'count': content_lower.count(comp_lower),
                    'position': comp_position,
                    'positioned_above_brand': comp_position < position if (comp_position and position) else None
                }
        
        # Determine mention type
        mention_type = cls._determine_mention_type(content, brand_name)
        
        # Check if direct comparison
        is_comparison = cls._is_comparison(content, brand_name, competitors)
        
        return {
            'brand_mentioned': brand_mentioned,
            'brand_mention_count': brand_mention_count,
            'position': position,
            'mention_type': mention_type,
            'is_comparison': is_comparison,
            'sentiment': sentiment_result['sentiment'],
            'sentiment_score': sentiment_result['score'],
            'competitor_mentions': competitor_mentions,
            'competitors_mentioned_count': len(competitor_mentions),
            'brand_featured': position == 1 if position else False,
            'in_top_3': position <= 3 if position else False
        }
    
    @classmethod
    def _find_list_position(cls, content: str, entity: str) -> Optional[int]:
        """Find position of entity in any numbered or bulleted list"""
        lines = content.split('\n')
        entity_lower = entity.lower()
        
        position = 0
        for line in lines:
            # Check for numbered list (1. or 1) or bullet points
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Check if this is a list item
            is_list_item = False
            if line_stripped and (
                line_stripped[0].isdigit() or 
                line_stripped[0] in ['*', '-', '•', '→']
            ):
                is_list_item = True
                position += 1
            
            # Check if entity is in this line
            if is_list_item and entity_lower in line.lower():
                return position
        
        # If not in a list but mentioned, check first occurrence
        if entity_lower in content.lower():
            # Return approximate position based on where it appears in content
            first_index = content.lower().index(entity_lower)
            total_length = len(content)
            if first_index < total_length * 0.2:
                return 1  # Early mention = likely top recommendation
            elif first_index < total_length * 0.5:
                return 2
            else:
                return 3
        
        return None
    
    @classmethod
    def _analyze_sentiment(cls, content: str, brand_name: str) -> Dict:
        """Analyze sentiment around brand mention"""
        content_lower = content.lower()
        brand_lower = brand_name.lower()
        
        # Find context around brand mention
        brand_index = content_lower.find(brand_lower)
        if brand_index == -1:
            return {'sentiment': 'neutral', 'score': 0}
        
        # Get surrounding context (200 chars before and after)
        start = max(0, brand_index - 200)
        end = min(len(content), brand_index + len(brand_name) + 200)
        context = content_lower[start:end]
        
        # Simple lexical sentiment analysis
        positive_words = [
            'best', 'great', 'excellent', 'amazing', 'top', 'recommend', 'leading',
            'outstanding', 'superior', 'trusted', 'reliable', 'popular', 'favorite',
            'innovative', 'powerful', 'efficient', 'easy', 'intuitive', 'perfect'
        ]
        
        negative_words = [
            'worst', 'bad', 'poor', 'terrible', 'avoid', 'issue', 'problem',
            'expensive', 'overpriced', 'difficult', 'complex', 'limited', 'lacking',
            'unreliable', 'slow', 'outdated', 'confusing', 'frustrating'
        ]
        
        positive_count = sum(1 for word in positive_words if word in context)
        negative_count = sum(1 for word in negative_words if word in context)
        
        if positive_count > negative_count:
            score = min(1.0, (positive_count - negative_count) * 0.2)
            return {'sentiment': 'positive', 'score': score}
        elif negative_count > positive_count:
            score = max(-1.0, -(negative_count - positive_count) * 0.2)
            return {'sentiment': 'negative', 'score': score}
        else:
            return {'sentiment': 'neutral', 'score': 0}
    
    @classmethod
    def _determine_mention_type(cls, content: str, brand_name: str) -> str:
        """Determine how the brand was mentioned"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['recommend', 'suggest', 'best', 'top pick']):
            return 'recommendation'
        elif any(word in content_lower for word in ['vs', 'versus', 'compared', 'alternative']):
            return 'comparison'
        elif any(word in content_lower for word in ['avoid', 'warning', 'caution', 'issue']):
            return 'warning'
        else:
            return 'information'
    
    @classmethod
    def _is_comparison(cls, content: str, brand_name: str, competitors: List[str]) -> bool:
        """Check if content contains direct comparison"""
        content_lower = content.lower()
        brand_lower = brand_name.lower()
        
        # Check for comparison patterns
        comparison_patterns = ['vs', 'versus', 'compared to', 'better than', 'worse than']
        has_comparison_word = any(p in content_lower for p in comparison_patterns)
        
        # Check if brand and at least one competitor are both mentioned
        brand_mentioned = brand_lower in content_lower
        competitor_mentioned = any(comp.lower() in content_lower for comp in competitors)
        
        return has_comparison_word and brand_mentioned and competitor_mentioned
    
    @classmethod
    def _calculate_summary(cls, platform_results: Dict, brand_name: str) -> Dict:
        """Calculate aggregate summary across all platforms"""
        
        total_platforms = len(platform_results)
        platforms_with_mention = 0
        total_sentiment_score = 0
        sentiment_count = 0
        positions = []
        first_position_count = 0
        top_3_count = 0
        
        for platform, result in platform_results.items():
            if result.get('brand_mentioned'):
                platforms_with_mention += 1
                
                if result.get('sentiment_score') is not None:
                    total_sentiment_score += result['sentiment_score']
                    sentiment_count += 1
                
                if result.get('position'):
                    positions.append(result['position'])
                    if result['position'] == 1:
                        first_position_count += 1
                    if result['position'] <= 3:
                        top_3_count += 1
        
        visibility_rate = (platforms_with_mention / total_platforms * 100) if total_platforms > 0 else 0
        avg_position = sum(positions) / len(positions) if positions else None
        avg_sentiment = total_sentiment_score / sentiment_count if sentiment_count > 0 else 0
        
        return {
            'total_platforms_checked': total_platforms,
            'platforms_with_mention': platforms_with_mention,
            'visibility_rate': round(visibility_rate, 1),
            'avg_position': round(avg_position, 2) if avg_position else None,
            'first_position_count': first_position_count,
            'top_3_count': top_3_count,
            'avg_sentiment_score': round(avg_sentiment, 3),
            'overall_sentiment': 'positive' if avg_sentiment > 0.2 else 'negative' if avg_sentiment < -0.2 else 'neutral'
        }


# Singleton instance
ai_monitoring_service = AIMonitoringService()
