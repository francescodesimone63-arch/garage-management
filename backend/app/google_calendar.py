"""
Google Calendar integration module

Handles OAuth2 flow (authorization code flow) and calendar operations.
Manages refresh tokens in DB for long-lived API access without user re-auth.
"""
import os
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.google_oauth import GoogleOAuthToken, GoogleOAuthState


# Environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/google/oauth/callback")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
GOOGLE_OAUTH_STATE_SECRET = os.getenv("GOOGLE_OAUTH_STATE_SECRET", "dev-secret-key")

# Google OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def generate_oauth_state(expiry_minutes: int = 120) -> str:
    """
    Generate a random OAuth state token.
    
    Args:
        expiry_minutes: Token expiry time in minutes (default 2 hours)
        
    Returns:
        Random state token (safe URL-friendly string)
    """
    return secrets.token_urlsafe(32)


async def save_oauth_state(db: AsyncSession, state: str, return_url: str = None, expiry_minutes: int = 120) -> bool:
    """
    Save OAuth state token to database.
    
    Args:
        db: AsyncSession
        state: State token to save
        return_url: URL to return user to after OAuth (optional)
        expiry_minutes: When the token expires (from now)
        
    Returns:
        True if saved successfully
    """
    try:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        
        oauth_state = GoogleOAuthState(
            state=state,
            return_url=return_url,
            expires_at=expires_at
        )
        db.add(oauth_state)
        await db.commit()
        return True
    except Exception as e:
        print(f"Error saving OAuth state: {e}")
        await db.rollback()
        return False


async def verify_oauth_state(db: AsyncSession, state: str) -> tuple[bool, str | None]:
    """
    Verify OAuth state token from database.
    
    Returns both validation result AND the return_url to redirect to.
    
    Args:
        db: AsyncSession
        state: State token to verify
        
    Returns:
        Tuple of (is_valid: bool, return_url: str or None)
    """
    try:
        # Query for the state
        result = await db.execute(
            select(GoogleOAuthState).filter(
                GoogleOAuthState.state == state,
                GoogleOAuthState.expires_at > datetime.now(timezone.utc)
            )
        )
        token_record = result.scalars().first()
        
        if token_record:
            return_url = token_record.return_url
            # Delete the state (one-time use)
            await db.delete(token_record)
            await db.commit()
            return (True, return_url)
        
        return (False, None)
    except Exception as e:
        print(f"Error verifying OAuth state: {e}")
        return (False, None)


def create_oauth_flow(scopes: list[str] = None) -> Flow:
    """
    Create OAuth2 Flow for authorization code flow.
    
    Args:
        scopes: OAuth scopes (defaults to calendar.write)
        
    Returns:
        google_auth_oauthlib.flow.Flow instance
    """
    if scopes is None:
        scopes = SCOPES
    
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=scopes,
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow


def exchange_code_for_token(code: str) -> Optional[dict]:
    """
    Exchange authorization code for tokens.
    
    NOTE: State validation must be done by the caller (via verify_oauth_state)!
    
    Args:
        code: Authorization code from Google
        
    Returns:
        Token response dict with refresh_token, access_token, etc., or None if failed
    """
    flow = create_oauth_flow()
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        return {
            "refresh_token": credentials.refresh_token,
            "access_token": credentials.token,
            "expires_in": credentials.expiry,
        }
    except Exception as e:
        print(f"Token exchange error: {e}")
        return None


async def get_calendar_service(db: AsyncSession):
    """
    Build Google Calendar service with auto-refresh credentials (ASYNC version).
    
    Reads refresh_token from DB, creates Credentials object with automatic
    refresh on expired access_token.
    
    Args:
        db: SQLAlchemy AsyncSession
        
    Returns:
        googleapiclient.discovery.Resource for calendar v3
        
    Raises:
        ValueError if no stored token found or credentials not configured
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    
    # Validate credentials are configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables must be set")
    
    result = await db.execute(select(GoogleOAuthToken).filter(GoogleOAuthToken.id == 1))
    token_record = result.scalars().first()
    
    if not token_record or not token_record.refresh_token:
        raise ValueError("No Google OAuth token found. Run OAuth flow first.")
    
    # Create credentials from stored refresh token
    creds = Credentials(
        token=token_record.access_token,
        refresh_token=token_record.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    
    # Refresh if expired - this part is synchronous blocking I/O (Google API call)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Update cached access token in DB - use the already-fetched object
        token_record.access_token = creds.token
        token_record.access_token_expiry = creds.expiry
        # SQLAlchemy tracks ORM objects, no need for db.add()
        await db.commit()
    
    service = build("calendar", "v3", credentials=creds)
    return service


def get_calendar_service_sync(db: Session):
    """
    Build Google Calendar service with auto-refresh credentials (SYNC version).
    
    Reads refresh_token from DB, creates Credentials object with automatic
    refresh on expired access_token. Use this for synchronous endpoints.
    
    Args:
        db: SQLAlchemy Session (sync)
        
    Returns:
        googleapiclient.discovery.Resource for calendar v3
        
    Raises:
        ValueError if no stored token found or credentials not configured
    """
    from sqlalchemy import select
    
    # Validate credentials are configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables must be set")
    
    result = db.execute(select(GoogleOAuthToken).filter(GoogleOAuthToken.id == 1))
    token_record = result.scalars().first()
    
    if not token_record or not token_record.refresh_token:
        raise ValueError("No Google OAuth token found. Run OAuth flow first.")
    
    # Create credentials from stored refresh token
    creds = Credentials(
        token=token_record.access_token,
        refresh_token=token_record.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Update cached access token in DB
            token_record.access_token = creds.token
            token_record.access_token_expiry = creds.expiry
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to refresh token: {str(e)}")
    
    service = build("calendar", "v3", credentials=creds)
    return service


async def save_oauth_token(db: AsyncSession, refresh_token: str, access_token: str, expires_in: datetime):
    """
    Save/update OAuth tokens in database.
    
    Args:
        db: SQLAlchemy AsyncSession
        refresh_token: Long-lived refresh token
        access_token: Short-lived access token
        expires_in: Expiry datetime for access token
    """
    result = await db.execute(select(GoogleOAuthToken).filter(GoogleOAuthToken.id == 1))
    token_record = result.scalars().first()
    
    if not token_record:
        token_record = GoogleOAuthToken(
            id=1,
            refresh_token=refresh_token,
            access_token=access_token,
            access_token_expiry=expires_in,
            calendar_id=GOOGLE_CALENDAR_ID,
        )
        db.add(token_record)
    else:
        token_record.refresh_token = refresh_token
        token_record.access_token = access_token
        token_record.access_token_expiry = expires_in
    
    await db.commit()


def create_calendar_event(
    service,
    summary: str,
    description: str,
    start_datetime: datetime,
    end_datetime: datetime,
    location: str = None,
    calendar_id: str = "primary",
) -> Optional[dict]:
    """
    Create event in Google Calendar.
    
    Args:
        service: Google Calendar service resource
        summary: Event title
        description: Event description
        start_datetime: Event start (datetime with timezone)
        end_datetime: Event end (datetime with timezone)
        location: Event location
        calendar_id: Calendar ID (default "primary")
        
    Returns:
        Created event dict with id, htmlLink, start, end; or None on error
    """
    event_body = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Europe/Rome",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Europe/Rome",
        },
    }
    
    if location:
        event_body["location"] = location
    
    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        return event
    except HttpError as error:
        print(f"Google Calendar API error: {error}")
        return None


def update_calendar_event(
    service,
    event_id: str,
    summary: str = None,
    description: str = None,
    location: str = None,
    start_datetime: datetime = None,
    end_datetime: datetime = None,
    send_updates: str = "none",
    calendar_id: str = "primary",
) -> Optional[dict]:
    """
    Update existing event in Google Calendar (patch semantics - only provided fields).
    
    Args:
        service: Google Calendar service resource
        event_id: Event ID to update
        summary: New summary (optional)
        description: New description (optional)
        location: New location (optional)
        start_datetime: New start time (optional)
        end_datetime: New end time (optional)
        send_updates: "all" to notify attendees, "externalOnly" for non-Google, "none" (default)
        calendar_id: Calendar ID
        
    Returns:
        Updated event dict, or None on error
    """
    event_patch = {}
    
    if summary is not None:
        event_patch["summary"] = summary
    if description is not None:
        event_patch["description"] = description
    if location is not None:
        event_patch["location"] = location
    
    if start_datetime is not None:
        event_patch["start"] = {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Europe/Rome",
        }
    
    if end_datetime is not None:
        event_patch["end"] = {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Europe/Rome",
        }
    
    try:
        event = service.events().patch(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_patch,
            sendUpdates=send_updates,
        ).execute()
        return event
    except HttpError as error:
        print(f"Google Calendar API error: {error}")
        return None


def delete_calendar_event(
    service,
    event_id: str,
    send_updates: str = "none",
    calendar_id: str = "primary",
) -> bool:
    """
    Delete event from Google Calendar.
    
    Args:
        service: Google Calendar service resource
        event_id: Event ID to delete
        send_updates: "all", "externalOnly", or "none"
        calendar_id: Calendar ID
        
    Returns:
        True if deleted successfully, False on error
    """
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates=send_updates,
        ).execute()
        return True
    except HttpError as error:
        if error.resp.status == 404:
            # Event already deleted
            return True
        print(f"Google Calendar API error: {error}")
        return False
