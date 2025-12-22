"""
Helper function for robust JSON parsing from LLM responses
"""

import json
import re
from typing import Optional, Dict, List, Any

def parse_llm_json(content: str) -> Optional[Dict]:
    """
    Robustly parse JSON from LLM responses with multiple fallback strategies
    """
    if not content or not content.strip():
        return None
    
    content = content.strip()
    
    # Strategy 1: Try direct JSON parse
    try:
        return json.loads(content)
    except:
        pass
    
    # Strategy 2: Extract from markdown JSON code blocks
    try:
        if "```json" in content:
            match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
    except:
        pass
    
    # Strategy 3: Extract from generic code blocks
    try:
        if "```" in content:
            match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
    except:
        pass
    
    # Strategy 4: Find JSON array/object in text
    try:
        # Look for JSON array
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    
    try:
        # Look for JSON object
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    
    # Strategy 5: Clean and retry
    try:
        # Remove common issues
        cleaned = content.replace('\n', ' ').replace('\r', '')
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return json.loads(cleaned)
    except:
        pass
    
    return None

def extract_prompts_from_response(response_data: Any) -> List[Dict]:
    """
    Extract prompts array from various response formats
    """
    if isinstance(response_data, list):
        return response_data
    
    if isinstance(response_data, dict):
        # Try common keys
        for key in ['prompts', 'questions', 'items', 'data', 'results']:
            if key in response_data and isinstance(response_data[key], list):
                return response_data[key]
        
        # If dict has prompt-like structure, wrap it
        if 'prompt' in response_data or 'question' in response_data:
            return [response_data]
    
    return []
