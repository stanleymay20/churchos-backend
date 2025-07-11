from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class RoleEnum(enum.Enum):
    DEACON = "Deacon"
    ELDER = "Elder"
    APOSTLE = "Apostle"
    NATION_SEER = "Nation Seer"

class UrgencyEnum(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StatusEnum(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

class CycleStatusEnum(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.DEACON)
    firebase_uid = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prophecies = relationship("Prophecy", back_populates="user")
    scroll_cycles = relationship("ScrollCycle", back_populates="creator")

class Prophecy(Base):
    __tablename__ = "prophecies"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    urgency = Column(Enum(UrgencyEnum), default=UrgencyEnum.MEDIUM)
    assigned_to = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.PENDING)
    user_id = Column(Integer, ForeignKey("users.id"))
    scroll_cycle_id = Column(Integer, ForeignKey("scroll_cycles.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="prophecies")
    scroll_cycle = relationship("ScrollCycle", back_populates="prophecies")

class ScrollCycle(Base):
    __tablename__ = "scroll_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    participants = Column(Integer, default=0)
    prophecies_count = Column(Integer, default=0)
    status = Column(Enum(CycleStatusEnum), default=CycleStatusEnum.SCHEDULED)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="scroll_cycles")
    prophecies = relationship("Prophecy", back_populates="scroll_cycle")

class PrayerSession(Base):
    __tablename__ = "prayer_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    is_live = Column(Boolean, default=False)
    stream_url = Column(String)
    participants_count = Column(Integer, default=0)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class BibleCharacter(Base):
    __tablename__ = "bible_characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    avatar_url = Column(String)
    personality_prompt = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HolyLandScene(Base):
    __tablename__ = "holy_land_scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    scene_data = Column(Text)  # JSON data for 3D scene
    triggers = Column(Text)  # JSON data for scroll triggers
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScrollComposition(Base):
    __tablename__ = "scroll_compositions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)  # JSON data for slide content
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LivestreamSession(Base):
    __tablename__ = "livestream_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    topic = Column(String)
    stream_url = Column(String)
    is_live = Column(Boolean, default=False)
    viewer_count = Column(Integer, default=0)
    creator_id = Column(Integer, ForeignKey("users.id"))
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow) 