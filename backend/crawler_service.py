"""
Web Crawler Service using Firecrawl API
Extracts content from user websites for prompt generation
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import requests
from typing import Dict, List, Optional
import asyncio
from bs4 import BeautifulSoup
import re

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY', 'fc-c9c7061cc1e44a398cc55f24a37682cd')
FIRECRAWL_BASE_URL = 'https://api.firecrawl.dev/v0'


class CrawlerService:
    """
    Handles website crawling using Firecrawl API with fallback to custom crawler
    """
    
    def __init__(self):
        self.api_key = FIRECRAWL_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def crawl_website(self, url: str, max_pages: int = 10) -> Dict:
        """
        Crawl website using Firecrawl API
        Returns extracted content and metadata
        """
        logger.info(f"Starting crawl for URL: {url}")
        
        try:
            # Try Firecrawl API first
            result = await self._crawl_with_firecrawl(url, max_pages)
            if result and result.get('success'):
                logger.info(f"Firecrawl API successful for {url}")
                return result
        except Exception as e:
            logger.error(f"Firecrawl API failed: {e}")
        
        # Fallback to custom crawler
        logger.info("Falling back to custom crawler")
        return await self._crawl_with_custom(url, max_pages)
    
    async def _crawl_with_firecrawl(self, url: str, max_pages: int) -> Dict:
        """
        Use Firecrawl API to crawl website
        """
        endpoint = f"{FIRECRAWL_BASE_URL}/scrape"
        
        payload = {
            'url': url,
            'formats': ['markdown', 'html'],
            'onlyMainContent': True,
            'waitFor': 2000,
            'timeout': 30000
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success'):
            # Extract comprehensive data from Firecrawl
            scraped_data = data.get('data', {})
            
            return {
                'success': True,
                'url': url,
                'title': scraped_data.get('metadata', {}).get('title', '') or scraped_data.get('title', ''),
                'content': scraped_data.get('markdown', '') or scraped_data.get('content', ''),
                'metadata': {
                    'description': scraped_data.get('metadata', {}).get('description', ''),
                    'keywords': scraped_data.get('metadata', {}).get('keywords', ''),
                    'og_title': scraped_data.get('metadata', {}).get('ogTitle', ''),
                    'og_description': scraped_data.get('metadata', {}).get('ogDescription', ''),
                    'headings': self._extract_headings_from_html(scraped_data.get('html', ''))
                },
                'links': scraped_data.get('links', []),
                'method': 'firecrawl'
            }
        
        return {'success': False, 'error': 'Firecrawl API returned unsuccessful response'}
    
    def _extract_headings_from_html(self, html: str) -> List[str]:
        """Extract headings from HTML"""
        if not html:
            return []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
            return headings[:10]
        except:
            return []
    
    async def _crawl_with_custom(self, url: str, max_pages: int) -> Dict:
        """
        Fallback custom crawler using requests + BeautifulSoup
        """
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; CiteSightBot/1.0)'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            content = main_content.get_text(separator='\n', strip=True) if main_content else ''
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract headings
            headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])]
            
            # Extract links
            links = [a.get('href') for a in soup.find_all('a', href=True)][:20]
            
            return {
                'success': True,
                'url': url,
                'title': title_text,
                'content': content[:10000],  # Limit to 10k chars
                'metadata': {
                    'description': description,
                    'headings': headings[:10]
                },
                'links': links,
                'method': 'custom'
            }
        
        except Exception as e:
            logger.error(f"Custom crawler failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def extract_core_product_details(self, crawl_result: Dict) -> Dict:
        """
        Extract core product information from crawled content
        """
        if not crawl_result.get('success'):
            return {}
        
        content = crawl_result.get('content', '')
        title = crawl_result.get('title', '')
        metadata = crawl_result.get('metadata', {})
        
        # Extract key product details
        product_details = {
            'name': title,
            'description': metadata.get('description', '')[:500],
            'headings': metadata.get('headings', []),
            'key_topics': self._extract_key_topics(content),
            'industry_keywords': self._extract_industry_keywords(content)
        }
        
        return product_details
    
    def _extract_key_topics(self, content: str) -> List[str]:
        """
        Extract key topics from content (simple keyword extraction)
        """
        # Simple approach: extract most common meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'they', 'were', 'been', 'about', 'more', 'will', 'when', 'make'}
        meaningful_words = [w for w in words if w not in stopwords]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(meaningful_words)
        
        # Return top 10
        return [word for word, count in word_freq.most_common(10)]
    
    def _extract_industry_keywords(self, content: str) -> List[str]:
        """
        Extract industry-specific keywords
        """
        # Common industry terms
        industry_patterns = [
            r'\b(SaaS|software|platform|solution|service|API|tool|application)\b',
            r'\b(B2B|B2C|enterprise|startup|business)\b',
            r'\b(AI|machine learning|automation|analytics|data)\b',
            r'\b(marketing|sales|CRM|SEO|advertising)\b'
        ]
        
        keywords = []
        for pattern in industry_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            keywords.extend(set(matches))
        
        return list(set(keywords))[:15]


# Initialize service
crawler_service = CrawlerService()
