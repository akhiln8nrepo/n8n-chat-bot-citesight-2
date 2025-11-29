"""
Keyword Analysis Service for CiteSight
Provides keyword monitoring, LLM question discovery, and web search integration
"""
import os
import logging
from typing import List, Dict, Optional
from tavily import TavilyClient
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize clients
tavily_client = TavilyClient(api_key=os.environ.get('TAVILY_API_KEY'))
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get('OPENROUTER_API_KEY')
)

# AI Models Configuration
AI_MODELS = {
    "chatgpt": {
        "name": "ChatGPT",
        "model_id": "openai/gpt-4o",
        "description": "OpenAI's GPT-4o model"
    },
    "perplexity": {
        "name": "Perplexity AI",
        "model_id": "perplexity/llama-3.1-sonar-large-128k-online",
        "description": "Perplexity's search-enabled LLM"
    },
    "claude": {
        "name": "Claude AI",
        "model_id": "anthropic/claude-3.5-sonnet",
        "description": "Anthropic's Claude 3.5 Sonnet"
    },
    "llama": {
        "name": "LLaMA",
        "model_id": "meta-llama/llama-3.3-70b-instruct",
        "description": "Meta's LLaMA 3.3 70B"
    },
    "deepseek": {
        "name": "DeepSeek",
        "model_id": "deepseek/deepseek-chat",
        "description": "DeepSeek Chat model"
    }
}


async def discover_llm_questions(keyword: str) -> List[Dict]:
    """
    Discover previously asked LLM questions related to a keyword
    Uses OpenRouter to query multiple AI models about common questions
    """
    try:
        logger.info(f"Discovering LLM questions for keyword: {keyword}")
        
        prompt = f"""Generate 10 commonly asked questions about "{keyword}".

Return a JSON object with this exact format:
{{
  "questions": [
    {{"question": "What is the best {keyword}?", "search_volume": "high"}},
    {{"question": "How to choose {keyword}?", "search_volume": "medium"}}
  ]
}}

Focus on:
- Purchase intent: "best {keyword}", "top {keyword}", "{keyword} buying guide"
- Problem-solving: "how to fix {keyword}", "{keyword} troubleshooting"
- Comparisons: "{keyword} vs alternative", "which {keyword}"
- Information: "what is {keyword}", "how does {keyword} work"

search_volume must be: high, medium, or low"""

        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a keyword research expert. Return valid JSON with questions array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        import json
        import re
        
        logger.info(f"OpenRouter response: {content[:200]}...")
        
        # Try to extract JSON from markdown code blocks if present
        if "```json" in content:
            content = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1)
        elif "```" in content:
            content = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL).group(1)
        
        # Parse the JSON
        data = json.loads(content.strip())
        
        # Handle different response formats
        if isinstance(data, dict):
            # Try common keys
            if 'questions' in data:
                questions = data['questions']
            elif 'data' in data:
                questions = data['data']
            elif 'items' in data:
                questions = data['items']
            elif 'results' in data:
                questions = data['results']
            else:
                # If dict doesn't have expected keys, might be a single level with question keys
                questions = []
        elif isinstance(data, list):
            questions = data
        else:
            questions = []
        
        # Validate questions format
        if questions and len(questions) > 0:
            # Ensure each question has required fields
            validated_questions = []
            for q in questions:
                if isinstance(q, dict) and 'question' in q:
                    if 'search_volume' not in q:
                        q['search_volume'] = 'medium'
                    validated_questions.append(q)
            questions = validated_questions
        
        if not questions or len(questions) == 0:
            logger.warning(f"No questions returned from API for {keyword}, using fallback")
            raise Exception("No questions in API response")
        
        logger.info(f"Discovered {len(questions)} questions for keyword: {keyword}")
        return questions
        
    except Exception as e:
        logger.error(f"Error discovering LLM questions: {e}")
        # Return fallback questions
        return [
            {"question": f"What is the best {keyword}?", "search_volume": "high"},
            {"question": f"How to choose {keyword}?", "search_volume": "high"},
            {"question": f"Top 10 {keyword} recommendations", "search_volume": "medium"},
            {"question": f"{keyword} buying guide", "search_volume": "medium"},
            {"question": f"How does {keyword} work?", "search_volume": "low"},
            {"question": f"{keyword} for beginners", "search_volume": "medium"},
            {"question": f"Best budget {keyword}", "search_volume": "high"},
            {"question": f"{keyword} pros and cons", "search_volume": "low"},
            {"question": f"How to use {keyword}", "search_volume": "medium"},
            {"question": f"{keyword} reviews and ratings", "search_volume": "high"}
        ]


async def search_most_searched_queries(keyword: str) -> List[Dict]:
    """
    Search for most-searched queries related to keyword using Tavily
    """
    try:
        logger.info(f"Searching most-searched queries for: {keyword}")
        
        # Use Tavily to search for trending questions
        search_query = f"{keyword} most asked questions trending searches"
        response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            max_results=5
        )
        
        queries = []
        for result in response.get('results', []):
            queries.append({
                "query": result.get('title', ''),
                "source": result.get('url', ''),
                "snippet": result.get('content', '')[:200]
            })
        
        logger.info(f"Found {len(queries)} trending queries for: {keyword}")
        return queries
        
    except Exception as e:
        logger.error(f"Error searching queries with Tavily: {e}")
        return []


async def analyze_content_coverage(keyword: str, content_text: str, questions: List[Dict]) -> Dict:
    """
    Analyze if content answers the discovered questions
    """
    try:
        logger.info(f"Analyzing content coverage for keyword: {keyword}")
        
        questions_text = "\n".join([f"- {q['question']}" for q in questions[:10]])
        
        prompt = f"""Analyze if the following content adequately answers these common questions about "{keyword}":

QUESTIONS:
{questions_text}

CONTENT:
{content_text[:2000]}

Provide analysis in JSON format:
{{
    "coverage_score": <0-100>,
    "answered_questions": [list of question numbers that are answered],
    "missing_questions": [list of question numbers that are NOT answered],
    "recommendations": [list of 3-5 specific improvements to better answer these questions]
}}"""

        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a content analysis expert. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        
        logger.info(f"Content coverage analysis complete. Score: {analysis.get('coverage_score', 0)}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing content coverage: {e}")
        return {
            "coverage_score": 50,
            "answered_questions": [],
            "missing_questions": list(range(len(questions))),
            "recommendations": ["Add more detailed answers to common questions"]
        }


async def calculate_keyword_difficulty(question: str) -> Dict:
    """
    Calculate keyword difficulty based on top 10 competing pages
    Returns difficulty percentage (0-100) and analysis
    """
    try:
        logger.info(f"Calculating keyword difficulty for: {question}")
        
        # Search for top 10 pages
        response = tavily_client.search(
            query=question,
            search_depth="advanced",
            max_results=10
        )
        
        results = response.get('results', [])
        
        if not results or len(results) == 0:
            return {
                "difficulty": 30,
                "level": "Low",
                "competing_pages": 0,
                "analysis": "Limited competition found"
            }
        
        # Analyze competition factors
        competing_pages = len(results)
        avg_score = sum([r.get('score', 0) for r in results]) / len(results) if results else 0
        
        # Check for high-authority domains
        high_authority_domains = [
            'wikipedia.org', 'forbes.com', 'nytimes.com', 'cnn.com',
            'bbc.com', 'reuters.com', 'wsj.com', 'bloomberg.com',
            'amazon.com', 'youtube.com', 'linkedin.com', 'medium.com'
        ]
        
        from urllib.parse import urlparse
        authority_count = 0
        for result in results:
            domain = urlparse(result.get('url', '')).netloc
            if any(auth_domain in domain for auth_domain in high_authority_domains):
                authority_count += 1
        
        # Calculate difficulty (0-100)
        # Factors: number of results, average relevance score, authority sites
        base_difficulty = min(competing_pages * 5, 50)  # Max 50 from count
        score_difficulty = avg_score * 30  # Max 30 from relevance
        authority_difficulty = (authority_count / len(results)) * 20  # Max 20 from authority
        
        total_difficulty = int(base_difficulty + score_difficulty + authority_difficulty)
        total_difficulty = min(max(total_difficulty, 0), 100)  # Clamp between 0-100
        
        # Determine difficulty level
        if total_difficulty < 30:
            level = "Low"
        elif total_difficulty < 60:
            level = "Medium"
        else:
            level = "High"
        
        logger.info(f"Difficulty calculated: {total_difficulty}% ({level})")
        
        return {
            "difficulty": total_difficulty,
            "level": level,
            "competing_pages": competing_pages,
            "high_authority_sites": authority_count,
            "analysis": f"{competing_pages} competing pages, {authority_count} high-authority sites"
        }
        
    except Exception as e:
        logger.error(f"Error calculating keyword difficulty: {e}")
        return {
            "difficulty": 50,
            "level": "Medium",
            "competing_pages": 0,
            "analysis": "Unable to calculate difficulty"
        }


async def discover_competitors(keyword: str, title: str) -> List[Dict]:
    """
    Discover competitor websites publishing content on the same keyword
    """
    try:
        logger.info(f"Discovering competitors for keyword: {keyword}")
        
        search_query = f"{keyword} {title}"
        response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            max_results=10
        )
        
        competitors = []
        for result in response.get('results', []):
            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(result.get('url', '')).netloc
            
            competitors.append({
                "name": domain,
                "url": result.get('url', ''),
                "title": result.get('title', ''),
                "snippet": result.get('content', '')[:200],
                "score": result.get('score', 0)
            })
        
        logger.info(f"Discovered {len(competitors)} competitors")
        return competitors
        
    except Exception as e:
        logger.error(f"Error discovering competitors: {e}")
        return []
