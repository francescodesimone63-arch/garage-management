"""
Google OAuth token storage model for calendar integration
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class GoogleOAuthToken(Base):
    """
    Stores Google OAuth tokens for calendar integration.
    Only one record (id=1) is used since this is a single garage account.
    """
    __tablename__ = "google_oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True, default=1)
    refresh_token = Column(Text, nullable=False)
    access_token = Column(Text, nullable=True)  # cached, may be expired
    access_token_expiry = Column(DateTime(timezone=True), nullable=True)
    calendar_id = Column(String(255), nullable=False, default="primary")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<GoogleOAuthToken(calendar_id='{self.calendar_id}', updated_at='{self.updated_at}')>"


class GoogleOAuthState(Base):
    """
    Temporary storage for OAuth state parameters during authorization flow.
    State tokens are validated on callback and then deleted.
    TTL: 2 hours (long enough for users to complete Google login)
    
    Includes return_url to redirect user to correct page after OAuth completes.
    """
    __tablename__ = "google_oauth_states"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    return_url = Column(String(1024), nullable=True)  # URL to return user to after OAuth
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<GoogleOAuthState(state='{self.state[:20]}...', return_url='{self.return_url}', expires_at='{self.expires_at}')>"
