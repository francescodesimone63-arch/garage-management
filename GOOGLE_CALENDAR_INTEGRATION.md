# 🚀 Google Calendar Integration - Complete Implementation

## ✅ Implementation Summary

### What Was Built

A complete **Google Calendar integration** for work order management with:

1. **OAuth2 Authorization Code Flow**
   - User-initiated Google authorization (one-time setup)
   - Automatic token refresh for persistent API access
   - HMAC-signed state parameter for CSRF protection
   - Expiry validation (10-minute window)

2. **Database Layer**
   - New `google_oauth_tokens` table for token storage
   - New `google_event_id` field in `work_orders` table (indexed)
   - Automatic token persistence and refresh

3. **Calendar Operations**
   - Create events from work order appointments
   - Update event details (title, description, time)
   - Delete events (with notification options)
   - Full error handling and validation

4. **REST API Endpoints**
   - `GET /api/v1/google/oauth/start` - Initiate OAuth
   - `GET /api/v1/google/oauth/callback` - Handle OAuth redirect (automatic)
   - `POST /api/v1/lavori/{id}/calendar` - Create event
   - `PATCH /api/v1/lavori/{id}/calendar` - Update event
   - `DELETE /api/v1/lavori/{id}/calendar` - Delete event

### Files Created/Modified

```
backend/
├── app/
│   ├── models/
│   │   ├── work_order.py                      ✏️ MODIFIED: Added google_event_id
│   │   └── google_oauth.py                    ✨ NEW: GoogleOAuthToken model
│   ├── google_calendar.py                     ✨ NEW: OAuth + Calendar service
│   └── api/v1/endpoints/
│       ├── google_oauth.py                    ✨ NEW: OAuth endpoints
│       ├── lavori_calendar.py                 ✨ NEW: Work order calendar endpoints
│       └── api.py                             ✏️ MODIFIED: Added router imports
├── models/__init__.py                         ✏️ MODIFIED: Added GoogleOAuthToken export
├── core/config.py                            ✏️ MODIFIED: Added GOOGLE_OAUTH_STATE_SECRET
├── .env                                       ✏️ MODIFIED: Added Google auth vars
├── alembic/versions/
│   └── ..._add_google_calendar_support.py    ✨ NEW: Database migration
├── garage.db                                  🔄 MIGRATED: Added 2 new columns + 1 table
├── test_google_calendar.sh                    ✨ NEW: curl test examples
├── GOOGLE_CALENDAR_SETUP.md                   ✨ NEW: Complete setup guide
└── setup_google_calendar_db.py                ✨ NEW: Database initialization script
```

---

## 🔧 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
# Already includes: google-auth-oauthlib, google-auth, google-api-python-client
```

### 2. Set Environment Variables (`.env`)
```dotenv
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google/oauth/callback
GOOGLE_CALENDAR_ID=primary
GOOGLE_OAUTH_STATE_SECRET=long-random-secret-key-here
```

### 3. Run Database Setup
```bash
python setup_google_calendar_db.py
```

### 4. Start Backend
```bash
uvicorn app.main:app --reload --port 8000
```

---

## 📚 API Documentation

### Create Calendar Event

```http
POST /api/v1/lavori/1/calendar
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "summary": "Riparazione motore",
  "description": "Analisi completa motore",
  "location": "Officina Via Roma"
}
```

**Requirements:**
- Work order must have `data_appuntamento` set (event start)
- Work order must have `data_fine_prevista` set (event end)
- `data_fine_prevista` must be after `data_appuntamento`

**Response (200):**
```json
{
  "google_event_id": "abc123def456_0",
  "html_link": "https://calendar.google.com/calendar/u/0/r/eventedit/abc123...",
  "summary": "Riparazione motore",
  "description": "Analisi completa motore",
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

### Update Calendar Event

```http
PATCH /api/v1/lavori/1/calendar?send_updates=none
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "summary": "Riparazione motore - URGENTE",
  "data_appuntamento": "2026-02-16T14:00:00+01:00",
  "data_fine_prevista": "2026-02-16T17:00:00+01:00"
}
```

**Semantics:**
- Patch: only provided fields are updated
- Datetimes must be ISO 8601 format with timezone
- Not provided fields retain current value

**Query Parameters:**
- `send_updates` (default: "none")
  - `"all"` - Notify all attendees
  - `"externalOnly"` - Notify non-Google attendees
  - `"none"` - No notifications

### Delete Calendar Event

```http
DELETE /api/v1/lavori/1/calendar
Authorization: Bearer <JWT_TOKEN>
```

**Result:**
- Event removed from Google Calendar
- `google_event_id` cleared in database
- Work order remains untouched

---

## 🔐 Security Features

### OAuth2 Security
- **State Parameter:** HMAC-SHA256 signed with expiry
- **CSRF Protection:** State validated before token exchange
- **No Email Exposure:** Tokens never logged or returned to client

### Token Management
- **Refresh Token:** Stored encrypted in database
- **Access Token:** Auto-refreshed on expiry (60 min)
- **Secure Endpoints:** JWT authentication required

### Authorization
- **Role-Based:** Only ADMIN users can manage events
- **Rate Limiting:** Implement in production

---

## ⚙️ Configuration

### Environment Variables

| Variable | Example | Note |
|----------|---------|------|
| `GOOGLE_CLIENT_ID` | Your_ID.apps.googleusercontent.com | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Your_secret | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | http://localhost:8000/api/v1/google/oauth/callback | Match Cloud Console |
| `GOOGLE_CALENDAR_ID` | primary | Usually "primary" |
| `GOOGLE_OAUTH_STATE_SECRET` | long-random-key | 256+ bits recommended |

### Google Cloud Setup

1. Create project: [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/google/oauth/callback` (dev)
   - `https://yourdomain.com/api/v1/google/oauth/callback` (prod)
5. Download client credentials JSON

---

## 🧪 Testing

### Manual Test with curl

```bash
# 1. Start OAuth flow
curl http://localhost:8000/api/v1/google/oauth/start

# 2. Open authorization URL in browser, authorize

# 3. Create calendar event
JWT_TOKEN="YOUR_TOKEN_HERE"
curl -X POST http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Test Event",
    "description": "Test description",
    "location": "Test location"
  }'

# 4. Update event
curl -X PATCH http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Updated Title",
    "data_appuntamento": "2026-02-20T10:00:00+01:00"
  }'

# 5. Delete event
curl -X DELETE http://localhost:8000/api/v1/lavori/1/calendar \
  -H "Authorization: Bearer $JWT_TOKEN"
```

See `test_google_calendar.sh` for more examples.

---

## 🐛 Troubleshooting

### "No Google OAuth token found"
**Problem:** Trying to create event without completing OAuth
**Solution:** 
1. Visit: http://localhost:8000/api/v1/google/oauth/start
2. Authorize on Google
3. Tokens will be stored in database

### "State parameter validation failed"
**Problem:** State expired or tampered with
**Solution:** Complete OAuth flow again (10-minute window)

### "Invalid datetime format"
**Problem:** Datetime not in ISO 8601 format
**Solution:** Use format: `2026-02-15T10:00:00+01:00`

### Google API Error 403
**Problem:** Calendar API not enabled in Cloud Console
**Solution:** 
1. Go to Cloud Console
2. Search "Google Calendar API"
3. Click "ENABLE"

---

## 📊 Database Schema

### google_oauth_tokens
```sql
CREATE TABLE google_oauth_tokens (
    id INTEGER PRIMARY KEY,                    -- Always 1
    refresh_token TEXT NOT NULL,               -- Long-lived token
    access_token TEXT,                         -- Short-lived, cached
    access_token_expiry DATETIME,              -- When access_token expires
    calendar_id TEXT DEFAULT 'primary',        -- Google calendar ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### work_orders (added)
```sql
ALTER TABLE work_orders ADD COLUMN google_event_id TEXT;
CREATE INDEX ix_work_orders_google_event_id ON work_orders(google_event_id);
```

---

## 🚀 Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend/Client                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ JWT Auth
                       ▼
    ┌──────────────────────────────────────┐
    │      FastAPI app (main.py)           │
    │                                      │
    │  ┌────────────────────────────────┐  │
    │  │  OAuth Endpoints               │  │
    │  │ - GET /auth/start              │  │
    │  │ - GET /auth/callback           │  │
    │  └────────────────────────────────┘  │
    │  ┌────────────────────────────────┐  │
    │  │  Calendar Endpoints            │  │
    │  │ - POST /lavori/{id}/calendar   │  │
    │  │ - PATCH /lavori/{id}/calendar  │  │
    │  │ - DELETE /lavori/{id}/calendar │  │
    │  └────────────────────────────────┘  │
    └──────────────────────┬───────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
         ┌────────────────┐    ┌────────────────┐
         │  SQLite DB     │    │ Google Calendar│
         │                │    │  API v3        │
         │ work_orders    │    │                │
         │ google_oauth   │    │ (OAuth2)       │
         │ tokens         │    │                │
         └────────────────┘    └────────────────┘
```

---

## 📝 Code Structure

### app/google_calendar.py
Core OAuth2 and Calendar API functions:
- `generate_oauth_state()` - CSRF state generation
- `verify_oauth_state()` - State validation
- `create_oauth_flow()` - OAuth2 Flow setup
- `exchange_code_for_token()` - Authorization code → tokens
- `get_calendar_service()` - Authenticated Calendar client
- `create_calendar_event()` - Create event on Calendar
- `update_calendar_event()` - Update event (patch semantics)
- `delete_calendar_event()` - Delete event

### app/api/v1/endpoints/google_oauth.py
OAuth2 endpoints:
- `GET /google/oauth/start` - Redirect to Google
- `GET /google/oauth/callback` - Handle Google callback

### app/api/v1/endpoints/lavori_calendar.py
Work order calendar endpoints:
- `POST /lavori/{id}/calendar` - Create event
- `PATCH /lavori/{id}/calendar` - Update event
- `DELETE /lavori/{id}/calendar` - Delete event

---

## 🔄 Workflow

```
1. Admin initiates OAuth
   GET /api/v1/google/oauth/start
   ↓
2. Redirected to Google authorization
   User approves access to Calendar
   ↓
3. Google redirects to callback
   GET /api/v1/google/oauth/callback?code=...&state=...
   ↓
4. Backend exchanges code for tokens
   refresh_token stored in DB
   ↓
5. Tokens ready for use
   GET /api/v1/lavori/1/calendar
   ↓
6. Create/Update/Delete events
   Events appear on Google Calendar
```

---

## ✨ Next Steps (Future Enhancements)

- [ ] Sync Google Calendar events back to database
- [ ] Add attendees (customer email, technician)
- [ ] Recurring maintenance events
- [ ] SMS/Email reminders from Calendar
- [ ] Multiple garage calendars (per location)
- [ ] Timezone auto-detection from customer location
- [ ] Calendar sharing with customers (read-only)
- [ ] Webhook integration for real-time updates

---

## 📞 Support

For detailed setup instructions, see: `GOOGLE_CALENDAR_SETUP.md`

For testing, see: `test_google_calendar.sh`

---

**Status:** ✅ Fully Implemented and Ready for Testing
