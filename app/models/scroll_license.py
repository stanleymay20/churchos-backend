from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from ..database import Base
import enum

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVATED = "activated"

class ScrollLicenseRequest(Base):
    __tablename__ = "scroll_license_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False)
    purpose = Column(Text, nullable=False)
    country = Column(String(10), nullable=False)
    ministry = Column(String(255), nullable=False)
    team_size = Column(String(20), nullable=False)
    experience = Column(String(20), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    access_token = Column(String(255), unique=True, nullable=True)
    activated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ScrollLicenseRequest(id={self.id}, email={self.email}, role={self.role}, status={self.status})>" 