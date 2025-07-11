from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import auth, credentials
import os
from typing import Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import logging
from .database import get_db
from .models import User, RoleEnum

# Configure logging for authentication events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK with proper error handling
def initialize_firebase():
    """Initialize Firebase Admin SDK with proper configuration"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Try to load service account key from environment
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized with service account")
            else:
                # For development, use default credentials
                firebase_admin.initialize_app()
                logger.info("Firebase Admin SDK initialized with default credentials")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        raise

# Initialize Firebase on module import
initialize_firebase()

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=True)

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify Firebase JWT token and return decoded user data
    Handles token expiration, invalid signatures, and malformed tokens
    """
    try:
        token = credentials.credentials
        
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        
        # Validate required fields
        if not decoded_token.get("uid"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check token expiration
        exp = decoded_token.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Token verified for user: {decoded_token.get('uid')}")
        return decoded_token
        
    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase token detected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.RevokedIdTokenError:
        logger.warning("Revoked Firebase token detected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase token detected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get or create current user from database based on Firebase UID
    Handles user creation for new Firebase users
    """
    try:
        firebase_uid = token_data.get("uid")
        if not firebase_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data: missing UID"
            )
        
        # Check if user exists in database
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            # Create new user with default role
            user = User(
                firebase_uid=firebase_uid,
                email=token_data.get("email", ""),
                name=token_data.get("name", token_data.get("display_name", "Unknown User")),
                role=RoleEnum.DEACON  # Default role for new users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.name} (UID: {firebase_uid})")
        else:
            # Update user information if needed
            if user.email != token_data.get("email", ""):
                user.email = token_data.get("email", "")
                db.commit()
                logger.info(f"Updated user email: {user.name}")
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user data"
        )

def check_role_permission(user: User, required_role: RoleEnum) -> bool:
    """
    Check if user has required role permission using EXOUSIA hierarchy
    Returns True if user's role level >= required role level
    """
    role_hierarchy = {
        RoleEnum.DEACON: 1,
        RoleEnum.ELDER: 2,
        RoleEnum.APOSTLE: 3,
        RoleEnum.NATION_SEER: 4
    }
    
    user_level = role_hierarchy.get(user.role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    has_permission = user_level >= required_level
    
    logger.info(f"Role check: {user.name} ({user.role.value}) -> {required_role.value} = {has_permission}")
    
    return has_permission

def require_role(required_role: RoleEnum):
    """
    Async route guard decorator to require specific EXOUSIA role
    Usage: @app.get("/admin") @require_role(RoleEnum.APOSTLE)
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if not check_role_permission(current_user, required_role):
            logger.warning(f"Access denied: {current_user.name} tried to access {required_role.value} endpoint")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}. Your role: {current_user.role.value}"
            )
        return current_user
    return role_checker

def require_minimum_role(minimum_role: RoleEnum):
    """
    Async route guard for minimum role requirement
    Allows access if user has minimum role or higher
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if not check_role_permission(current_user, minimum_role):
            logger.warning(f"Access denied: {current_user.name} tried to access minimum {minimum_role.value} endpoint")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Minimum required role: {minimum_role.value}. Your role: {current_user.role.value}"
            )
        return current_user
    return role_checker

async def get_user_permissions(user: User) -> list:
    """
    Get user's permissions based on their EXOUSIA role
    Returns list of permission strings
    """
    permissions_map = {
        RoleEnum.DEACON: [
            "view_prophecies",
            "create_basic_prophecies",
            "join_prayer_sessions"
        ],
        RoleEnum.ELDER: [
            "view_prophecies",
            "create_prophecies",
            "manage_prayer_sessions",
            "access_bible_characters",
            "view_holy_land"
        ],
        RoleEnum.APOSTLE: [
            "view_prophecies",
            "create_prophecies",
            "manage_prayer_sessions",
            "access_bible_characters",
            "view_holy_land",
            "create_scroll_compositions",
            "manage_users",
            "start_livestreams"
        ],
        RoleEnum.NATION_SEER: [
            "view_prophecies",
            "create_prophecies",
            "manage_prayer_sessions",
            "access_bible_characters",
            "view_holy_land",
            "create_scroll_compositions",
            "manage_users",
            "start_livestreams",
            "manage_roles",
            "access_all_modules",
            "prophetic_oversight"
        ]
    }
    
    return permissions_map.get(user.role, [])

# Convenience functions for common role checks
def require_deacon():
    """Require at least Deacon role"""
    return require_minimum_role(RoleEnum.DEACON)

def require_elder():
    """Require at least Elder role"""
    return require_minimum_role(RoleEnum.ELDER)

def require_apostle():
    """Require at least Apostle role"""
    return require_minimum_role(RoleEnum.APOSTLE)

def require_nation_seer():
    """Require Nation Seer role (highest level)"""
    return require_role(RoleEnum.NATION_SEER) 