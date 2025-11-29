"""
Content Optimization Templates for CiteSight
Base template + Model-specific templates for AI visibility optimization
"""

# Base Template - Universal optimization for all AI models
BASE_TEMPLATE = {
    "id": "base",
    "name": "Universal AI Optimization Template",
    "description": "Comprehensive optimization template applicable to all AI models",
    "guidelines": {
        "content_header": {
            "rules": [
                "Use clear, descriptive H1 tags with primary keyword",
                "Include secondary keywords in H2 and H3 tags",
                "Keep headers between 40-60 characters",
                "Use action-oriented language"
            ],
            "example": "Complete Guide to [Keyword]: Everything You Need to Know"
        },
        "subject_line": {
            "rules": [
                "Include primary keyword at the beginning",
                "Keep under 60 characters for optimal display",
                "Use numbers or lists when applicable",
                "Create urgency or curiosity"
            ],
            "example": "[Keyword] 2025: Top 10 Expert-Recommended Options"
        },
        "body_content": {
            "rules": [
                "Start with a clear problem statement",
                "Provide data-backed information with sources",
                "Include actionable steps or recommendations",
                "Use natural language and varied sentence structure",
                "Aim for 1500-2500 words for comprehensive coverage",
                "Include relevant statistics and facts"
            ],
            "structure": [
                "Introduction (100-150 words)",
                "Problem/Need identification",
                "Solutions/Options (with comparisons)",
                "Expert recommendations",
                "Actionable conclusion"
            ]
        },
        "credibility_signals": {
            "required": [
                "Author expertise/credentials",
                "Publication date",
                "Last updated date",
                "Sources and citations",
                "Expert quotes or testimonials",
                "Statistical data with sources"
            ]
        },
        "faqs": {
            "rules": [
                "Include 5-10 frequently asked questions",
                "Questions should match search intent",
                "Answers should be concise (50-100 words)",
                "Use natural question phrasing"
            ]
        },
        "schema_markup": {
            "required_types": [
                "Article schema",
                "FAQPage schema",
                "BreadcrumbList schema",
                "Organization schema"
            ]
        },
        "semantic_chunking": {
            "rules": [
                "Break content into logical sections (300-500 words)",
                "Each chunk should address one main point",
                "Use descriptive subheadings",
                "Include transition sentences between chunks"
            ]
        },
        "keyword_optimization": {
            "rules": [
                "Primary keyword density: 1-2%",
                "Include LSI keywords and synonyms",
                "Use keyword in first 100 words",
                "Natural placement in headers and body",
                "Include long-tail keyword variations"
            ]
        }
    }
}

# ChatGPT-Specific Template
CHATGPT_TEMPLATE = {
    "id": "chatgpt",
    "name": "ChatGPT Optimization Template",
    "model": "ChatGPT (GPT-4)",
    "description": "Optimized for OpenAI's GPT models",
    "specific_guidelines": {
        "tone": "Conversational yet authoritative",
        "structure": "Question-answer format works well",
        "key_factors": [
            "Clear, logical flow of information",
            "Use of analogies and examples",
            "Direct answers to common questions",
            "Structured lists and bullet points",
            "Definition of technical terms"
        ],
        "optimization_tips": [
            "Include 'What', 'Why', 'How' sections",
            "Use comparison tables",
            "Add step-by-step guides",
            "Include practical examples",
            "Define acronyms and jargon"
        ]
    }
}

# Perplexity AI Template
PERPLEXITY_TEMPLATE = {
    "id": "perplexity",
    "name": "Perplexity AI Optimization Template",
    "model": "Perplexity AI",
    "description": "Optimized for Perplexity's search-enabled AI",
    "specific_guidelines": {
        "tone": "Factual and citation-heavy",
        "structure": "Research paper style with sources",
        "key_factors": [
            "Multiple reliable sources cited",
            "Recent data and statistics",
            "Expert opinions and quotes",
            "Comparative analysis",
            "Clear source attribution"
        ],
        "optimization_tips": [
            "Include source links inline",
            "Use data from recent studies (within 2 years)",
            "Cite industry experts",
            "Provide multiple perspectives",
            "Include publication dates prominently"
        ]
    }
}

# Claude AI Template
CLAUDE_TEMPLATE = {
    "id": "claude",
    "name": "Claude AI Optimization Template",
    "model": "Claude (Anthropic)",
    "description": "Optimized for Anthropic's Claude models",
    "specific_guidelines": {
        "tone": "Thoughtful and nuanced",
        "structure": "Comprehensive with context",
        "key_factors": [
            "Thorough context and background",
            "Consideration of multiple viewpoints",
            "Ethical considerations when relevant",
            "Detailed explanations",
            "Balanced perspectives"
        ],
        "optimization_tips": [
            "Provide historical context",
            "Discuss trade-offs and considerations",
            "Include pros and cons",
            "Address potential concerns",
            "Explain reasoning behind recommendations"
        ]
    }
}

# LLaMA Template
LLAMA_TEMPLATE = {
    "id": "llama",
    "name": "LLaMA Optimization Template",
    "model": "LLaMA (Meta)",
    "description": "Optimized for Meta's LLaMA models",
    "specific_guidelines": {
        "tone": "Clear and educational",
        "structure": "Structured with clear sections",
        "key_factors": [
            "Clear topic sentences",
            "Logical progression of ideas",
            "Use of examples and case studies",
            "Practical applications",
            "Summary sections"
        ],
        "optimization_tips": [
            "Use clear section headers",
            "Include real-world examples",
            "Provide actionable takeaways",
            "Use simple, direct language",
            "Add visual descriptions where helpful"
        ]
    }
}

# DeepSeek Template
DEEPSEEK_TEMPLATE = {
    "id": "deepseek",
    "name": "DeepSeek Optimization Template",
    "model": "DeepSeek",
    "description": "Optimized for DeepSeek AI models",
    "specific_guidelines": {
        "tone": "Technical yet accessible",
        "structure": "Hierarchical with detailed subsections",
        "key_factors": [
            "Technical accuracy",
            "Detailed specifications",
            "Performance metrics",
            "Comparative data",
            "Technical documentation style"
        ],
        "optimization_tips": [
            "Include technical specifications",
            "Provide detailed methodology",
            "Use charts and data visualizations (describe them)",
            "Include benchmark comparisons",
            "Add technical glossary"
        ]
    }
}

# Template Collection
ALL_TEMPLATES = {
    "base": BASE_TEMPLATE,
    "chatgpt": CHATGPT_TEMPLATE,
    "perplexity": PERPLEXITY_TEMPLATE,
    "claude": CLAUDE_TEMPLATE,
    "llama": LLAMA_TEMPLATE,
    "deepseek": DEEPSEEK_TEMPLATE
}


def get_template(template_id: str):
    """Get a specific template by ID"""
    return ALL_TEMPLATES.get(template_id, BASE_TEMPLATE)


def get_all_templates():
    """Get all available templates"""
    return ALL_TEMPLATES


def get_model_specific_templates():
    """Get only model-specific templates (excluding base)"""
    return {
        k: v for k, v in ALL_TEMPLATES.items() 
        if k != "base"
    }
