# Google Calendar Integration - Setup Guide

## Overview

This implementation provides complete Google Calendar integration for work order management. The system automatically stores appointment details in a shared Google Calendar.

**Key Features:**
- OAuth2 authorization code flow (one-time setup per garage)
- Automatic token refresh for long-lived API access
- Create, update, and delete calendar events via REST API
- Support for custom summaries, descriptions, and locations
- Full error handling and validation

## Setup Instructions

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Garage Calendar"
3. Enable Calendar API:
   - Search "Google Calendar API"
   - Click "ENABLE"

### 2. Create OAuth Credentials

1. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
2. Select "Web application"
3. Add AuthorizedRedirectURIs:
   ```
   http://localhost:8000/api/v1/google/oauth/callback
   https://yourdomain.com/api/v1/google/oauth/callback (for production)
   ```
4. Download JSON and copy:
   - `client_id`
   - `client_secret`

### 3. Configure Environment Variables

Add to `.env`:

```dotenv
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google/oauth/callback
GOOGLE_CALENDAR_ID=primary
GOOGLE_OAUTH_STATE_SECRET=your-secret-256-bit-key-here
```

> **Note:** `GOOGLE_OAUTH_STATE_SECRET` should be a long random string (256+ bits). Used for CSRF protection in OAuth state parameter.

### 4. Start OAuth Flow

1. Visit: http://localhost:8000/api/v1/google/oauth/start
2. You'll be redirected to Google's authorization screen
3. Authorize the application
4. Google redirects you back to the callback endpoint
5. Tokens are stored in database automatically

**Why `prompt=consent`?**
- Ensures the refresh token is always returned
- Forces user to re-authorize even if they already granted permission
- Critical for long-lived API access without re-authentication

![OAuth Flow Diagram](docs/oauth-flow.png)

## Database Schema

### google_oauth_tokens
```sql
CREATE TABLE google_oauth_tokens (
    id INTEGER PRIMARY KEY,
    refresh_token TEXT NOT NULL,       -- Long-lived token
    access_token TEXT,                 -- Short-lived, auto-refreshed
    access_token_expiry DATETIME,      -- When access_token expires
    calendar_id TEXT DEFAULT 'primary', -- Calendar ID (usually "primary")
    created_at DATETIME,
    updated_at DATETIME
);
```

### work_orders (updated)
```sql
ALTER TABLE work_orders ADD COLUMN google_event_id TEXT;
CREATE INDEX ix_work_orders_google_event_id ON work_orders(google_event_id);
```

## API Endpoints

### 1. Start OAuth Authorization
```
GET /api/v1/google/oauth/start
```

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "base64-encoded-signed-state"
}
```

### 2. OAuth Callback (automatic)
```
GET /api/v1/google/oauth/callback?code=...&state=...
```

Google redirects to this automatically. System validates state and exchanges code for tokens.

### 3. Create Calendar Event
```
POST /api/v1/lavori/{lavoro_id}/calendar
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "summary": "Riparazione motore",
  "description": "Analisi e riparazione motore - Cliente VIP",
  "location": "Officina Via Roma 123"
}
```

**Validation:**
- WorkOrder must have `data_appuntamento` and `data_fine_prevista` set
- `data_fine_prevista` must be after `data_appuntamento`

**Response:**
```json
{
  "google_event_id": "abc123def456",
  "html_link": "https://calendar.google.com/calendar/u/0/r/eventedit/abc123",
  "summary": "Riparazione motore",
  "start": {
    "dateTime": "2026-02-15T10:00:00+01:00",
    "timeZone": "Europe/Rome"
  },
  "end": {
    "dateTime": "2026-02-15T13:00:00+01:00",
    "timeZone": "Europe/Rome"
  }
}
```

### 4. Update Calendar Event
```
PATCH /api/v1/lavori/{lavoro_id}/calendar?send_updates=none
Authorization: Bearer JWT_TOKEN
Content-Type: application/json

{
  "summary": "Riparazione motore - URGENTE",
  "data_appuntamento": "2026-02-15T14:00:00+01:00",
  "data_fine_prevista": "2026-02-15T17:00:00+01:00"
}
```

**Semantics:**
- Only provided fields are updated
- `data_appuntamento` and `data_fine_prevista` are parsed as ISO 8601 with timezone
- Missing fields use current work order values

**Query Parameters:**
- `send_updates` (default: "none")
  - `"none"` - Don't notify attendees
  - `"all"` - Notify all attendees
  - `"externalOnly"` - Notify non-Google attendees only

### 5. Delete Calendar Event
```
DELETE /api/v1/lavori/{lavoro_id}/calendar
Authorization: Bearer JWT_TOKEN
```

**Result:**
- Event deleted from Google Calendar
- `google_event_id` cleared in database
- Work order remains intact

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success (GET, POST, PATCH) | Event created/updated |
| 204 | Success (DELETE) | Event deleted |
| 400 | Validation error | Missing dates, invalid format |
| 404 | Not found | Work order doesn't exist |
| 409 | Conflict | No event to update/delete |
| 500 | Server error | No OAuth token, API error |
| 502 | Bad gateway | Google Calendar API failure |

## Error Handling

### No OAuth Token
```json
{
  "detail": "No Google OAuth token found. Run OAuth flow first."
}
```
**Solution:** Complete the OAuth setup via `/api/v1/google/oauth/start`

### Invalid Dates
```json
{
  "detail": "data_fine_prevista must be after data_appuntamento"
}
```
**Solution:** Ensure end time is after start time

### Event Not Found
```json
{
  "detail": "Failed to delete calendar event"
}
```
**Note:** If event was deleted externally from Google Calendar, the system reflects this (404 → 200).

## Test Examples

See `test_google_calendar.sh` for curl examples.

### Quick Test Sequence

```bash
# 1. Get authorization URL
curl http://localhost:8000/api/v1/google/oauth/start

# 2. Open the authorization_url in browser, authorize

# 3. Create event
curl -X POST http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"summary": "Test"}'

# 4. Verify in Google Calendar
# https://calendar.google.com/
```

## Troubleshooting

### State Verification Failed
- State expired (10-minute window)
- Wrong GOOGLE_OAUTH_STATE_SECRET in .env
- Solution: Complete OAuth flow again

### Token Refresh Fails
- GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET incorrect
- Tokens were revoked by user in Google Account
- Solution: Complete OAuth flow to get new tokens

### Calendar API Error 403
- Google Calendar API not enabled in Cloud Project
- Service account lacks permissions
- Solution: Verify Calendar API is enabled in Cloud Console

### SSL Certificate Error (Production)
- Use valid HTTPS URL in GOOGLE_REDIRECT_URI
- Configure SSL in reverse proxy
- Solution: Add domain to OAuth credentials in Cloud Console

## Security Notes

1. **State Parameter Validation**
   - State includes expiry (10 minutes)
   - HMAC-SHA256 signature prevents tampering
   - Prevents CSRF attacks

2. **Token Management**
   - Refresh token stored securely in database
   - Access token auto-refreshed when expired
   - Tokens never logged or exposed in responses

3. **API Access**
   - All endpoints require JWT authentication
   - Only admins can create/update/delete events
   - Calendar ID tied to garage account

4. **Production Requirements**
   - Use strong GOOGLE_OAUTH_STATE_SECRET (256+ bits)
   - Enable HTTPS for OAuth callbacks
   - Rotate secrets periodically
   - Implement rate limiting
   - Monitor API quota usage

## Implementation Details

### Files Modified/Created

```
backend/
├── app/
│   ├── models/
│   │   ├── work_order.py          [MODIFIED] Added google_event_id
│   │   └── google_oauth.py        [NEW] GoogleOAuthToken model
│   ├── google_calendar.py         [NEW] OAuth and Calendar service
│   └── api/v1/endpoints/
│       ├── google_oauth.py        [NEW] OAuth endpoints
│       └── lavori_calendar.py     [NEW] Work order calendar endpoints
├── alembic/versions/
│   └── ..._add_google_calendar_support.py  [NEW] Database migration
├── .env                           [MODIFIED] New env vars
├── requirements.txt               [OK] Already has google-auth-oauthlib
└── test_google_calendar.sh        [NEW] Test examples
```

### Key Functions

**`app/google_calendar.py`:**
- `generate_oauth_state()` - Create signed CSRF state
- `verify_oauth_state()` - Validate state signature and expiry
- `create_oauth_flow()` - Initialize OAuth2 Flow
- `exchange_code_for_token()` - Code → tokens
- `save_oauth_token()` - Store tokens in DB
- `get_calendar_service()` - Build Calendar API client with auto-refresh

**`app/api/v1/endpoints/google_oauth.py`:**
- `GET /google/oauth/start` - Redirect to Google
- `GET /google/oauth/callback` - Handle Google redirect

**`app/api/v1/endpoints/lavori_calendar.py`:**
- `POST /lavori/{id}/calendar` - Create event
- `PATCH /lavori/{id}/calendar` - Update event
- `DELETE /lavori/{id}/calendar` - Delete event

## Performance Considerations

- Token refresh happens on-demand, not on every request
- Cached in memory via Credentials object (expires after 60 minutes)
- Database queries minimal (single row lookups)
- Google Calendar API calls cached in browser (CalDAV format)

## Future Enhancements

- [ ] Sync calendar events back to database (polling/webhook)
- [ ] Attendees list (customer email, technician email)
- [ ] Recurring events for maintenance
- [ ] Calendar sharing with customers
- [ ] Timezone detection from customer location
- [ ] SMS/Email reminders via Google Calendar
- [ ] Multiple garage calendars (per location)
