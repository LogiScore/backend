from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import httpx
import os
from dotenv import load_dotenv

from database.database import get_db
from database.models import User

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_expired_token(token: str) -> Optional[dict]:
    """Verify and decode an expired JWT token for refresh purposes"""
    try:
        # Decode without expiration validation
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"DEBUG: Validating token: {credentials.credentials[:20]}...")  # Debug log
        payload = verify_token(credentials.credentials)
        if payload is None:
            print("DEBUG: Token verification failed - payload is None")  # Debug log
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            print("DEBUG: Token verification failed - no user_id in payload")  # Debug log
            raise credentials_exception
        print(f"DEBUG: Token verified for user_id: {user_id}")  # Debug log
    except JWTError as e:
        print(f"DEBUG: JWT error during token verification: {e}")  # Debug log
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"DEBUG: User not found in database for user_id: {user_id}")  # Debug log
        raise credentials_exception
    print(f"DEBUG: User found: {user.email}")  # Debug log
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Get current user from JWT token if provided, otherwise return None (for anonymous reviews)"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name
    }

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def authenticate_github_user(code: str, db: Session) -> Optional[User]:
    """Authenticate user with GitHub OAuth"""
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    if not github_client_id or not github_client_secret:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": github_client_id,
                "client_secret": github_client_secret,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        github_user = user_response.json()
        
        # Get user email
        emails_response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        emails = emails_response.json() if emails_response.status_code == 200 else []
        primary_email = next((email["email"] for email in emails if email["primary"]), None)
        
        # Check if user exists
        user = db.query(User).filter(User.github_id == str(github_user["id"])).first()
        
        if not user:
            # Create new user
            user = User(
                github_id=str(github_user["id"]),
                email=primary_email or github_user.get("email", ""),
                username=github_user["login"],
                full_name=github_user.get("name", ""),
                avatar_url=github_user.get("avatar_url", ""),
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user
            user.email = primary_email or github_user.get("email", user.email)
            user.username = github_user["login"]
            user.full_name = github_user.get("name", user.full_name)
            user.avatar_url = github_user.get("avatar_url", user.avatar_url)
            db.commit()
            db.refresh(user)
        
        return user 