from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models import PrayerSession, User
from ..auth import get_current_user

router = APIRouter()

@router.post("/start-stream")
async def start_stream(
    stream_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new prayer livestream"""
    try:
        session = PrayerSession(
            title=stream_data["title"],
            description=stream_data.get("description", ""),
            start_time=datetime.utcnow(),
            is_live=True,
            creator_id=current_user.id
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "id": session.id,
            "title": session.title,
            "stream_url": f"rtmp://localhost/live/prayer_{session.id}",
            "is_live": session.is_live
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting stream: {str(e)}"
        )

@router.post("/join-prayer")
async def join_prayer_room(
    room_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Join a prayer intercession room"""
    try:
        room_id = room_data["room_id"]
        
        return {
            "room_id": room_id,
            "user_id": current_user.id,
            "user_name": current_user.name,
            "join_time": datetime.utcnow().isoformat(),
            "webrtc_config": {
                "ice_servers": [
                    {"urls": "stun:stun.l.google.com:19302"}
                ]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error joining prayer room: {str(e)}"
        )

@router.post("/log-prayer")
async def log_prayer(
    prayer_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a prayer or intercession"""
    try:
        # In a real implementation, this would save to a prayer log table
        return {
            "id": "prayer_123",
            "user_id": current_user.id,
            "user_name": current_user.name,
            "prayer_text": prayer_data["prayer_text"],
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": prayer_data.get("session_id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error logging prayer: {str(e)}"
        )

@router.post("/upload-decree")
async def upload_decree(
    decree_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Upload a prophetic decree or declaration"""
    try:
        return {
            "id": "decree_456",
            "user_id": current_user.id,
            "decree_text": decree_data["decree_text"],
            "timestamp": datetime.utcnow().isoformat(),
            "type": decree_data.get("type", "prophetic_decree")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading decree: {str(e)}"
        ) 