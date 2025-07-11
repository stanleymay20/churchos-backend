import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Sacred configuration settings for CHURCHOS™"""
    
    # =============================================================================
    # FIREBASE CONFIGURATION
    # =============================================================================
    firebase_project_id: str = Field(..., env="FIREBASE_PROJECT_ID")
    firebase_private_key_id: str = Field(..., env="FIREBASE_PRIVATE_KEY_ID")
    firebase_private_key: str = Field(..., env="FIREBASE_PRIVATE_KEY")
    firebase_client_email: str = Field(..., env="FIREBASE_CLIENT_EMAIL")
    firebase_client_id: str = Field(..., env="FIREBASE_CLIENT_ID")
    firebase_auth_uri: str = Field(default="https://accounts.google.com/o/oauth2/auth", env="FIREBASE_AUTH_URI")
    firebase_token_uri: str = Field(default="https://oauth2.googleapis.com/token", env="FIREBASE_TOKEN_URI")
    firebase_auth_provider_x509_cert_url: str = Field(default="https://www.googleapis.com/oauth2/v1/certs", env="FIREBASE_AUTH_PROVIDER_X509_CERT_URL")
    firebase_client_x509_cert_url: str = Field(..., env="FIREBASE_CLIENT_X509_CERT_URL")
    
    # =============================================================================
    # OPENAI CONFIGURATION
    # =============================================================================
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: Optional[str] = Field(None, env="DATABASE_TEST_URL")
    
    # =============================================================================
    # JWT CONFIGURATION
    # =============================================================================
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_seconds: int = Field(default=86400, env="JWT_EXPIRATION_SECONDS")
    
    # =============================================================================
    # STRIPE CONFIGURATION
    # =============================================================================
    stripe_secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    
    # =============================================================================
    # SERVER CONFIGURATION
    # =============================================================================
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # =============================================================================
    # CORS CONFIGURATION
    # =============================================================================
    allowed_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "https://churchos.app",
            "https://www.churchos.app"
        ],
        env="ALLOWED_ORIGINS"
    )
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/churchos.log", env="LOG_FILE")
    
    # =============================================================================
    # REDIS CONFIGURATION
    # =============================================================================
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    smtp_host: Optional[str] = Field(None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    
    # =============================================================================
    # FILE STORAGE CONFIGURATION
    # =============================================================================
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(None, env="AWS_S3_BUCKET")
    
    # =============================================================================
    # ANALYTICS CONFIGURATION
    # =============================================================================
    google_analytics_id: Optional[str] = Field(None, env="GOOGLE_ANALYTICS_ID")
    mixpanel_token: Optional[str] = Field(None, env="MIXPANEL_TOKEN")
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "churchos.app", "www.churchos.app"],
        env="ALLOWED_HOSTS"
    )
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    enable_ai_characters: bool = Field(default=True, env="ENABLE_AI_CHARACTERS")
    enable_livestreaming: bool = Field(default=True, env="ENABLE_LIVESTREAMING")
    enable_xr_holyland: bool = Field(default=True, env="ENABLE_XR_HOLYLAND")
    enable_mobile_control: bool = Field(default=True, env="ENABLE_MOBILE_CONTROL")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_billing: bool = Field(default=True, env="ENABLE_BILLING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings

def get_firebase_config() -> dict:
    """Get Firebase configuration as a dictionary"""
    return {
        "type": "service_account",
        "project_id": settings.firebase_project_id,
        "private_key_id": settings.firebase_private_key_id,
        "private_key": settings.firebase_private_key.replace("\\n", "\n"),
        "client_email": settings.firebase_client_email,
        "client_id": settings.firebase_client_id,
        "auth_uri": settings.firebase_auth_uri,
        "token_uri": settings.firebase_token_uri,
        "auth_provider_x509_cert_url": settings.firebase_auth_provider_x509_cert_url,
        "client_x509_cert_url": settings.firebase_client_x509_cert_url
    }

def get_database_url() -> str:
    """Get the appropriate database URL based on environment"""
    if settings.environment == "test":
        return settings.database_test_url or settings.database_url
    return settings.database_url

def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() == "development"

def get_cors_origins() -> List[str]:
    """Get CORS origins as a list"""
    if isinstance(settings.allowed_origins, str):
        return [origin.strip() for origin in settings.allowed_origins.split(",")]
    return settings.allowed_origins

def get_allowed_hosts() -> List[str]:
    """Get allowed hosts as a list"""
    if isinstance(settings.allowed_hosts, str):
        return [host.strip() for host in settings.allowed_hosts.split(",")]
    return settings.allowed_hosts 