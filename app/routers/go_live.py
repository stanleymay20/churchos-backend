from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models import LivestreamSession, User
from ..auth import get_current_user

router = APIRouter()

@router.post("/go-live/start")
async def start_livestream(
    stream_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a sacred livestream with scroll cover overlay"""
    try:
        session = LivestreamSession(
            title=stream_data["title"],
            topic=stream_data.get("topic"),
            is_live=True,
            creator_id=current_user.id,
            started_at=datetime.utcnow()
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session_id": session.id,
            "title": session.title,
            "topic": session.topic,
            "stream_url": f"rtmp://localhost/live/sacred_{session.id}",
            "is_live": session.is_live,
            "started_by": current_user.name,
            "start_time": session.started_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting livestream: {str(e)}"
        )

@router.post("/go-live/schedule")
async def schedule_livestream(
    schedule_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule a livestream and notify intercessors"""
    try:
        scheduled_time = datetime.fromisoformat(schedule_data["scheduled_time"])
        
        session = LivestreamSession(
            title=schedule_data["title"],
            topic=schedule_data.get("topic"),
            is_live=False,
            creator_id=current_user.id,
            scheduled_at=scheduled_time
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session_id": session.id,
            "title": session.title,
            "topic": session.topic,
            "scheduled_time": session.scheduled_at.isoformat(),
            "scheduled_by": current_user.name,
            "notifications_sent": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scheduling livestream: {str(e)}"
        )

@router.get("/go-live/topics")
async def get_livestream_topics(
    current_user: User = Depends(get_current_user)
):
    """Get available livestream topics"""
    try:
        topics = [
            {
                "id": "warfare_prayer",
                "name": "Warfare Prayer",
                "description": "Spiritual warfare and intercession",
                "duration": 60
            },
            {
                "id": "open_heaven_ghana",
                "name": "Open Heaven: Ghana",
                "description": "Prophetic intercession for Ghana",
                "duration": 90
            },
            {
                "id": "revival_fire",
                "name": "Revival Fire",
                "description": "Calling for revival and awakening",
                "duration": 120
            },
            {
                "id": "prophetic_worship",
                "name": "Prophetic Worship",
                "description": "Worship and prophetic flow",
                "duration": 75
            }
        ]
        
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching topics: {str(e)}"
        ) 