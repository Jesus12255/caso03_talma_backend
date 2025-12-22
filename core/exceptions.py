
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app.core.exceptions")

class AppBaseException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code

class NotFoundException(AppBaseException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

async def app_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppBaseException, app_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
