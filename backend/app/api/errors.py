import uuid
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from backend.app.core.exceptions import SatQueryException
from backend.app.core.logging import logger

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(SatQueryException)
    async def satquery_exception_handler(request: Request, exc: SatQueryException):
        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        logger.warning(
            "Domain exception caught.",
            error_code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=req_id
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        logger.error(
            "Unhandled system exception caught.",
            error=str(exc),
            request_id=req_id
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected backend processing error occurred.",
                    "request_id": req_id
                }
            }
        )
