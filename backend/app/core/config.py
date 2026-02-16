"""
Configuration settings for the Garage Management System
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application Settings
    app_name: str = Field(default="Garage Management System")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="your-secret-key-here-change-in-production")
    api_v1_str: str = Field(default="/api/v1")
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./garage.db")
    
    # JWT Settings
    jwt_secret_key: str = Field(default="your-jwt-secret-key-here-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=480)  # 8 hours
    jwt_refresh_token_expire_days: int = Field(default=30)
    
    # CORS Settings
    cors_origins: str = Field(default="http://localhost:3000")
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Google APIs
    google_client_id: Optional[str] = Field(default=None)
    google_client_secret: Optional[str] = Field(default=None)
    google_redirect_uri: str = Field(default="http://localhost:8000/api/v1/google/oauth/callback")
    google_calendar_id: str = Field(default="primary")
    google_oauth_state_secret: str = Field(default="dev-secret-key-change-in-production")
    
    # SendGrid (Email)
    sendgrid_api_key: Optional[str] = Field(default=None)
    sendgrid_from_email: str = Field(default="noreply@garage.com")
    
    # Twilio (SMS)
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_from_number: Optional[str] = Field(default=None)
    
    # WhatsApp Business API
    whatsapp_api_url: str = Field(default="https://api.whatsapp.com/v1/")
    whatsapp_api_token: Optional[str] = Field(default=None)
    
    # OpenAI (for AI search)
    openai_api_key: Optional[str] = Field(default=None)
    
    # Perplexity API (alternative AI search)
    perplexity_api_key: Optional[str] = Field(default=None)
    perplexity_api_url: str = Field(default="https://api.perplexity.ai")
    
    # Scheduler Settings
    scheduler_timezone: str = Field(default="Europe/Rome")
    scheduler_job_defaults_coalesce: bool = Field(default=True)
    scheduler_job_defaults_max_instances: int = Field(default=3)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/app.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()