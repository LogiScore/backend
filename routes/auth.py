from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import uuid
import random
import string
import os

from database.database import get_db
from database.models import User
from auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from email_service import email_service

router = APIRouter()

class EmailAuthRequest(BaseModel):
    email: str
    user_type: Optional[str] = "shipper"  # Allow users to specify their type
    company_name: Optional[str] = None

class CodeVerificationRequest(BaseModel):
    email: str
    code: str

class EmailAuthResponse(BaseModel):
    message: str
    expires_in: int

class CodeVerificationResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

async def send_verification_email(email: str, code: str, expires_in: int) -> bool:
    """Send verification code email using SendGrid"""
    try:
        # Use the SendGrid email service
        return await email_service.send_verification_code(email, code)
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@router.post("/send-code", response_model=EmailAuthResponse)
async def send_verification_code(
    request: EmailAuthRequest,
    db: Session = Depends(get_db)
):
    """Send verification code to user's email"""
    try:
        email = request.email.lower().strip()
        user_type = request.user_type or "shipper"  # Default to shipper if not specified
        company_name = request.company_name
        
        # Validate user_type
        if user_type not in ["shipper", "forwarder", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user type. Must be 'shipper', 'forwarder', or 'admin'"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        # Generate verification code
        code = generate_verification_code()
        expires_in = 10  # 10 minutes
        
        # Store code in user record (or create user if doesn't exist)
        if user:
            # Update existing user
            user.verification_code = code
            user.verification_code_expires = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        else:
            # Generate unique username
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            # Check if username exists and generate unique one if needed
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
                if counter > 100:  # Prevent infinite loop
                    username = f"{base_username}_{uuid.uuid4().hex[:8]}"
                    break
            
            # Create new user with proper user_type
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                user_type=user_type,  # Use the specified user type
                company_name=company_name,
                subscription_tier="free",
                is_verified=False,
                is_active=True,
                verification_code=code,
                verification_code_expires=datetime.now(timezone.utc) + timedelta(minutes=expires_in)
            )
            db.add(user)
        
        db.commit()
        
        # Send verification email
        if await send_verification_email(email, code, expires_in):
            return EmailAuthResponse(
                message="Verification code sent to your email",
                expires_in=expires_in
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post("/verify-code", response_model=CodeVerificationResponse)
async def verify_code(
    request: CodeVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify the code and authenticate user"""
    try:
        email = request.email.lower().strip()
        code = request.code.strip()
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if code is valid and not expired
        if not user.verification_code or user.verification_code != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        if not user.verification_code_expires or user.verification_code_expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired"
            )
        
        # Clear verification code
        user.verification_code = None
        user.verification_code_expires = None
        user.is_verified = True
        db.commit()
        
        # Generate access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Return user data
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "company_name": user.company_name,
            "user_type": user.user_type,
            "subscription_tier": user.subscription_tier,
            "is_verified": user.is_verified,
            "is_active": user.is_active
        }
        
        return CodeVerificationResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        ) 