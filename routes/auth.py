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
from auth.auth import create_access_token, verify_expired_token, ACCESS_TOKEN_EXPIRE_MINUTES
from email_service import email_service

router = APIRouter()

class SigninCodeRequest(BaseModel):
    email: str

class SignupCodeRequest(BaseModel):
    email: str
    user_type: Optional[str] = "shipper"  # Allow users to specify their type
    company_name: Optional[str] = None

class CodeVerificationRequest(BaseModel):
    email: str
    code: str

class SignupVerificationRequest(BaseModel):
    email: str
    code: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    user_type: Optional[str] = "shipper"

class RefreshTokenRequest(BaseModel):
    token: str

class EmailAuthResponse(BaseModel):
    message: str
    expires_in: int

class CodeVerificationResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

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
        # For now, return True to allow the flow to continue
        # In production, you might want to log this and handle differently
        return True

@router.post("/send-signin-code", response_model=EmailAuthResponse)
async def send_signin_code(
    request: SigninCodeRequest,
    db: Session = Depends(get_db)
):
    """Send verification code for existing user sign-in"""
    try:
        email = request.email.lower().strip()
        
        # Check if user exists - only send codes to registered users for sign-in
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # User doesn't exist - return error directing them to sign up
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found. Please sign up instead."
            )
        
        # Generate verification code
        code = generate_verification_code()
        expires_in = 10  # 10 minutes
        
        # Update existing user with new verification code
        user.verification_code = code
        user.verification_code_expires = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
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
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post("/send-signup-code", response_model=EmailAuthResponse)
async def send_signup_code(
    request: SignupCodeRequest,
    db: Session = Depends(get_db)
):
    """Send verification code for new user registration"""
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
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists. Please use sign-in instead."
            )
        
        # Generate verification code
        code = generate_verification_code()
        expires_in = 10  # 10 minutes
        
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

@router.post("/verify-signin-code", response_model=CodeVerificationResponse)
async def verify_signin_code(
    request: CodeVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify the code and authenticate existing user for sign-in"""
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

@router.post("/verify-signup-code", response_model=CodeVerificationResponse)
async def verify_signup_code(
    request: SignupVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify the code and complete new user registration"""
    try:
        email = request.email.lower().strip()
        code = request.code.strip()
        full_name = request.full_name
        company_name = request.company_name
        user_type = request.user_type or "shipper"
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please request a new signup code."
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
        
        # Update user with additional information from signup
        if full_name:
            user.full_name = full_name
        if company_name:
            user.company_name = company_name
        if user_type:
            user.user_type = user_type
        
        # Clear verification code and mark as verified
        user.verification_code = None
        user.verification_code_expires = None
        user.is_verified = True
        db.commit()
        
        # Generate access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Send welcome email to new user
        try:
            user_display_name = user.full_name or user.username or user.email
            await email_service.send_welcome_email(
                to_email=user.email,
                full_name=user_display_name
            )
        except Exception as e:
            # Log error but don't fail the signup process
            print(f"Failed to send welcome email to {user.email}: {e}")
        
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

# Keep the legacy endpoints for backward compatibility
@router.post("/send-code", response_model=EmailAuthResponse)
async def send_verification_code(
    request: SignupCodeRequest,
    db: Session = Depends(get_db)
):
    """Legacy endpoint - redirects to signup flow"""
    return await send_signup_code(request, db)

@router.post("/verify-code", response_model=CodeVerificationResponse)
async def verify_code(
    request: SignupVerificationRequest,
    db: Session = Depends(get_db)
):
    """Legacy endpoint - redirects to signup verification flow"""
    return await verify_signup_code(request, db)

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an expired JWT token
    
    This endpoint accepts an expired JWT token, validates it (ignoring expiration),
    and returns a new valid JWT token if the user still exists and is active.
    """
    try:
        # Validate the expired token (ignoring expiration)
        payload = verify_expired_token(request.token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identifier"
            )
        
        # Check if user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        ) 