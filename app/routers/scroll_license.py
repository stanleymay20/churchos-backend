from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from datetime import datetime, timedelta
import uuid

from ..database import get_db
from ..models.user import User
from ..models.scroll_license import ScrollLicenseRequest
from ..schemas.scroll_license import ScrollLicenseRequestCreate, ScrollLicenseRequestResponse
from ..auth.firebase_auth import get_current_user
from ..config import settings

router = APIRouter(prefix="/scroll-license", tags=["ScrollLicense"])

# Pre-filled apostolic accounts for launch
APOSTOLIC_ACCOUNTS = [
    {
        "name": "Prophet Sarah Johnson",
        "email": "sarah.johnson@churchos.app",
        "role": "apostle",
        "country": "us",
        "ministry": "Global Prophetic Network",
        "teamSize": "21-50",
        "experience": "expert",
        "purpose": "Leading apostolic network across North America"
    },
    {
        "name": "Apostle Michael Chen",
        "email": "michael.chen@churchos.app",
        "role": "apostle",
        "country": "ca",
        "ministry": "Canadian Apostolic Alliance",
        "teamSize": "51-100",
        "experience": "expert",
        "purpose": "Overseeing prophetic ministry across Canada"
    },
    {
        "name": "Prophetess Rachel Williams",
        "email": "rachel.williams@churchos.app",
        "role": "prophet",
        "country": "uk",
        "ministry": "British Prophetic Council",
        "teamSize": "21-50",
        "experience": "advanced",
        "purpose": "Prophetic oversight for UK churches"
    },
    {
        "name": "Apostle David Okafor",
        "email": "david.okafor@churchos.app",
        "role": "apostle",
        "country": "ng",
        "ministry": "Nigerian Apostolic Network",
        "teamSize": "100+",
        "experience": "expert",
        "purpose": "Leading apostolic movement across Nigeria"
    },
    {
        "name": "Prophet Daniel Schmidt",
        "email": "daniel.schmidt@churchos.app",
        "role": "prophet",
        "country": "de",
        "ministry": "German Prophetic Ministry",
        "teamSize": "6-20",
        "experience": "advanced",
        "purpose": "Prophetic ministry in German-speaking regions"
    },
    {
        "name": "Apostle Marie Dubois",
        "email": "marie.dubois@churchos.app",
        "role": "apostle",
        "country": "fr",
        "ministry": "French Apostolic Alliance",
        "teamSize": "21-50",
        "experience": "expert",
        "purpose": "Apostolic oversight for French-speaking churches"
    },
    {
        "name": "Prophet Kwame Asante",
        "email": "kwame.asante@churchos.app",
        "role": "prophet",
        "country": "gh",
        "ministry": "Ghanaian Prophetic Council",
        "teamSize": "51-100",
        "experience": "advanced",
        "purpose": "Prophetic ministry across Ghana"
    },
    {
        "name": "Apostle Yosef Cohen",
        "email": "yosef.cohen@churchos.app",
        "role": "apostle",
        "country": "il",
        "ministry": "Israeli Apostolic Network",
        "teamSize": "21-50",
        "experience": "expert",
        "purpose": "Apostolic oversight in Israel and Middle East"
    },
    {
        "name": "Prophet Ahmed Al-Rashid",
        "email": "ahmed.alrashid@churchos.app",
        "role": "prophet",
        "country": "sa",
        "ministry": "Saudi Prophetic Ministry",
        "teamSize": "6-20",
        "experience": "advanced",
        "purpose": "Prophetic ministry in Saudi Arabia"
    },
    {
        "name": "Apostle Grace Thompson",
        "email": "grace.thompson@churchos.app",
        "role": "apostle",
        "country": "au",
        "ministry": "Australian Apostolic Alliance",
        "teamSize": "21-50",
        "experience": "expert",
        "purpose": "Leading apostolic network across Australia"
    },
    {
        "name": "Prophet Carlos Rodriguez",
        "email": "carlos.rodriguez@churchos.app",
        "role": "prophet",
        "country": "us",
        "ministry": "Hispanic Prophetic Network",
        "teamSize": "51-100",
        "experience": "advanced",
        "purpose": "Prophetic ministry in Hispanic communities"
    },
    {
        "name": "Apostle Elizabeth Kim",
        "email": "elizabeth.kim@churchos.app",
        "role": "apostle",
        "country": "us",
        "ministry": "Asian Apostolic Network",
        "teamSize": "21-50",
        "experience": "expert",
        "purpose": "Apostolic oversight for Asian churches"
    }
]

def send_scroll_invite_email(email: str, name: str, role: str, access_link: str):
    """Send ScrollInvite email with sacred onboarding instructions"""
    
    # Email template based on role
    if role in ["apostle", "prophet"]:
        template = "apostolic_leader"
    elif role == "intercessor":
        template = "intercessor"
    else:
        template = "general"
    
    # Sacred email content
    subject = "🕊️ Sacred Invitation: Join CHURCHOS™ for Prophetic Church Governance"
    
    body = f"""
Dear {name},

"For the word of God is living and active, sharper than any two-edged sword." - Hebrews 4:12

We are honored to extend a sacred invitation for your ministry to experience CHURCHOS™ - the scroll-certified operating system for prophetic church governance.

**Your Sacred Access:**
- Role: {role.title()}
- Access Link: {access_link}
- Training Guide: https://docs.churchos.app/scrollguide

**Next Steps:**
1. Click the access link above to create your sacred account
2. Complete your profile and ministry information
3. Review the training guide for your role
4. Begin your prophetic journey with CHURCHOS™

**Sacred Features Available:**
- 📊 ScrollDashboard: Live prophetic cycle tracking
- 🙏 Prayer Portal: WebRTC livestreaming for intercessory prayer
- 🤖 AI Bible Characters: GPT-4 conversations with biblical figures
- 🌍 HolyLand VR: Immersive virtual Bible travel
- 📝 ScrollComposer: Sacred content creation tools
- 📱 Mobile Control: On-the-go prophecy and ministry management

**Sacred Commitment:**
By implementing CHURCHOS™, your ministry commits to:
- Prophetic excellence through technology
- Prayer as the foundation of all activities
- Community building and relationship strengthening
- Continuous growth and spiritual development
- Global impact in the prophetic community

**Support & Resources:**
- Email: team@churchos.app
- Documentation: https://docs.churchos.app
- Community: https://community.churchos.app
- Prayer Support: prayer@churchos.app

"The Lord is my shepherd, I shall not want. He makes me lie down in green pastures, he leads me beside quiet waters, he refreshes my soul." - Psalm 23:1-3

Govern the Church with CHURCHOS. The future is scroll.

Blessings,
The CHURCHOS™ Team
    """
    
    # Send email (implement with your email service)
    try:
        # Configure your email service here
        # For now, we'll just log the email
        print(f"Sending ScrollInvite email to {email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        
        # TODO: Implement actual email sending
        # send_email(email, subject, body)
        
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")

@router.post("/request", response_model=ScrollLicenseRequestResponse)
async def request_scroll_license(
    request: ScrollLicenseRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a ScrollLicense request for sacred access"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create ScrollLicense request
    db_request = ScrollLicenseRequest(
        name=request.name,
        email=request.email,
        role=request.role,
        purpose=request.purpose,
        country=request.country,
        ministry=request.ministry,
        team_size=request.teamSize,
        experience=request.experience,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Generate access link
    access_token = str(uuid.uuid4())
    access_link = f"https://churchos.app/activate/{access_token}"
    
    # Send ScrollInvite email in background
    background_tasks.add_task(
        send_scroll_invite_email,
        request.email,
        request.name,
        request.role,
        access_link
    )
    
    return ScrollLicenseRequestResponse(
        id=db_request.id,
        name=db_request.name,
        email=db_request.email,
        role=db_request.role,
        status=db_request.status,
        created_at=db_request.created_at,
        message="Sacred request submitted successfully. Check your email for access instructions."
    )

@router.get("/requests", response_model=List[ScrollLicenseRequestResponse])
async def get_scroll_license_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all ScrollLicense requests (EXOUSIA role required)"""
    
    if current_user.role not in ["apostle", "nation_seer"]:
        raise HTTPException(status_code=403, detail="Insufficient EXOUSIA level")
    
    requests = db.query(ScrollLicenseRequest).order_by(ScrollLicenseRequest.created_at.desc()).all()
    return requests

@router.post("/activate/{token}")
async def activate_scroll_license(
    token: str,
    db: Session = Depends(get_db)
):
    """Activate ScrollLicense with access token"""
    
    # Find request by token (implement token storage)
    # For now, we'll create a user directly
    
    # Create user account
    user = User(
        email="user@example.com",  # Get from token
        name="User Name",  # Get from token
        role="deacon",  # Default role
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    
    return {"message": "ScrollLicense activated successfully"}

@router.post("/seed-apostolic-accounts")
async def seed_apostolic_accounts(
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Seed pre-filled apostolic accounts for launch (Admin only)"""
    
    if current_user.role != "nation_seer":
        raise HTTPException(status_code=403, detail="Nation Seer access required")
    
    created_requests = []
    
    for account in APOSTOLIC_ACCOUNTS:
        # Check if account already exists
        existing = db.query(ScrollLicenseRequest).filter(
            ScrollLicenseRequest.email == account["email"]
        ).first()
        
        if not existing:
            # Create ScrollLicense request
            db_request = ScrollLicenseRequest(
                name=account["name"],
                email=account["email"],
                role=account["role"],
                purpose=account["purpose"],
                country=account["country"],
                ministry=account["ministry"],
                team_size=account["teamSize"],
                experience=account["experience"],
                status="approved",
                created_at=datetime.utcnow()
            )
            
            db.add(db_request)
            created_requests.append(db_request)
    
    db.commit()
    
    # Send ScrollInvite emails in background
    for request in created_requests:
        access_token = str(uuid.uuid4())
        access_link = f"https://churchos.app/activate/{access_token}"
        
        background_tasks.add_task(
            send_scroll_invite_email,
            request.email,
            request.name,
            request.role,
            access_link
        )
    
    return {
        "message": f"Seeded {len(created_requests)} apostolic accounts",
        "accounts_created": len(created_requests),
        "total_apostolic_accounts": len(APOSTOLIC_ACCOUNTS)
    }

@router.get("/stats")
async def get_scroll_license_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ScrollLicense statistics (EXOUSIA role required)"""
    
    if current_user.role not in ["apostle", "nation_seer"]:
        raise HTTPException(status_code=403, detail="Insufficient EXOUSIA level")
    
    total_requests = db.query(ScrollLicenseRequest).count()
    pending_requests = db.query(ScrollLicenseRequest).filter(
        ScrollLicenseRequest.status == "pending"
    ).count()
    approved_requests = db.query(ScrollLicenseRequest).filter(
        ScrollLicenseRequest.status == "approved"
    ).count()
    
    # Role distribution
    role_stats = db.query(
        ScrollLicenseRequest.role,
        db.func.count(ScrollLicenseRequest.id)
    ).group_by(ScrollLicenseRequest.role).all()
    
    # Country distribution
    country_stats = db.query(
        ScrollLicenseRequest.country,
        db.func.count(ScrollLicenseRequest.id)
    ).group_by(ScrollLicenseRequest.country).all()
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "role_distribution": dict(role_stats),
        "country_distribution": dict(country_stats),
        "apostolic_accounts": len(APOSTOLIC_ACCOUNTS)
    } 