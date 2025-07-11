from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVATED = "activated"

class ScrollLicenseRequestCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    purpose: str
    country: str
    ministry: str
    teamSize: str
    experience: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Prophet Sarah Johnson",
                "email": "sarah.johnson@churchos.app",
                "role": "prophet",
                "purpose": "Leading prophetic ministry and intercessory prayer",
                "country": "us",
                "ministry": "Global Prophetic Network",
                "teamSize": "21-50",
                "experience": "expert"
            }
        }

class ScrollLicenseRequestResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: RequestStatus
    created_at: datetime
    message: str

    class Config:
        from_attributes = True

class ScrollLicenseStats(BaseModel):
    total_requests: int
    pending_requests: int
    approved_requests: int
    role_distribution: dict
    country_distribution: dict
    apostolic_accounts: int

class ScrollLicenseActivation(BaseModel):
    token: str
    email: str
    name: str
    role: str 