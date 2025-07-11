from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..database import get_db
from ..auth import verify_token_and_role
from ..models import User, Prophecy, ScrollCycle, PrayerRequest
from ..schemas.scroll_dashboard import DashboardData, ProphecyItem, ScrollCycleItem

router = APIRouter()

@router.get("/", response_model=DashboardData)
async def get_scroll_dashboard(
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get live dashboard data with prophetic cycles and assigned scrolls
    Access: Elder role required
    """
    try:
        # Get recent prophecies
        recent_prophecies = db.query(Prophecy).filter(
            Prophecy.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(desc(Prophecy.created_at)).limit(10).all()
        
        # Format prophecies for response
        prophecy_items = []
        for prophecy in recent_prophecies:
            user = db.query(User).filter(User.id == prophecy.user_id).first()
            prophecy_items.append(
                ProphecyItem(
                    id=prophecy.id,
                    message=prophecy.message,
                    timestamp=prophecy.created_at,
                    urgency=prophecy.urgency,
                    role=user.role if user else "Unknown",
                    status=prophecy.status,
                    user_id=prophecy.user_id,
                    username=user.username if user else "Unknown"
                )
            )
        
        # Get active scroll cycles
        active_cycles = db.query(ScrollCycle).filter(
            ScrollCycle.status == "active"
        ).order_by(desc(ScrollCycle.created_at)).limit(5).all()
        
        # Format scroll cycles for response
        scroll_cycle_items = []
        for cycle in active_cycles:
            user = db.query(User).filter(User.id == cycle.user_id).first()
            scroll_cycle_items.append(
                ScrollCycleItem(
                    id=cycle.id,
                    start_time=cycle.start_time,
                    end_time=cycle.end_time,
                    participants=cycle.participants,
                    status=cycle.status,
                    user_id=cycle.user_id,
                    username=user.username if user else "Unknown",
                    description=cycle.description
                )
            )
        
        # Get pending prophecies count
        pending_prophecies = db.query(Prophecy).filter(
            Prophecy.status == "Pending"
        ).count()
        
        # Get active scroll cycles count
        active_cycles_count = db.query(ScrollCycle).filter(
            ScrollCycle.status == "active"
        ).count()
        
        # Get recent prayer requests
        recent_prayers = db.query(PrayerRequest).filter(
            PrayerRequest.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(desc(PrayerRequest.created_at)).limit(5).all()
        
        # Get user statistics
        total_users = db.query(User).count()
        active_users_today = db.query(User).filter(
            User.last_login >= datetime.utcnow().date()
        ).count()
        
        # Get role distribution
        role_distribution = {
            "Deacon": db.query(User).filter(User.role == "Deacon").count(),
            "Elder": db.query(User).filter(User.role == "Elder").count(),
            "Apostle": db.query(User).filter(User.role == "Apostle").count(),
            "Nation Seer": db.query(User).filter(User.role == "Nation Seer").count()
        }
        
        # Get prophecy status distribution
        prophecy_status = {
            "Pending": db.query(Prophecy).filter(Prophecy.status == "Pending").count(),
            "Active": db.query(Prophecy).filter(Prophecy.status == "Active").count(),
            "Fulfilled": db.query(Prophecy).filter(Prophecy.status == "Fulfilled").count(),
            "Archived": db.query(Prophecy).filter(Prophecy.status == "Archived").count()
        }
        
        # Get urgent prophecies
        urgent_prophecies = db.query(Prophecy).filter(
            Prophecy.urgency == "High",
            Prophecy.status.in_(["Pending", "Active"])
        ).order_by(desc(Prophecy.created_at)).limit(3).all()
        
        urgent_items = []
        for prophecy in urgent_prophecies:
            user = db.query(User).filter(User.id == prophecy.user_id).first()
            urgent_items.append(
                ProphecyItem(
                    id=prophecy.id,
                    message=prophecy.message,
                    timestamp=prophecy.created_at,
                    urgency=prophecy.urgency,
                    role=user.role if user else "Unknown",
                    status=prophecy.status,
                    user_id=prophecy.user_id,
                    username=user.username if user else "Unknown"
                )
            )
        
        return DashboardData(
            prophecies=prophecy_items,
            scroll_cycles=scroll_cycle_items,
            urgent_prophecies=urgent_items,
            pending_prophecies_count=pending_prophecies,
            active_cycles_count=active_cycles_count,
            total_users=total_users,
            active_users_today=active_users_today,
            role_distribution=role_distribution,
            prophecy_status=prophecy_status,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

@router.get("/prophecies")
async def get_prophecies(
    limit: int = 20,
    status: Optional[str] = None,
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get prophecies with optional filtering
    Access: Elder role required
    """
    try:
        query = db.query(Prophecy)
        
        if status:
            query = query.filter(Prophecy.status == status)
        
        prophecies = query.order_by(desc(Prophecy.created_at)).limit(limit).all()
        
        prophecy_list = []
        for prophecy in prophecies:
            user = db.query(User).filter(User.id == prophecy.user_id).first()
            prophecy_list.append({
                "id": prophecy.id,
                "message": prophecy.message,
                "timestamp": prophecy.created_at,
                "urgency": prophecy.urgency,
                "status": prophecy.status,
                "user": {
                    "id": user.id if user else None,
                    "username": user.username if user else "Unknown",
                    "role": user.role if user else "Unknown"
                }
            })
        
        return {
            "prophecies": prophecy_list,
            "total": len(prophecy_list),
            "status_filter": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve prophecies: {str(e)}"
        )

@router.get("/scroll-cycles")
async def get_scroll_cycles(
    status: Optional[str] = None,
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get scroll cycles with optional filtering
    Access: Elder role required
    """
    try:
        query = db.query(ScrollCycle)
        
        if status:
            query = query.filter(ScrollCycle.status == status)
        
        cycles = query.order_by(desc(ScrollCycle.created_at)).all()
        
        cycle_list = []
        for cycle in cycles:
            user = db.query(User).filter(User.id == cycle.user_id).first()
            cycle_list.append({
                "id": cycle.id,
                "start_time": cycle.start_time,
                "end_time": cycle.end_time,
                "participants": cycle.participants,
                "status": cycle.status,
                "description": cycle.description,
                "user": {
                    "id": user.id if user else None,
                    "username": user.username if user else "Unknown",
                    "role": user.role if user else "Unknown"
                }
            })
        
        return {
            "scroll_cycles": cycle_list,
            "total": len(cycle_list),
            "status_filter": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scroll cycles: {str(e)}"
        )

@router.get("/user/{user_id}")
async def get_user_dashboard(
    user_id: int,
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get dashboard data for a specific user
    Access: Elder role required
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user's prophecies
        user_prophecies = db.query(Prophecy).filter(
            Prophecy.user_id == user_id
        ).order_by(desc(Prophecy.created_at)).limit(10).all()
        
        # Get user's scroll cycles
        user_cycles = db.query(ScrollCycle).filter(
            ScrollCycle.user_id == user_id
        ).order_by(desc(ScrollCycle.created_at)).limit(5).all()
        
        # Get user's prayer requests
        user_prayers = db.query(PrayerRequest).filter(
            PrayerRequest.user_id == user_id
        ).order_by(desc(PrayerRequest.created_at)).limit(5).all()
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "email": user.email,
                "created_at": user.created_at,
                "last_login": user.last_login
            },
            "prophecies": [
                {
                    "id": p.id,
                    "message": p.message,
                    "timestamp": p.created_at,
                    "urgency": p.urgency,
                    "status": p.status
                } for p in user_prophecies
            ],
            "scroll_cycles": [
                {
                    "id": c.id,
                    "start_time": c.start_time,
                    "end_time": c.end_time,
                    "status": c.status,
                    "description": c.description
                } for c in user_cycles
            ],
            "prayer_requests": [
                {
                    "id": pr.id,
                    "topic": pr.topic,
                    "message": pr.message,
                    "timestamp": pr.created_at,
                    "status": pr.status
                } for pr in user_prayers
            ],
            "statistics": {
                "total_prophecies": len(user_prophecies),
                "total_cycles": len(user_cycles),
                "total_prayers": len(user_prayers),
                "pending_prophecies": len([p for p in user_prophecies if p.status == "Pending"]),
                "active_cycles": len([c for c in user_cycles if c.status == "active"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user dashboard: {str(e)}"
        ) 