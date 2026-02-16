"""
Middleware per logging automatico di tutte le richieste API
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging_config import api_logger, get_logger

logger = get_logger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware che logga automaticamente:
    - Tutte le richieste HTTP
    - Tempi di risposta
    - Errori con stack trace completo
    """
    
    async def dispatch(self, request: Request, call_next):
        # Timestamp inizio
        start_time = time.time()
        
        # Estrai info richiesta
        method = request.method
        path = request.url.path
        user_id = getattr(request.state, "user_id", None) if hasattr(request.state, "user_id") else None
        
        # Log richiesta
        api_logger.log_request(method, path, user_id)
        
        # Log query parameters se presenti
        if request.url.query:
            logger.debug(f"Query params: {dict(request.query_params)}")
        
        # Log headers importanti
        logger.debug(f"Headers: Authorization={request.headers.get('authorization', 'None')[:20]}...")
        
        try:
            # Esegui richiesta
            response = await call_next(request)
            
            # Calcola durata
            duration_ms = (time.time() - start_time) * 1000
            
            # Log risposta
            api_logger.log_response(method, path, response.status_code, duration_ms)
            
            # Warning se lenta (>2 secondi)
            if duration_ms > 2000:
                logger.warning(f"SLOW REQUEST: {method} {path} took {duration_ms:.2f}ms")
            
            return response
            
        except Exception as e:
            # Log errore completo
            duration_ms = (time.time() - start_time) * 1000
            api_logger.log_error(method, path, e)
            
            # Log dettagli aggiuntivi
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            logger.error(f"Request: {method} {path}")
            logger.error(f"Duration: {duration_ms:.2f}ms")
            
            # Re-raise per permettere a FastAPI di gestirlo
            raise
