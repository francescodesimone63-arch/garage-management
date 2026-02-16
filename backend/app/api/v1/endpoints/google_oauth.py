"""
Google OAuth endpoints for calendar integration
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette.responses import RedirectResponse

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app import google_calendar as gc


router = APIRouter(prefix="/google/oauth", tags=["google-oauth"])


@router.get("/authorize")
async def oauth_authorize(db: AsyncSession = Depends(get_db), return_url: str = Query(None)):
    """
    Initia flusso OAuth2 con Google - reindirizza direttamente a Google per il login.
    
    **Flow:**
    1. Crea uno state token random (salvato nel DB per 2 ore con return_url)
    2. Crea Flow OAuth2 Google (con prompt=consent)
    3. Genera URL di autorizzazione
    4. **Reindirizza il browser direttamente a Google** (no JSON)
    
    **Scopes richiesti:**
    - https://www.googleapis.com/auth/calendar (lettura/scrittura calendario)
    
    **Query Parameters:**
    - return_url: URL di ritorno dopo OAuth (optional, default=/work-orders)
    
    **Ritorno:**
    - 302 redirect a Google OAuth URL
    """
    # Generate and save state token to DB (expires in 2 hours)
    state = gc.generate_oauth_state()
    await gc.save_oauth_state(db, state, return_url=return_url, expiry_minutes=120)
    
    flow = gc.create_oauth_flow()
    
    auth_url, _state = flow.authorization_url(
        access_type="offline",
        prompt="consent",  # Force new consent to ensure refresh_token
        state=state
    )
    
    # Redirect direttamente a Google (no JSON)
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
async def oauth_callback(code: str = Query(...), state: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Callback dopo che l'utente autorizza su Google.
    
    **Flow:**
    1. Valida state token dal DB e legge return_url
    2. Scambia authorization code con tokens
    3. Salva refresh_token nel DB (ID=1)
    4. Reindirizza al return_url con successo o fallback
    
    **Parametri query:**
    - code: Authorization code da Google OAuth
    - state: State token per CSRF protection
    
    **Errori:**
    - 400: State token scaduto o code non valido
    - 502: Errore Google API
    
    **Ritorno success:**
    - 303 redirect a return_url con ?calendar_auth=success
    - Fallback: http://localhost:3000/work-orders?calendar_auth=success
    """
    
    # Validate state from database AND get return_url
    state_valid, return_url = await gc.verify_oauth_state(db, state)
    if not state_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State token non valido o scaduto. Prova di nuovo."
        )
    
    # Exchange code for tokens (state already validated above)
    token_info = gc.exchange_code_for_token(code)
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code non valido. Prova di nuovo."
        )
    
    # Save tokens
    try:
        await gc.save_oauth_token(
            db,
            refresh_token=token_info["refresh_token"],
            access_token=token_info["access_token"],
            expires_in=token_info["expires_in"],
        )
    except Exception as e:
        print(f"❌ Errore salvataggio token: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Errore salvataggio token. Contatta l'amministratore."
        )
    
    # Redirect to return_url with success parameter
    if return_url:
        # Ensure return_url is clean and properly formatted
        # Remove any malformed parameters that might have been included
        clean_return_url = return_url.replace('&', '?').strip()
        separator = '&' if '?' in clean_return_url else '?'
        redirect_url = f"http://localhost:3000{clean_return_url}{separator}calendar_auth=success"
    else:
        redirect_url = "http://localhost:3000/work-orders?calendar_auth=success"
    
    print(f"🔄 OAuth Callback redirect: {redirect_url}")
    return RedirectResponse(url=redirect_url, status_code=303)


@router.get("/status")
async def oauth_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verifica se Google Calendar è configurato.
    
    **Ritorno success (token presente):**
    ```json
    {
        "configured": true,
        "calendar_id": "primary",
        "configured_at": "2026-02-13T10:00:00+01:00"
    }
    ```
    
    **Ritorno fail (token assente):**
    ```json
    {
        "configured": false,
        "message": "Google Calendar non configurato. Avvia il login OAuth.",
        "auth_url": "/api/v1/google/oauth/authorize"
    }
    ```
    """
    from app.models.google_oauth import GoogleOAuthToken
    
    result = await db.execute(select(GoogleOAuthToken).filter(GoogleOAuthToken.id == 1))
    token_record = result.scalars().first()
    
    if token_record and token_record.refresh_token:
        return {
            "configured": True,
            "calendar_id": token_record.calendar_id,
            "configured_at": token_record.updated_at.isoformat() if token_record.updated_at else None
        }
    else:
        return {
            "configured": False,
            "message": "Google Calendar non configurato. Avvia il login OAuth.",
            "auth_url": "/api/v1/google/oauth/authorize"
        }


@router.get("/info")
async def oauth_info(current_user: User = Depends(get_current_user)):
    """
    Ritorna informazioni sull'architettura di persistenza delle credenziali OAuth.
    Endpoint pubblico per documentazione.
    
    **Flusso di Salvataggio e Riuso delle Credenziali:**
    
    1. **Primo accesso (Authorization):**
       - Frontend avvia OAuth tramite `/api/v1/google/oauth/authorize`
       - Backend genera state token random
       - State token salvato nel DB con TTL di 2 ore
       - Browser reindirizzato a Google login
    
    2. **Auth Code Exchange (Callback):**
       - Google reindirizza con ?code=XXX&state=YYY
       - Backend valida state dal DB
       - Code scambiato con refresh_token e access_token
       - **Credenziali salvate nel DB (permanently)** ✅
    
    3. **Accessi Successivi (Riuso Automatico):**
       - CalendarModal richiama `/api/v1/calendar/events`
       - Backend carica refresh_token dal DB
       - Se access_token scaduto, auto-refresh utilizzando refresh_token
       - **Nessun nuovo OAuth necessario** ✅
    
    **Storage Details:**
    - Tabella: `google_oauth_tokens`
    - Record ID: 1 (single garage account pattern)
    - Campi persistenti:
        * `refresh_token`: Long-lived token (non scade finché non revocato da Google)
        * `access_token`: Short-lived token (cached for performance)
        * `access_token_expiry`: Data di scadenza dell'access token
        * `calendar_id`: ID del calendario (default: "primary")
        * `updated_at`: Timestamp ultimo aggiornamento
    
    **Auto-Refresh Mechanism:**
    - Quando `get_calendar_service()` è chiamato:
        * Controlla se `access_token` è scaduto
        * Se scaduto, usa `refresh_token` per ottenerne uno nuovo
        * Aggiorna il cache nel DB
        * Riprova l'operazione calendario
    - Questo è TOTALMENTE AUTOMATICO e trasparente
    
    **Benefici:**
    ✅ Credenziali persistenti - sopravvivono ai riavvii dell'app
    ✅ Zero friction - utenti non ripetono login
    ✅ Lungo periodo - refresh_token valido per mesi/anni
    ✅ Auto-refresh - nessun intervento manuale
    """
    return {
        "status": "OAuth credential persistence implemented",
        "storage": "Database (google_oauth_tokens table)",
        "record_id": 1,
        "lifetime": "Persistent (until Google revokes)",
        "auto_refresh": "Enabled - automatic token refresh on expiry",
        "user_friction": "Zero - no re-authentication needed",
        "next_operation": "Click 'Book Calendar' button in work order details"
    }
