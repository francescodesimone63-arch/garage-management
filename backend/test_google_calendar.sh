#!/bin/bash
# Google Calendar Integration - Test Examples
# Replace placeholders with real values before running

# 1. START OAUTH FLOW
# This initiates the authorization process
# Go to the returned URL to authorize the app
curl -X GET "http://localhost:8000/api/v1/google/oauth/start" \
  -H "Accept: application/json" \
  -w "\n\nHTTP: %{http_code}\n"


# 2. CALLBACK (after user authorizes)
# In a real flow, Google redirects to this with code and state
# After authorization, you'll receive:
#   - code (authorization code)
#   - state (CSRF token)
# Example (replace with real values from Google redirect):
# curl -X GET "http://localhost:8000/api/v1/google/oauth/callback?code=4/0AX4XfW...&state=..." \
#   -w "\n\nHTTP: %{http_code}\n"


# 3. CREATE CALENDAR EVENT
# Creates a Google Calendar event for a work order
# Prerequisites:
#   - OAuth completed (tokens in DB)
#   - Work order ID 1 exists with data_appuntamento and data_fine_prevista set
curl -X POST "http://localhost:8000/api/v1/lavori/1/calendar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Riparazione motore",
    "description": "Analisi e riparazione motore - Cliente VIP",
    "location": "Officina Via Roma 123"
  }' \
  -w "\n\nHTTP: %{http_code}\n"


# 4. UPDATE CALENDAR EVENT
# Modifies an existing calendar event
# The work order must have google_event_id already set
curl -X PATCH "http://localhost:8000/api/v1/lavori/1/calendar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Riparazione motore - URGENTE",
    "data_appuntamento": "2026-02-15T10:00:00+01:00",
    "data_fine_prevista": "2026-02-15T13:00:00+01:00"
  }' \
  -w "\n\nHTTP: %{http_code}\n"


# 5. DELETE CALENDAR EVENT
# Removes the calendar event but keeps the work order
curl -X DELETE "http://localhost:8000/api/v1/lavori/1/calendar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -w "\n\nHTTP: %{http_code}\n"


# NOTES:
# - Replace YOUR_JWT_TOKEN_HERE with actual token from /api/v1/auth/login
# - Replace http://localhost:8000 with your API URL
# - Ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in .env
# - The refresh_token will be stored in google_oauth_tokens table after OAuth callback
# - All datetime values must be ISO 8601 with timezone offset
# - send_updates query param can be: "none" (default), "all", "externalOnly"
#
# HTTP Status Codes:
# - 200: Success
# - 400: Validation error (missing dates, invalid format, etc.)
# - 404: Work order not found
# - 409: No calendar event associated with work order (for update/delete)
# - 500: Calendar API error or no OAuth token found
# - 502: Google Calendar API failure
