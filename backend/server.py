from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AI Platforms
AI_PLATFORMS = ["Google AI Overview", "Bing Copilot", "Perplexity", "ChatGPT"]

# ==================== MODELS ====================

class Publisher(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    website: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PublisherCreate(BaseModel):
    name: str
    email: str
    website: str

class Content(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    publisher_id: str
    title: str
    url: str
    content_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContentCreate(BaseModel):
    publisher_id: str
    title: str
    url: str
    content_text: str

class AIVisibilityRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform: str
    visibility_score: float  # 0-100
    is_present: bool
    summary_snippet: Optional[str] = None
    position: Optional[int] = None
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Keyword(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    keyword: str
    platforms_found: List[str] = Field(default_factory=list)
    avg_position: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KeywordCreate(BaseModel):
    content_id: str
    keyword: str

class GEORecommendation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    recommendation_type: str
    recommendation_text: str
    priority: str  # high, medium, low
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompetitorAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    publisher_id: str
    competitor_name: str
    competitor_url: str
    visibility_score: float
    platforms_present: List[str]
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== HELPER FUNCTIONS ====================

def generate_mock_visibility_data(content_id: str) -> List[Dict]:
    """Generate mock visibility data for AI platforms"""
    visibility_records = []
    for platform in AI_PLATFORMS:
        is_present = random.choice([True, True, False])  # 66% chance of being present
        visibility_score = random.uniform(45, 95) if is_present else random.uniform(5, 30)
        
        record = {
            "id": str(uuid.uuid4()),
            "content_id": content_id,
            "platform": platform,
            "visibility_score": round(visibility_score, 2),
            "is_present": is_present,
            "summary_snippet": f"Your content appears in {platform} summary..." if is_present else None,
            "position": random.randint(1, 10) if is_present else None,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        visibility_records.append(record)
    
    return visibility_records

async def generate_geo_recommendations(content_text: str, content_id: str) -> List[Dict]:
    """Generate GEO recommendations using LLM"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"citesight_rec_{content_id}",
            system_message="You are an AI-powered GEO (Generative Engine Optimization) expert. Provide 5 actionable recommendations to improve content visibility in AI-generated summaries. Focus on semantic structure, schema markup, FAQ injection, and content optimization."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(
            text=f"Analyze this content and provide 5 specific GEO recommendations to improve its visibility in AI summaries (Google AI Overview, Bing Copilot, Perplexity, ChatGPT). Content: {content_text[:1000]}..."
        )
        
        response = await chat.send_message(user_message)
        
        # Parse response and create recommendations
        recommendations = []
        priorities = ["high", "high", "medium", "medium", "low"]
        types = ["Semantic Chunking", "Schema Markup", "FAQ Injection", "Content Structure", "Keyword Optimization"]
        
        lines = response.strip().split('\n')
        for i, line in enumerate(lines[:5]):
            if line.strip():
                recommendations.append({
                    "id": str(uuid.uuid4()),
                    "content_id": content_id,
                    "recommendation_type": types[i] if i < len(types) else "General",
                    "recommendation_text": line.strip(),
                    "priority": priorities[i] if i < len(priorities) else "medium",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
        
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        # Fallback mock recommendations
        return [
            {
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "recommendation_type": "Semantic Chunking",
                "recommendation_text": "Break content into logical sections with clear H2/H3 headings to improve AI parsing.",
                "priority": "high",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "recommendation_type": "Schema Markup",
                "recommendation_text": "Add Article schema markup with author, datePublished, and description fields.",
                "priority": "high",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "content_id": content_id,
                "recommendation_type": "FAQ Injection",
                "recommendation_text": "Add FAQ section with 3-5 common questions and concise answers.",
                "priority": "medium",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

# ==================== AUTH MIDDLEWARE ====================

async def get_current_user_from_token(authorization: str = None):
    """Extract and verify user from JWT token"""
    if not authorization or not authorization.startswith('Bearer '):
        return None
    
    token = authorization.split(' ')[1]
    try:
        from auth_utils import verify_token
        payload = verify_token(token)
        if payload:
            return payload.get('user_id')
    except:
        pass
    return None

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "AI Content Monitor API"}

# Publisher routes
@api_router.post("/publishers", response_model=Publisher)
async def create_publisher(input: PublisherCreate, request: Request):
    # Get user_id from auth token
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    # Check if publisher already exists for this user
    if user_id:
        existing = await db.publishers.find_one({"user_id": str(user_id)})
        if existing:
            existing['created_at'] = datetime.fromisoformat(existing['created_at']) if isinstance(existing['created_at'], str) else existing['created_at']
            return Publisher(**existing)
    
    publisher_data = input.model_dump()
    publisher_data['user_id'] = str(user_id) if user_id else None
    publisher = Publisher(**publisher_data)
    doc = publisher.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.publishers.insert_one(doc)
    return publisher

@api_router.get("/publishers", response_model=List[Publisher])
async def get_publishers(request: Request):
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    # Only return publishers for the logged-in user
    query = {"user_id": str(user_id)} if user_id else {}
    publishers = await db.publishers.find(query, {"_id": 0}).to_list(1000)
    for p in publishers:
        if isinstance(p['created_at'], str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
    return publishers

@api_router.get("/publishers/me", response_model=Publisher)
async def get_my_publisher(request: Request):
    """Get or create publisher for logged-in user"""
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find existing publisher
    existing = await db.publishers.find_one({"user_id": str(user_id)})
    if existing:
        if isinstance(existing['created_at'], str):
            existing['created_at'] = datetime.fromisoformat(existing['created_at'])
        return Publisher(**existing)
    
    # Create default publisher for user (using user_id as identifier)
    # In production, you would fetch user details from auth system
    publisher = Publisher(
        name=f"User {user_id}",
        email=f"user{user_id}@citesight.com",
        website="https://citesight.com",
        user_id=str(user_id)
    )
    doc = publisher.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.publishers.insert_one(doc)
    return publisher

# Content routes
@api_router.post("/content", response_model=Content)
async def create_content(input: ContentCreate, request: Request):
    # Verify user owns the publisher
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    if user_id:
        publisher = await db.publishers.find_one({"id": input.publisher_id, "user_id": str(user_id)})
        if not publisher:
            raise HTTPException(status_code=403, detail="Not authorized to add content for this publisher")
    
    content = Content(**input.model_dump())
    doc = content.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.content.insert_one(doc)
    
    # Generate initial visibility data
    visibility_data = generate_mock_visibility_data(content.id)
    if visibility_data:
        await db.visibility.insert_many(visibility_data)
    
    # Generate GEO recommendations
    recommendations = await generate_geo_recommendations(input.content_text, content.id)
    if recommendations:
        await db.recommendations.insert_many(recommendations)
    
    return content

@api_router.get("/content", response_model=List[Content])
async def get_content(request: Request):
    # Get user's publisher IDs
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    if not user_id:
        return []
    
    # Find user's publishers
    publishers = await db.publishers.find({"user_id": str(user_id)}, {"_id": 0}).to_list(100)
    publisher_ids = [p['id'] for p in publishers]
    
    # Get content for these publishers
    content_list = await db.content.find({"publisher_id": {"$in": publisher_ids}}, {"_id": 0}).to_list(1000)
    for c in content_list:
        if isinstance(c['created_at'], str):
            c['created_at'] = datetime.fromisoformat(c['created_at'])
    return content_list

@api_router.get("/content/{content_id}", response_model=Content)
async def get_content_by_id(content_id: str):
    content = await db.content.find_one({"id": content_id}, {"_id": 0})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if isinstance(content['created_at'], str):
        content['created_at'] = datetime.fromisoformat(content['created_at'])
    return content

# Visibility routes
@api_router.get("/visibility/{content_id}")
async def get_visibility(content_id: str):
    visibility_records = await db.visibility.find({"content_id": content_id}, {"_id": 0}).to_list(100)
    for v in visibility_records:
        if isinstance(v.get('checked_at'), str):
            v['checked_at'] = datetime.fromisoformat(v['checked_at'])
    return visibility_records

# Keyword routes
@api_router.post("/keywords", response_model=Keyword)
async def create_keyword(input: KeywordCreate):
    # Check if content exists
    content = await db.content.find_one({"id": input.content_id})
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Simulate keyword tracking
    platforms_found = random.sample(AI_PLATFORMS, random.randint(1, 4))
    keyword = Keyword(
        **input.model_dump(),
        platforms_found=platforms_found,
        avg_position=round(random.uniform(2, 8), 1) if platforms_found else None
    )
    
    doc = keyword.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.keywords.insert_one(doc)
    return keyword

@api_router.get("/keywords/{content_id}", response_model=List[Keyword])
async def get_keywords(content_id: str):
    keywords = await db.keywords.find({"content_id": content_id}, {"_id": 0}).to_list(100)
    for k in keywords:
        if isinstance(k['created_at'], str):
            k['created_at'] = datetime.fromisoformat(k['created_at'])
    return keywords

# Recommendations routes
@api_router.get("/recommendations/{content_id}", response_model=List[GEORecommendation])
async def get_recommendations(content_id: str):
    recommendations = await db.recommendations.find({"content_id": content_id}, {"_id": 0}).to_list(100)
    for r in recommendations:
        if isinstance(r['created_at'], str):
            r['created_at'] = datetime.fromisoformat(r['created_at'])
    return recommendations

# Dashboard stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request):
    # Get user's publisher
    auth_header = request.headers.get('authorization')
    user_id = await get_current_user_from_token(auth_header)
    
    if not user_id:
        return {
            "total_content": 0,
            "avg_visibility_score": 0,
            "platforms_present": {},
            "total_keywords": 0,
            "visibility_trend": []
        }
    
    # Find user's publisher
    publisher = await db.publishers.find_one({"user_id": str(user_id)})
    if not publisher:
        return {
            "total_content": 0,
            "avg_visibility_score": 0,
            "platforms_present": {},
            "total_keywords": 0,
            "visibility_trend": []
        }
    
    # Get all content for this publisher
    query = {"publisher_id": publisher['id']}
    content_list = await db.content.find(query, {"_id": 0}).to_list(1000)
    
    if not content_list:
        return {
            "total_content": 0,
            "avg_visibility_score": 0,
            "platforms_present": {},
            "total_keywords": 0,
            "visibility_trend": []
        }
    
    content_ids = [c['id'] for c in content_list]
    
    # Get visibility data
    visibility_records = await db.visibility.find(
        {"content_id": {"$in": content_ids}},
        {"_id": 0}
    ).to_list(10000)
    
    # Calculate stats
    total_score = sum(v['visibility_score'] for v in visibility_records)
    avg_score = total_score / len(visibility_records) if visibility_records else 0
    
    platforms_count = {}
    for v in visibility_records:
        if v['is_present']:
            platforms_count[v['platform']] = platforms_count.get(v['platform'], 0) + 1
    
    # Get keyword count
    keywords_count = await db.keywords.count_documents({"content_id": {"$in": content_ids}})
    
    # Generate visibility trend (last 7 days)
    trend = []
    for i in range(6, -1, -1):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        score = round(random.uniform(60, 85), 2)  # Mock trend data
        trend.append({
            "date": date.strftime("%Y-%m-%d"),
            "score": score
        })
    
    return {
        "total_content": len(content_list),
        "avg_visibility_score": round(avg_score, 2),
        "platforms_present": platforms_count,
        "total_keywords": keywords_count,
        "visibility_trend": trend
    }

# Competitor routes
@api_router.get("/competitors")
async def get_competitors(publisher_id: str):
    # Generate mock competitor data
    competitors = [
        {
            "id": str(uuid.uuid4()),
            "publisher_id": publisher_id,
            "competitor_name": "TechCrunch",
            "competitor_url": "https://techcrunch.com",
            "visibility_score": 87.5,
            "platforms_present": ["Google AI Overview", "Bing Copilot", "Perplexity", "ChatGPT"],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "publisher_id": publisher_id,
            "competitor_name": "The Verge",
            "competitor_url": "https://theverge.com",
            "visibility_score": 82.3,
            "platforms_present": ["Google AI Overview", "Bing Copilot", "ChatGPT"],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "publisher_id": publisher_id,
            "competitor_name": "Wired",
            "competitor_url": "https://wired.com",
            "visibility_score": 79.8,
            "platforms_present": ["Google AI Overview", "Perplexity", "ChatGPT"],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    return competitors

# Include the routers in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()