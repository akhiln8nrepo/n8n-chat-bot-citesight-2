from passlib.context import CryptContext
import jwt
import secrets
import string
from datetime import datetime, timedelta, timezone
import os
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'citesight_secret_key_change_in_production_2024')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token generation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

# OTP generation
def generate_otp(length: int = 6) -> str:
    """Generate numeric OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

# Validation functions
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    # Basic phone validation (can be enhanced)
    pattern = r'^[+]?[0-9]{10,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

# Mock Email/SMS services
def send_email_otp(email: str, otp: str):
    """Mock email OTP - logs to console"""
    print(f"\n{'='*50}")
    print(f"📧 EMAIL OTP SENT")
    print(f"To: {email}")
    print(f"OTP Code: {otp}")
    print(f"Valid for: 10 minutes")
    print(f"{'='*50}\n")
    return True

def send_sms_otp(phone: str, otp: str):
    """Mock SMS OTP - logs to console"""
    print(f"\n{'='*50}")
    print(f"📱 SMS OTP SENT")
    print(f"To: {phone}")
    print(f"OTP Code: {otp}")
    print(f"Valid for: 10 minutes")
    print(f"{'='*50}\n")
    return True
