from fastapi import FastAPI, APIRouter, HTTPException, Request, Header, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt

# Import new services
from crawler_service import crawler_service
from prompt_generator_service import prompt_generator_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client['citesight']

# Auth setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'citesight_secret_key_2024')
ALGORITHM = "HS256"

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=1440)  # 24 hours
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company_name: str
    website_url: str
    industry: str
    product_description: Optional[str] = None  # Optional product description
    competitors: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    first_name: str
    last_name: str
    company_name: str
    website_url: str
    industry: str
    product_description: Optional[str] = None
    competitors: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    onboarding_completed: bool = False

class Prompt(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    prompt: str
    source: str  # category_search, product_discovery, competitor_comparison, use_case, persona_based, problem_solution, feature_discovery, reddit_mining
    intent: str  # informational, navigational, commercial_investigation, transactional, local, support
    business_value: int  # 0-100 scale (25% weight)
    volume: int  # 0-100 scale (15% weight)
    competition: int  # 0-100 scale (higher = more competition, 10% weight inverted)
    feasibility: int  # 0-100 scale (10% weight)
    intent_score: int  # 0-100 scale (5% weight - conversion intent)
    citation_potential: int  # 0-100 scale (15% weight)
    brand_relevance: int  # 0-100 scale (20% weight)
    overall_score: float  # Weighted composite score (0-100)
    rank: int
    tier: str = ""  # TIER_1_CRITICAL, TIER_2_HIGH, TIER_3_MEDIUM, TIER_4_LOW
    buyer_stage: str = ""  # awareness, consideration, decision, retention
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    week_number: int  # Week of year

class CrawlResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    url: str
    title: str
    content: str
    metadata: Dict
    product_details: Dict
    crawled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Create FastAPI app
app = FastAPI()
api_router = APIRouter(prefix='/api')

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth dependency
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = payload.get('user_id')
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# ============================================
# AUTH ROUTES
# ============================================

@api_router.post("/auth/register")
async def register(user_data: UserRegister, background_tasks: BackgroundTasks):
    """
    Register new user with company details and competitors
    """
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company_name=user_data.company_name,
        website_url=user_data.website_url,
        industry=user_data.industry,
        product_description=user_data.product_description,
        competitors=user_data.competitors or []
    )
    
    await db.users.insert_one(user.model_dump())
    
    # Start onboarding process in background
    background_tasks.add_task(
        onboard_user, 
        user.id, 
        user_data.website_url, 
        user_data.industry, 
        user_data.product_description,
        user_data.competitors
    )
    
    # Create access token
    access_token = create_access_token({"user_id": user.id, "email": user.email})
    
    return {
        "message": "Registration successful. We're analyzing your website...",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "company_name": user.company_name
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"user_id": user['id'], "email": user['email']})
    
    return {
        "access_token": access_token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "company_name": user['company_name'],
            "onboarding_completed": user.get('onboarding_completed', False)
        }
    }

# ============================================
# ONBOARDING & CRAWLING
# ============================================

async def onboard_user(user_id: str, website_url: str, industry: str, product_description: Optional[str], competitors: List[str]):
    """
    Background task: Crawl website and generate initial prompts
    """
    try:
        logger.info(f"Starting onboarding for user {user_id}")
        
        # Step 1: Crawl website using Firecrawl
        logger.info(f"Crawling website: {website_url}")
        crawl_result = await crawler_service.crawl_website(website_url)
        
        if not crawl_result.get('success'):
            logger.error(f"Crawl failed: {crawl_result.get('error')}")
            return
        
        # Extract product details from crawl + user description
        product_details = crawler_service.extract_core_product_details(crawl_result)
        
        # Enhance with user-provided description if available
        if product_description:
            product_details['user_description'] = product_description
        
        # Save crawl result
        crawl_data = CrawlResult(
            user_id=user_id,
            url=website_url,
            title=crawl_result.get('title', ''),
            content=crawl_result.get('content', ''),
            metadata=crawl_result.get('metadata', {}),
            product_details=product_details
        )
        await db.crawl_results.insert_one(crawl_data.model_dump())
        
        logger.info(f"Crawl saved. Product details extracted: {product_details.get('name', 'Unknown')}")
        
        # Step 2: Generate prompts based on product understanding
        website_data = {
            'name': product_details.get('name', ''),
            'description': product_details.get('description', ''),
            'user_description': product_description or '',
            'key_topics': product_details.get('key_topics', []),
            'industry_keywords': product_details.get('industry_keywords', []),
            'full_content': crawl_result.get('content', '')[:5000]  # First 5000 chars
        }
        
        logger.info(f"Generating prompts for: {website_data['name']}")
        
        prompts = await prompt_generator_service.generate_prompts(
            website_data=website_data,
            industry=industry,
            competitors=competitors
        )
        
        logger.info(f"Generated {len(prompts)} prompts")
        
        # Step 3: Save prompts to database
        week_number = datetime.now(timezone.utc).isocalendar()[1]
        
        for prompt_data in prompts:
            prompt = Prompt(
                user_id=user_id,
                prompt=prompt_data.get('prompt', ''),
                source=prompt_data.get('source', ''),
                intent=prompt_data.get('intent', ''),
                business_value=prompt_data.get('business_value', 0),
                volume=prompt_data.get('volume', 0),
                competition=prompt_data.get('competition', 0),
                feasibility=prompt_data.get('feasibility', 0),
                intent_score=prompt_data.get('intent_score', 50),  # NEW 7th metric
                citation_potential=prompt_data.get('citation_potential', 0),
                brand_relevance=prompt_data.get('brand_relevance', 0),
                overall_score=prompt_data.get('overall_score', 0),
                rank=prompt_data.get('rank', 0),
                week_number=week_number
            )
            await db.prompts.insert_one(prompt.model_dump())
        
        # Mark onboarding complete
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"onboarding_completed": True}}
        )
        
        logger.info(f"Onboarding complete for user {user_id}")
        
    except Exception as e:
        logger.error(f"Onboarding failed for user {user_id}: {e}")

# ============================================
# PROMPT ROUTES
# ============================================

@api_router.get("/prompts")
async def get_prompts(request: Request, authorization: str = Header(None)):
    """Get all prompts for current user"""
    user = await get_current_user(authorization)
    
    # Get latest week's prompts
    prompts = await db.prompts.find(
        {"user_id": user['id']},
        {"_id": 0}
    ).sort("overall_score", -1).to_list(25)
    
    return prompts

@api_router.get("/prompts/stats")
async def get_prompt_stats(authorization: str = Header(None)):
    """Get prompt statistics for dashboard with 7-factor metrics"""
    user = await get_current_user(authorization)
    
    total_prompts = await db.prompts.count_documents({"user_id": user['id']})
    
    # Get average scores for all 7 metrics
    pipeline = [
        {"$match": {"user_id": user['id']}},
        {"$group": {
            "_id": None,
            "avg_business_value": {"$avg": "$business_value"},
            "avg_volume": {"$avg": "$volume"},
            "avg_competition": {"$avg": "$competition"},
            "avg_feasibility": {"$avg": "$feasibility"},
            "avg_intent_score": {"$avg": "$intent_score"},
            "avg_citation_potential": {"$avg": "$citation_potential"},
            "avg_brand_relevance": {"$avg": "$brand_relevance"},
            "avg_overall_score": {"$avg": "$overall_score"}
        }}
    ]
    
    stats = await db.prompts.aggregate(pipeline).to_list(1)
    avg_stats = stats[0] if stats else {}
    
    # Get source breakdown
    source_pipeline = [
        {"$match": {"user_id": user['id']}},
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ]
    source_breakdown = await db.prompts.aggregate(source_pipeline).to_list(10)
    
    # Get intent breakdown
    intent_pipeline = [
        {"$match": {"user_id": user['id']}},
        {"$group": {"_id": "$intent", "count": {"$sum": 1}}}
    ]
    intent_breakdown = await db.prompts.aggregate(intent_pipeline).to_list(10)
    
    return {
        "total_prompts": total_prompts,
        "avg_business_value": round(avg_stats.get('avg_business_value', 0), 1),
        "avg_volume": round(avg_stats.get('avg_volume', 0), 1),
        "avg_competition": round(avg_stats.get('avg_competition', 0), 1),
        "avg_feasibility": round(avg_stats.get('avg_feasibility', 0), 1),
        "avg_intent_score": round(avg_stats.get('avg_intent_score', 0), 1),
        "avg_citation_potential": round(avg_stats.get('avg_citation_potential', 0), 1),
        "avg_brand_relevance": round(avg_stats.get('avg_brand_relevance', 0), 1),
        "avg_overall_score": round(avg_stats.get('avg_overall_score', 0), 1),
        "source_breakdown": {item['_id']: item['count'] for item in source_breakdown},
        "intent_breakdown": {item['_id']: item['count'] for item in intent_breakdown}
    }

@api_router.get("/onboarding/status")
async def get_onboarding_status(authorization: str = Header(None)):
    """Check if onboarding is complete"""
    user = await get_current_user(authorization)
    
    return {
        "completed": user.get('onboarding_completed', False),
        "prompt_count": await db.prompts.count_documents({"user_id": user['id']})
    }

# ============================================
# USER ROUTES
# ============================================

@api_router.get("/user/me")
async def get_current_user_info(authorization: str = Header(None)):
    """Get current user info"""
    user = await get_current_user(authorization)
    
    return {
        "id": user['id'],
        "email": user['email'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "company_name": user['company_name'],
        "website_url": user['website_url'],
        "industry": user['industry'],
        "competitors": user.get('competitors', []),
        "onboarding_completed": user.get('onboarding_completed', False)
    }

# Root routes
@app.get("/")
async def root():
    return {"message": "CiteSight API - Prompt Monitoring Platform"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Register router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
