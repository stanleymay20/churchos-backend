from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models import HolyLandScene, User
from ..auth import get_current_user

router = APIRouter()

@router.get("/holy-land/scenes")
async def get_holy_land_scenes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available Holy Land scenes"""
    try:
        scenes = db.query(HolyLandScene).filter(HolyLandScene.is_active == True).all()
        
        return {
            "scenes": [
                {
                    "id": scene.id,
                    "name": scene.name,
                    "description": scene.description,
                    "scene_data": scene.scene_data,
                    "triggers": scene.triggers
                }
                for scene in scenes
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching scenes: {str(e)}"
        )

@router.post("/holy-land/visit")
async def log_visit(
    visit_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Log a visit to a Holy Land scene"""
    try:
        return {
            "user_id": current_user.id,
            "scene_id": visit_data["scene_id"],
            "visit_time": datetime.utcnow().isoformat(),
            "coordinates": visit_data.get("coordinates"),
            "triggers_activated": visit_data.get("triggers", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error logging visit: {str(e)}"
        ) 