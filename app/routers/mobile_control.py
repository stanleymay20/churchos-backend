from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models import User
from ..auth import get_current_user

router = APIRouter()

@router.post("/mobile/start-service")
async def start_service(
    service_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Start a service from mobile control"""
    try:
        return {
            "service_id": "service_123",
            "type": service_data["type"],
            "started_by": current_user.name,
            "start_time": datetime.utcnow().isoformat(),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting service: {str(e)}"
        )

@router.post("/mobile/project-content")
async def project_content(
    content_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Project prayer or scripture remotely"""
    try:
        return {
            "projection_id": "proj_456",
            "content_type": content_data["type"],
            "content": content_data["content"],
            "projected_by": current_user.name,
            "projection_time": datetime.utcnow().isoformat(),
            "duration": content_data.get("duration", 30)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error projecting content: {str(e)}"
        )

@router.post("/mobile/push-prophecy")
async def push_prophecy(
    prophecy_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Push prophecies to dashboard from mobile"""
    try:
        return {
            "prophecy_id": "prop_789",
            "message": prophecy_data["message"],
            "urgency": prophecy_data.get("urgency", "medium"),
            "pushed_by": current_user.name,
            "push_time": datetime.utcnow().isoformat(),
            "status": "pushed_to_dashboard"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error pushing prophecy: {str(e)}"
        ) 