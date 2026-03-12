from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 1. Prevent Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 2. Prevent MIME Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Referrer Policy (prevent leaking sensitive URLs)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Strict-Transport-Security (HSTS)
        # Apply only in production (requires HTTPS) to enforce secure connections
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 5. Content-Security-Policy (CSP)
        # Starting with 'self' as a secure baseline. Can be expanded (e.g., adding 
        # https://www.google.com/recaptcha/ to script-src if frontend is served by FastAPI)
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # 6. Permissions-Policy
        # Disable APIs that the backend doesn't need to request from the browser
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        # 7. Obfuscate Server Headers
        response.headers["Server"] = "Talma Web API"
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response
