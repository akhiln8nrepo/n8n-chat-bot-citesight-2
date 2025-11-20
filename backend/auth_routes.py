from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, timedelta, timezone
from slowapi import Limiter
from slowapi.util import get_remote_address

from auth_db import get_db, User, OTPLog, AuthLog, init_db
from auth_utils import (
    hash_password, verify_password, create_access_token, verify_token,
    generate_otp, validate_email, validate_phone, validate_password_strength,
    send_email_otp, send_sms_otp
)

# Initialize database
init_db()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Router
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security
security = HTTPBearer()

# ==================== PYDANTIC MODELS ====================

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    gst_tax_id: Optional[str] = None
    notes: Optional[str] = None

    @validator('phone')
    def validate_phone_format(cls, v):
        if not validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v

    @validator('password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

class LoginRequest(BaseModel):
    identifier: str  # Can be email or phone
    password: str

class SendOTPRequest(BaseModel):
    identifier: str  # Email or phone
    otp_type: str  # 'email' or 'sms'

class VerifyOTPRequest(BaseModel):
    identifier: str
    otp_code: str
    otp_type: str

class ForgotPasswordRequest(BaseModel):
    identifier: str  # Email or phone

class ResetPasswordRequest(BaseModel):
    identifier: str
    otp_code: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v

# ==================== HELPER FUNCTIONS ====================

def log_auth_action(db: Session, user_id: Optional[int], action: str, 
                    ip_address: str, user_agent: str, status: str, 
                    error_message: Optional[str] = None):
    \"\"\"Log authentication actions\"\"\"
    log = AuthLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        error_message=error_message
    )
    db.add(log)
    db.commit()

def get_user_by_identifier(db: Session, identifier: str):
    \"\"\"Get user by email or phone\"\"\"
    if validate_email(identifier):
        return db.query(User).filter(User.email == identifier).first()
    elif validate_phone(identifier):
        clean_phone = identifier.replace(' ', '').replace('-', '')
        return db.query(User).filter(User.phone == clean_phone).first()
    return None

def create_and_send_otp(db: Session, user: User, otp_type: str):
    \"\"\"Create OTP and send via email or SMS\"\"\"
    # Generate OTP
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    # Save OTP to database
    otp_log = OTPLog(
        user_id=user.id,
        otp_code=otp_code,
        otp_type=otp_type,
        expires_at=expires_at,
        verified=False,
        attempts=0
    )
    db.add(otp_log)
    db.commit()
    
    # Send OTP
    if otp_type == 'email':
        send_email_otp(user.email, otp_code)
    elif otp_type == 'sms':
        send_sms_otp(user.phone, otp_code)
    
    return otp_log

# ==================== ROUTES ====================

@auth_router.post(\"/register\")
@limiter.limit(\"5/minute\")
async def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    \"\"\"Register new user\"\"\"
    try:
        # Check if email exists
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            log_auth_action(db, None, 'register', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Email already registered')
            raise HTTPException(status_code=400, detail=\"Email already registered\")
        
        # Check if phone exists
        clean_phone = data.phone.replace(' ', '').replace('-', '')
        existing_phone = db.query(User).filter(User.phone == clean_phone).first()
        if existing_phone:
            log_auth_action(db, None, 'register', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Phone already registered')
            raise HTTPException(status_code=400, detail=\"Phone number already registered\")
        
        # Create user
        hashed_password = hash_password(data.password)
        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=clean_phone,
            password_hash=hashed_password,
            business_name=data.business_name,
            business_type=data.business_type,
            gst_tax_id=data.gst_tax_id,
            notes=data.notes
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log success
        log_auth_action(db, new_user.id, 'register', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        # Send verification OTPs
        email_otp = create_and_send_otp(db, new_user, 'email')
        sms_otp = create_and_send_otp(db, new_user, 'sms')
        
        return {
            \"message\": \"Registration successful. Please verify your email or phone.\",
            \"user_id\": new_user.id,
            \"email\": new_user.email,
            \"phone\": new_user.phone,
            \"email_verified\": False,
            \"phone_verified\": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_auth_action(db, None, 'register', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'failed', str(e))
        raise HTTPException(status_code=500, detail=\"Registration failed\")

@auth_router.post(\"/login\")
@limiter.limit(\"10/minute\")
async def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    \"\"\"User login with email or phone\"\"\"
    try:
        # Find user
        user = get_user_by_identifier(db, data.identifier)
        
        if not user:
            log_auth_action(db, None, 'login', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'User not found')
            raise HTTPException(status_code=401, detail=\"Invalid credentials\")
        
        # Verify password
        if not verify_password(data.password, user.password_hash):
            log_auth_action(db, user.id, 'login', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Invalid password')
            raise HTTPException(status_code=401, detail=\"Invalid credentials\")
        
        # Check verification status
        if not user.email_verified and not user.phone_verified:
            log_auth_action(db, user.id, 'login', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Account not verified')
            raise HTTPException(
                status_code=403, 
                detail=\"Please verify your email or phone number before logging in\"
            )
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Create access token
        access_token = create_access_token(data={\"user_id\": user.id, \"email\": user.email})
        
        # Log success
        log_auth_action(db, user.id, 'login', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        return {
            \"message\": \"Login successful\",
            \"access_token\": access_token,
            \"token_type\": \"bearer\",
            \"user\": {
                \"id\": user.id,
                \"first_name\": user.first_name,
                \"last_name\": user.last_name,
                \"email\": user.email,
                \"phone\": user.phone,
                \"email_verified\": user.email_verified,
                \"phone_verified\": user.phone_verified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=\"Login failed\")

@auth_router.post(\"/send-otp\")
@limiter.limit(\"5/minute\")
async def send_otp(request: Request, data: SendOTPRequest, db: Session = Depends(get_db)):
    \"\"\"Send OTP via email or SMS\"\"\"
    try:
        # Find user
        user = get_user_by_identifier(db, data.identifier)
        
        if not user:
            raise HTTPException(status_code=404, detail=\"User not found\")
        
        # Check if already verified
        if data.otp_type == 'email' and user.email_verified:
            return {\"message\": \"Email already verified\"}
        if data.otp_type == 'sms' and user.phone_verified:
            return {\"message\": \"Phone already verified\"}
        
        # Create and send OTP
        otp_log = create_and_send_otp(db, user, data.otp_type)
        
        # Log action
        log_auth_action(db, user.id, 'otp_send', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        return {
            \"message\": f\"OTP sent to your {data.otp_type}\",
            \"expires_in\": \"10 minutes\"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=\"Failed to send OTP\")

@auth_router.post(\"/verify-otp\")
@limiter.limit(\"5/minute\")
async def verify_otp(request: Request, data: VerifyOTPRequest, db: Session = Depends(get_db)):
    \"\"\"Verify OTP code\"\"\"
    try:
        # Find user
        user = get_user_by_identifier(db, data.identifier)
        
        if not user:
            raise HTTPException(status_code=404, detail=\"User not found\")
        
        # Find latest OTP
        otp_log = db.query(OTPLog).filter(
            OTPLog.user_id == user.id,
            OTPLog.otp_type == data.otp_type,
            OTPLog.verified == False
        ).order_by(OTPLog.created_at.desc()).first()
        
        if not otp_log:
            log_auth_action(db, user.id, 'otp_verify', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'No OTP found')
            raise HTTPException(status_code=404, detail=\"No OTP found. Please request a new one.\")
        
        # Check expiry
        if datetime.now(timezone.utc) > otp_log.expires_at:
            log_auth_action(db, user.id, 'otp_verify', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'OTP expired')
            raise HTTPException(status_code=400, detail=\"OTP has expired\")
        
        # Check attempts (max 5)
        if otp_log.attempts >= 5:
            log_auth_action(db, user.id, 'otp_verify', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Too many attempts')
            raise HTTPException(status_code=400, detail=\"Too many failed attempts. Please request a new OTP.\")
        
        # Increment attempts
        otp_log.attempts += 1
        db.commit()
        
        # Verify OTP
        if otp_log.otp_code != data.otp_code:
            log_auth_action(db, user.id, 'otp_verify', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Invalid OTP')
            raise HTTPException(status_code=400, detail=\"Invalid OTP code\")
        
        # Mark as verified
        otp_log.verified = True
        
        if data.otp_type == 'email':
            user.email_verified = True
        elif data.otp_type == 'sms':
            user.phone_verified = True
        
        db.commit()
        
        # Log success
        log_auth_action(db, user.id, 'otp_verify', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        return {
            \"message\": f\"{data.otp_type.capitalize()} verified successfully\",
            \"email_verified\": user.email_verified,
            \"phone_verified\": user.phone_verified
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=\"Verification failed\")

@auth_router.post(\"/resend-otp\")
@limiter.limit(\"3/minute\")
async def resend_otp(request: Request, data: SendOTPRequest, db: Session = Depends(get_db)):
    \"\"\"Resend OTP\"\"\"
    return await send_otp(request, data, db)

@auth_router.post(\"/forgot-password\")
@limiter.limit(\"3/minute\")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    \"\"\"Initiate password reset\"\"\"
    try:
        # Find user
        user = get_user_by_identifier(db, data.identifier)
        
        if not user:
            # Don't reveal if user exists
            return {\"message\": \"If the account exists, a password reset code has been sent\"}
        
        # Send OTP to both email and SMS
        create_and_send_otp(db, user, 'email')
        create_and_send_otp(db, user, 'sms')
        
        # Log action
        log_auth_action(db, user.id, 'password_reset_request', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        return {
            \"message\": \"Password reset codes sent to your email and phone\",
            \"expires_in\": \"10 minutes\"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=\"Failed to process request\")

@auth_router.post(\"/reset-password\")
@limiter.limit(\"5/minute\")
async def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    \"\"\"Reset password with OTP\"\"\"
    try:
        # Find user
        user = get_user_by_identifier(db, data.identifier)
        
        if not user:
            raise HTTPException(status_code=404, detail=\"User not found\")
        
        # Verify OTP (check both email and SMS)
        otp_valid = False
        for otp_type in ['email', 'sms']:
            otp_log = db.query(OTPLog).filter(
                OTPLog.user_id == user.id,
                OTPLog.otp_type == otp_type,
                OTPLog.otp_code == data.otp_code,
                OTPLog.verified == False,
                OTPLog.expires_at > datetime.now(timezone.utc)
            ).order_by(OTPLog.created_at.desc()).first()
            
            if otp_log and otp_log.attempts < 5:
                otp_log.verified = True
                otp_valid = True
                break
        
        if not otp_valid:
            log_auth_action(db, user.id, 'password_reset', 
                          get_remote_address(request), 
                          request.headers.get('user-agent', ''),
                          'failed', 'Invalid or expired OTP')
            raise HTTPException(status_code=400, detail=\"Invalid or expired OTP\")
        
        # Update password
        user.password_hash = hash_password(data.new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Log success
        log_auth_action(db, user.id, 'password_reset', 
                       get_remote_address(request), 
                       request.headers.get('user-agent', ''),
                       'success')
        
        return {\"message\": \"Password reset successful. Please login with your new password.\"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=\"Password reset failed\")

@auth_router.get(\"/me\")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                          db: Session = Depends(get_db)):
    \"\"\"Get current authenticated user\"\"\"
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail=\"Invalid or expired token\")
    
    user_id = payload.get(\"user_id\")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=\"User not found\")
    
    return {
        \"id\": user.id,
        \"first_name\": user.first_name,
        \"last_name\": user.last_name,
        \"email\": user.email,
        \"phone\": user.phone,
        \"business_name\": user.business_name,
        \"business_type\": user.business_type,
        \"gst_tax_id\": user.gst_tax_id,
        \"email_verified\": user.email_verified,
        \"phone_verified\": user.phone_verified,
        \"created_at\": user.created_at,
        \"last_login\": user.last_login
    }
