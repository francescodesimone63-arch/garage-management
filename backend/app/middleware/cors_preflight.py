"""
Middleware specializzato per gestire Le OPTIONS requests (preflight CORS).
Questo middleware intercetta le richieste OPTIONS e ritorna 200 OK
con i corretti header CORS senza farle passare al routing normalmente.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CORSPreflightMiddleware(BaseHTTPMiddleware):
    """
    Middleware che intercetta e gestisce manualmente le richieste OPTIONS
    per il preflight CORS, ritornando 200 OK anziché 405.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Se è una OPTIONS request (preflight CORS), gestisci direttamente
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "http://localhost:3000",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*"),
                    "Access-Control-Max-Age": "3600",
                }
            )
        
        # Per tutte le altre richieste, continua normalmente
        return await call_next(request)
