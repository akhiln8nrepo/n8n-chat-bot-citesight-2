from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection for auth
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
auth_db_name = os.environ.get('AUTH_DB_NAME', 'citesight_auth')
client = AsyncIOMotorClient(mongo_url)
auth_db = client[auth_db_name]

# Collections
users_collection = auth_db['users']
otp_logs_collection = auth_db['otp_logs']
auth_logs_collection = auth_db['auth_logs']

# Create indexes
async def init_auth_db():
    """Initialize auth database with indexes"""
    # Users indexes
    await users_collection.create_index('email', unique=True)
    await users_collection.create_index('phone', unique=True)
    await users_collection.create_index('id', unique=True)
    
    # OTP logs indexes
    await otp_logs_collection.create_index('user_id')
    await otp_logs_collection.create_index('expires_at')
    
    # Auth logs indexes
    await auth_logs_collection.create_index('user_id')
    await auth_logs_collection.create_index('timestamp')
    
    print("Auth database indexes created successfully")
