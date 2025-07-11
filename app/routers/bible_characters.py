from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
import logging
from datetime import datetime

from ..database import get_db
from ..models import BibleCharacter, User
from ..auth import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client with async support
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    character: str
    message: str

class ChatResponse(BaseModel):
    character: str
    user_message: str
    character_response: str
    timestamp: str

# Sacred Bible Character Profiles for CHURCHOS™
CHARACTER_PROFILES = {
    "Jesus": {
        "personality": "Compassionate, wise, and loving teacher who speaks with authority and grace. He uses parables and metaphors to convey deep spiritual truths.",
        "speaking_style": "Gentle yet authoritative, often using 'I tell you' and 'Truly, truly' to emphasize important points.",
        "knowledge_base": "All scripture, especially the Gospels, teachings about the Kingdom of God, salvation, and discipleship.",
        "sacred_purpose": "To guide believers in the way of love, truth, and discipleship."
    },
    "Paul": {
        "personality": "Passionate, bold, and deeply theological. He speaks with conviction about grace, faith, and the church.",
        "speaking_style": "Direct and theological, often using phrases like 'I want you to know' and 'By no means!'",
        "knowledge_base": "Epistles, theology, church planting, grace, and the mystery of Christ.",
        "sacred_purpose": "To build up the body of Christ through sound doctrine and spiritual wisdom."
    },
    "Esther": {
        "personality": "Courageous, wise, and strategic. She speaks with royal dignity and faith in God's providence.",
        "speaking_style": "Elegant and measured, often using 'If I perish, I perish' type of courageous statements.",
        "knowledge_base": "The Book of Esther, Jewish history, royal court dynamics, and God's hidden providence.",
        "sacred_purpose": "To inspire courage and trust in God's providential care."
    },
    "Moses": {
        "personality": "Humble yet powerful leader who speaks with divine authority. He's experienced in both Egyptian wisdom and divine revelation.",
        "speaking_style": "Authoritative and prophetic, often using 'Thus says the Lord' and speaking of God's mighty acts.",
        "knowledge_base": "Pentateuch, Exodus, Law, wilderness journey, and God's covenant with Israel.",
        "sacred_purpose": "To lead God's people in obedience and faith through divine guidance."
    },
    "David": {
        "personality": "Passionate, poetic, and deeply emotional. He speaks with raw honesty about his relationship with God.",
        "speaking_style": "Poetic and heartfelt, often using psalms and songs to express his soul's deepest longings.",
        "knowledge_base": "Psalms, Davidic covenant, kingship, worship, and God's faithfulness.",
        "sacred_purpose": "To teach authentic worship and trust in God through all of life's seasons."
    },
    "Ruth": {
        "personality": "Loyal, faithful, and determined. She speaks with quiet strength and unwavering commitment.",
        "speaking_style": "Gentle and steadfast, often using words of loyalty and commitment like 'Where you go, I will go.'",
        "knowledge_base": "The Book of Ruth, loyalty, God's providence, and the lineage of Christ.",
        "sacred_purpose": "To demonstrate faithfulness and God's providential care in difficult circumstances."
    }
}

@router.get("/ai-character/{name}")
async def get_character_info(
    name: str,
    current_user: User = Depends(get_current_user)
):
    """Get sacred information about a Bible character"""
    try:
        character_name = name.title()
        if character_name not in CHARACTER_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character '{name}' not found in our sacred library"
            )
        
        profile = CHARACTER_PROFILES[character_name]
        
        logger.info(f"User {current_user.name} accessed character info for {character_name}")
        
        return {
            "name": character_name,
            "personality": profile["personality"],
            "speaking_style": profile["speaking_style"],
            "knowledge_base": profile["knowledge_base"],
            "sacred_purpose": profile["sacred_purpose"],
            "avatar_url": f"/api/v1/characters/{character_name.lower()}/avatar"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching character info for {name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred while accessing character information"
        )

@router.post("/ai-character/chat", response_model=ChatResponse)
async def chat_with_character(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat with an AI-powered Bible character using OpenAI GPT-4"""
    try:
        character_name = chat_request.character.title()
        user_message = chat_request.message.strip()
        
        # Validate character exists
        if character_name not in CHARACTER_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character '{character_name}' not found in our sacred library"
            )
        
        # Validate message
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        profile = CHARACTER_PROFILES[character_name]
        
        # Create the sacred system prompt for the character
        system_prompt = f"""You are {character_name}, a biblical figure from the sacred scriptures. 

Personality: {profile['personality']}
Speaking Style: {profile['speaking_style']}
Knowledge Base: {profile['knowledge_base']}
Sacred Purpose: {profile['sacred_purpose']}

Respond as {character_name} would, staying true to their biblical character, personality, and speaking style. Use their typical phrases and mannerisms. Keep responses concise but meaningful, as if having a personal conversation with a modern believer.

Remember: You are {character_name} speaking to a modern believer seeking spiritual guidance. Share wisdom, encouragement, or guidance as {character_name} would, drawing from their biblical experiences and knowledge. Keep responses under 200 words and maintain the sacred, respectful tone appropriate for spiritual counsel."""

        # Call OpenAI API with async handling
        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            character_response = response.choices[0].message.content or ""
            character_response = character_response.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Sacred AI service encountered an error"
            )
        
        # Log the interaction for sacred purposes
        logger.info(f"User {current_user.name} chatted with {character_name}")
        
        return ChatResponse(
            character=character_name,
            user_message=user_message,
            character_response=character_response,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in character chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred during character interaction"
        )

@router.get("/characters")
async def get_available_characters(
    current_user: User = Depends(get_current_user)
):
    """Get list of available sacred Bible characters"""
    try:
        characters = []
        for name, profile in CHARACTER_PROFILES.items():
            characters.append({
                "name": name,
                "personality": profile["personality"][:100] + "...",
                "sacred_purpose": profile["sacred_purpose"][:100] + "...",
                "avatar_url": f"/api/v1/characters/{name.lower()}/avatar"
            })
        
        logger.info(f"User {current_user.name} accessed available characters")
        
        return {"characters": characters}
        
    except Exception as e:
        logger.error(f"Error fetching characters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sacred error occurred while accessing character library"
        ) 