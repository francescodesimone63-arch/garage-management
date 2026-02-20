"""
Middleware di debugging avanzato per FastAPI.
Traccia e logga tutte le richieste e risposte.
"""

import time
import json
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from app.utils.logger import main_logger


class DebugMiddleware(BaseHTTPMiddleware):
    """Middleware che logga tutti i dettagli delle richieste e risposte."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip per OPTIONS requests (preflight CORS)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        request_id = time.time()
        path = request.url.path
        method = request.method
        
        # Cattura dettagli richiesta
        start_time = time.time()
        
        try:
            # Estrai il body della richiesta se presente
            body = None
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        body = json.loads(body)
                except:
                    body = "[Binary or invalid JSON]"
                
                # Ricrea il body per il prossimo handler
                async def receive():
                    return {"type": "http.request", "body": body if isinstance(body, bytes) else json.dumps(body).encode()}
                request._receive = receive
            
            # Estrai headers importanti
            headers = {
                "user-agent": request.headers.get("user-agent", "N/A"),
                "origin": request.headers.get("origin", "N/A"),
                "authorization": "***" if request.headers.get("authorization") else "None",
            }
            
            # Log della richiesta iniziale
            main_logger.api_request(
                method=method,
                path=path,
                request_id=request_id,
                headers=headers,
                body=body,
                query_params=dict(request.query_params)
            )
            
            # Chiama il prossimo middleware/endpoint
            response = await call_next(request)
            
            # Calcola tempo di elaborazione
            duration = time.time() - start_time
            
            # Log della risposta
            main_logger.api_response(
                method=method,
                path=path,
                status_code=response.status_code,
                request_id=request_id,
                duration_ms=f"{duration*1000:.2f}",
                headers={
                    "content-type": response.headers.get("content-type", "N/A"),
                    "access-control-allow-origin": response.headers.get("access-control-allow-origin", "N/A"),
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            main_logger.error(
                f"❌ Errore nel middleware per {method} {path}",
                exception=e,
                request_id=request_id,
                duration_ms=f"{duration*1000:.2f}",
                path=path,
                method=method
            )
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware dedicato alla gestione degli errori."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            # Logga errori HTTP
            if response.status_code >= 400:
                main_logger.warning(
                    f"HTTP Error {response.status_code} on {request.method} {request.url.path}",
                    status_code=response.status_code,
                    method=request.method,
                    path=request.url.path
                )
            
            return response
            
        except Exception as e:
            main_logger.error(
                f"Eccezione non gestita in {request.method} {request.url.path}",
                exception=e,
                method=request.method,
                path=request.url.path
            )
            
            # Re-raise per far gestire a FastAPI
            raise
