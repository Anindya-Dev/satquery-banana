from collections import defaultdict, deque
from time import monotonic
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.api.routes import router as api_router
from backend.app.api.errors import register_exception_handlers

# Setup structured logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

request_history = defaultdict(deque)

@app.middleware("http")
async def rate_limit_requests(request: Request, call_next):
    if not request.url.path.startswith(settings.API_V1_STR):
        return await call_next(request)
    client = request.client.host if request.client else "unknown"
    now = monotonic()
    history = request_history[client]
    while history and now - history[0] > 60:
        history.popleft()
    if len(history) >= settings.API_RATE_LIMIT_PER_MINUTE:
        return JSONResponse(status_code=429, content={"error": {"code": "RATE_LIMITED", "message": "Too many requests. Try again shortly."}})
    history.append(now)
    return await call_next(request)

# Register domain exception handlers
register_exception_handlers(app)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "SatQuery AI Production Backend Engine is operational.",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
