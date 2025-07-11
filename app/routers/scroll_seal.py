from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
import logging

from ..database import get_db
from ..models import User, RoleEnum
from ..auth import get_current_user, require_role, require_apostle, require_nation_seer

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

def verify_token_and_role(required_role: RoleEnum):
    """Verify token and check role permission for sacred access"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sacred authentication required"
            )
        
        # Check role hierarchy
        role_hierarchy = {
            RoleEnum.DEACON: 1,
            RoleEnum.ELDER: 2,
            RoleEnum.APOSTLE: 3,
            RoleEnum.NATION_SEER: 4
        }
        
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            logger.warning(f"Access denied: {current_user.name} tried to access {required_role.value} endpoint")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient EXOUSIA. Required role: {required_role.value}. Your role: {current_user.role.value}"
            )
        
        return current_user
    return role_checker

@router.get("/scroll-seal")
async def get_scroll_seal_access(
    current_user: User = Depends(verify_token_and_role(RoleEnum.APOSTLE))
):
    """Get scroll seal access confirmation for sacred operations"""
    try:
        logger.info(f"User {current_user.name} accessed scroll seal with role {current_user.role.value}")
        
        return {
            "access_granted": True,
            "user_id": current_user.id,
            "user_name": current_user.name,
            "role": current_user.role.value,
            "seal_level": "APOSTLE",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Sacred scroll seal access confirmed. You have authority to perform sacred operations."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scroll seal access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred during scroll seal verification"
        )

@router.get("/roles")
async def get_roles(
    current_user: User = Depends(get_current_user)
):
    """Get available EXOUSIA roles and their sacred permissions"""
    try:
        roles = [
            {
                "name": "Deacon",
                "level": 1,
                "permissions": [
                    "view_prophecies",
                    "create_basic_prophecies",
                    "join_prayer_sessions"
                ],
                "description": "Basic scroll access for consecrated believers"
            },
            {
                "name": "Elder",
                "level": 2,
                "permissions": [
                    "view_prophecies",
                    "create_prophecies",
                    "manage_prayer_sessions",
                    "access_bible_characters",
                    "view_holy_land"
                ],
                "description": "Enhanced scroll access with biblical character interaction"
            },
            {
                "name": "Apostle",
                "level": 3,
                "permissions": [
                    "view_prophecies",
                    "create_prophecies",
                    "manage_prayer_sessions",
                    "access_bible_characters",
                    "view_holy_land",
                    "create_scroll_compositions",
                    "manage_users",
                    "start_livestreams",
                    "scroll_seal_access"
                ],
                "description": "Full scroll authority with user management capabilities"
            },
            {
                "name": "Nation Seer",
                "level": 4,
                "permissions": [
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
                    "prophetic_oversight",
                    "scroll_seal_access",
                    "nation_wide_authority"
                ],
                "description": "Supreme scroll authority with prophetic oversight"
            }
        ]
        
        logger.info(f"User {current_user.name} accessed role information")
        
        return {"roles": roles}
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred while accessing role information"
        )

@router.post("/assign-role")
async def assign_role(
    role_data: Dict[str, Any],
    current_user: User = Depends(require_apostle()),
    db: Session = Depends(get_db)
):
    """Assign a sacred role to a user (requires Apostle or higher)"""
    try:
        user_id = role_data.get("user_id")
        new_role_str = role_data.get("role")
        
        if not user_id or not new_role_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID and role are required"
            )
        
        # Validate role
        try:
            new_role = RoleEnum(new_role_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {new_role_str}"
            )
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if current user has authority to assign this role
        role_hierarchy = {
            RoleEnum.DEACON: 1,
            RoleEnum.ELDER: 2,
            RoleEnum.APOSTLE: 3,
            RoleEnum.NATION_SEER: 4
        }
        
        current_user_level = role_hierarchy.get(current_user.role, 0)
        new_role_level = role_hierarchy.get(new_role, 0)
        
        if current_user_level <= new_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign roles lower than your own"
            )
        
        # Update user role
        old_role = user.role
        user.role = new_role
        db.commit()
        
        logger.info(f"User {current_user.name} assigned role {new_role.value} to {user.name}")
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "old_role": old_role.value,
            "new_role": new_role.value,
            "assigned_by": current_user.name,
            "assigned_at": datetime.utcnow().isoformat(),
            "message": f"Sacred role {new_role.value} assigned successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred during role assignment"
        )

@router.get("/my-permissions")
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get current user's sacred permissions based on EXOUSIA role"""
    try:
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
                "start_livestreams",
                "scroll_seal_access"
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
                "prophetic_oversight",
                "scroll_seal_access",
                "nation_wide_authority"
            ]
        }
        
        user_permissions = permissions_map.get(current_user.role, [])
        
        logger.info(f"User {current_user.name} checked their permissions")
        
        return {
            "user_id": current_user.id,
            "user_name": current_user.name,
            "role": current_user.role.value,
            "permissions": user_permissions,
            "permission_count": len(user_permissions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching permissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred while accessing permission information"
        )

@router.get("/seal-status")
async def get_seal_status(
    current_user: User = Depends(require_nation_seer())
):
    """Get sacred scroll seal status (Nation Seer only)"""
    try:
        logger.info(f"Nation Seer {current_user.name} accessed seal status")
        
        return {
            "seal_active": True,
            "seal_level": "NATION_SEER",
            "user_id": current_user.id,
            "user_name": current_user.name,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Sacred scroll seal is active and under prophetic oversight"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in seal status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred during seal status verification"
        ) 