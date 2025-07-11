from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database import get_db
from ..models import ScrollComposition, User
from ..auth import get_current_user

router = APIRouter()

@router.post("/save-scroll")
async def save_scroll_composition(
    composition_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a scroll composition (sermon/worship slides)"""
    try:
        composition = ScrollComposition(
            title=composition_data["title"],
            content=composition_data["content"],
            creator_id=current_user.id,
            is_published=composition_data.get("is_published", False)
        )
        
        db.add(composition)
        db.commit()
        db.refresh(composition)
        
        return {
            "id": composition.id,
            "title": composition.title,
            "created_at": composition.created_at.isoformat(),
            "is_published": composition.is_published
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving scroll: {str(e)}"
        )

@router.post("/render-slide")
async def render_slide(
    slide_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Render a slide for stage display"""
    try:
        return {
            "slide_id": "slide_123",
            "title": slide_data["title"],
            "content": slide_data["content"],
            "background": slide_data.get("background", "default"),
            "font_size": slide_data.get("font_size", "large"),
            "animation": slide_data.get("animation", "fade"),
            "duration": slide_data.get("duration", 10)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error rendering slide: {str(e)}"
        ) 