from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..database import get_db
from ..auth import verify_token_and_role
from ..models import User, Prophecy, ScrollCycle, PrayerRequest
from ..schemas.analytics import AnalyticsOverview, TopVerse, PrayerTopic, LivestreamStats

router = APIRouter()

@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: Dict = Depends(verify_token_and_role("Apostle")),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics overview for sacred dashboard
    Access: Apostle role required
    """
    try:
        # Calculate date ranges
        now = datetime.utcnow()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        
        # Get total counts
        total_users = db.query(User).count()
        total_prophecies = db.query(Prophecy).count()
        total_scroll_cycles = db.query(ScrollCycle).count()
        total_prayers = db.query(PrayerRequest).count()
        
        # Get recent activity
        recent_prophecies = db.query(Prophecy).filter(
            Prophecy.created_at >= last_7_days
        ).count()
        
        recent_prayers = db.query(PrayerRequest).filter(
            PrayerRequest.created_at >= last_7_days
        ).count()
        
        # Get top verses (mock data for now)
        top_verses = [
            TopVerse(
                verse="John 3:16",
                reference="John 3:16",
                usage_count=156,
                last_used=now - timedelta(hours=2)
            ),
            TopVerse(
                verse="Psalm 23:1",
                reference="Psalm 23:1",
                usage_count=89,
                last_used=now - timedelta(hours=5)
            ),
            TopVerse(
                verse="Romans 8:28",
                reference="Romans 8:28",
                usage_count=67,
                last_used=now - timedelta(hours=8)
            ),
            TopVerse(
                verse="Philippians 4:13",
                reference="Philippians 4:13",
                usage_count=45,
                last_used=now - timedelta(hours=12)
            ),
            TopVerse(
                verse="Jeremiah 29:11",
                reference="Jeremiah 29:11",
                usage_count=34,
                last_used=now - timedelta(hours=24)
            )
        ]
        
        # Get prayer topics (mock data)
        prayer_topics = [
            PrayerTopic(
                topic="Healing",
                request_count=89,
                urgency_level="High",
                last_request=now - timedelta(hours=1)
            ),
            PrayerTopic(
                topic="Guidance",
                request_count=67,
                urgency_level="Medium",
                last_request=now - timedelta(hours=3)
            ),
            PrayerTopic(
                topic="Protection",
                request_count=45,
                urgency_level="High",
                last_request=now - timedelta(hours=2)
            ),
            PrayerTopic(
                topic="Wisdom",
                request_count=34,
                urgency_level="Medium",
                last_request=now - timedelta(hours=6)
            ),
            PrayerTopic(
                topic="Peace",
                request_count=23,
                urgency_level="Low",
                last_request=now - timedelta(hours=12)
            )
        ]
        
        # Get livestream stats (mock data)
        livestream_stats = LivestreamStats(
            total_sessions=24,
            total_duration_hours=156.5,
            average_viewers=45,
            peak_viewers=89,
            total_participants=234,
            last_session=now - timedelta(hours=2),
            upcoming_sessions=3
        )
        
        # Get user activity heatmap (mock data)
        activity_heatmap = {
            "monday": {"morning": 15, "afternoon": 23, "evening": 34},
            "tuesday": {"morning": 12, "afternoon": 28, "evening": 41},
            "wednesday": {"morning": 18, "afternoon": 31, "evening": 38},
            "thursday": {"morning": 14, "afternoon": 26, "evening": 35},
            "friday": {"morning": 16, "afternoon": 29, "evening": 42},
            "saturday": {"morning": 22, "afternoon": 35, "evening": 48},
            "sunday": {"morning": 45, "afternoon": 52, "evening": 38}
        }
        
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
        
        return AnalyticsOverview(
            total_users=total_users,
            total_prophecies=total_prophecies,
            total_scroll_cycles=total_scroll_cycles,
            total_prayers=total_prayers,
            recent_prophecies=recent_prophecies,
            recent_prayers=recent_prayers,
            top_verses=top_verses,
            prayer_topics=prayer_topics,
            livestream_stats=livestream_stats,
            activity_heatmap=activity_heatmap,
            role_distribution=role_distribution,
            prophecy_status=prophecy_status,
            last_updated=now
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics data: {str(e)}"
        )

@router.get("/daily-stats")
async def get_daily_stats(
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get daily statistics for dashboard
    Access: Elder role required
    """
    try:
        today = datetime.utcnow().date()
        
        # Get today's stats
        today_prophecies = db.query(Prophecy).filter(
            func.date(Prophecy.created_at) == today
        ).count()
        
        today_prayers = db.query(PrayerRequest).filter(
            func.date(PrayerRequest.created_at) == today
        ).count()
        
        today_users = db.query(User).filter(
            func.date(User.created_at) == today
        ).count()
        
        return {
            "date": today.isoformat(),
            "prophecies": today_prophecies,
            "prayers": today_prayers,
            "new_users": today_users,
            "active_users": 45,  # Mock data
            "scroll_cycles_completed": 3  # Mock data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve daily stats: {str(e)}"
        )

@router.get("/user-activity/{user_id}")
async def get_user_activity(
    user_id: int,
    current_user: Dict = Depends(verify_token_and_role("Elder")),
    db: Session = Depends(get_db)
):
    """
    Get activity statistics for a specific user
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
        ).count()
        
        # Get user's prayers
        user_prayers = db.query(PrayerRequest).filter(
            PrayerRequest.user_id == user_id
        ).count()
        
        # Get user's scroll cycles
        user_scroll_cycles = db.query(ScrollCycle).filter(
            ScrollCycle.user_id == user_id
        ).count()
        
        return {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
            "total_prophecies": user_prophecies,
            "total_prayers": user_prayers,
            "total_scroll_cycles": user_scroll_cycles,
            "last_activity": user.last_login,
            "member_since": user.created_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user activity: {str(e)}"
        )

@router.get("/prophecy-trends")
async def get_prophecy_trends(
    days: int = 30,
    current_user: Dict = Depends(verify_token_and_role("Apostle")),
    db: Session = Depends(get_db)
):
    """
    Get prophecy trends over specified days
    Access: Apostle role required
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get prophecies by date
        prophecies = db.query(
            func.date(Prophecy.created_at).label('date'),
            func.count(Prophecy.id).label('count')
        ).filter(
            Prophecy.created_at >= start_date,
            Prophecy.created_at <= end_date
        ).group_by(
            func.date(Prophecy.created_at)
        ).order_by(
            func.date(Prophecy.created_at)
        ).all()
        
        # Format data for frontend
        trends = []
        for prophecy in prophecies:
            trends.append({
                "date": prophecy.date.isoformat(),
                "count": prophecy.count
            })
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "trends": trends,
            "total_prophecies": sum(t['count'] for t in trends)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve prophecy trends: {str(e)}"
        ) 