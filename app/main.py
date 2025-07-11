from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
try:
    firebase_admin.get_app()
except ValueError:
    # Initialize Firebase Admin SDK with service account
    if os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"):
        cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"))
        firebase_admin.initialize_app(cred)
    else:
        # Initialize with default credentials (for development)
        firebase_admin.initialize_app()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🕊️ CHURCHOS™ Backend starting up...")
    yield
    # Shutdown
    print("🕊️ CHURCHOS™ Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="CHURCHOS™ API",
    description="Sacred Operating System for Prophetic Church Governance",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://churchos.app",
        "https://www.churchos.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.routers import (
    auth,
    users,
    prophecies,
    scroll_cycles,
    prayer_portal,
    bible_character_room,
    holy_land_scene,
    scroll_composer,
    scroll_seal,
    mobile_control,
    go_live_with_heaven,
    scroll_license,
    analytics
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(prophecies.router, prefix="/api/prophecies", tags=["Prophecies"])
app.include_router(scroll_cycles.router, prefix="/api/scroll-cycles", tags=["Scroll Cycles"])
app.include_router(prayer_portal.router, prefix="/api/prayer-portal", tags=["Prayer Portal"])
app.include_router(bible_character_room.router, prefix="/api/bible-character-room", tags=["Bible Character Room"])
app.include_router(holy_land_scene.router, prefix="/api/holy-land-scene", tags=["Holy Land Scene"])
app.include_router(scroll_composer.router, prefix="/api/scroll-composer", tags=["Scroll Composer"])
app.include_router(scroll_seal.router, prefix="/api/scroll-seal", tags=["Scroll Seal"])
app.include_router(mobile_control.router, prefix="/api/mobile-control", tags=["Mobile Control"])
app.include_router(go_live_with_heaven.router, prefix="/api/go-live-with-heaven", tags=["Go Live With Heaven"])
app.include_router(scroll_license.router, prefix="/api/scroll-license", tags=["Scroll License"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "🕊️ CHURCHOS™ API - Sacred Operating System for Prophetic Church Governance",
        "version": "1.0.0",
        "status": "active",
        "modules": [
            "ScrollDashboard",
            "ScrollPrayerPortal", 
            "BibleCharacterRoom",
            "HolyLandScene",
            "ScrollComposer",
            "ScrollSeal",
            "MobileControlApp",
            "GoLiveWithHeaven"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": "CHURCHOS™ API"
    }

# API documentation endpoint
@app.get("/api")
async def api_info():
    return {
        "title": "CHURCHOS™ API",
        "description": "Sacred Operating System for Prophetic Church Governance",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "message": "Sacred error occurred"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "message": "Sacred system error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 