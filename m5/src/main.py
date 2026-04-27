import logging
import sys
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure the project root (m5/) is on sys.path when running as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import APP_TITLE, APP_VERSION, DEBUG, HOST, PORT
from src.api.routes import router
from src.cache.in_memory_cache import cache
from src.middleware.rate_limiter import RateLimitMiddleware
from src.utils.helpers import format_timestamp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="High-performance FastAPI service with TTL in-process LRU cache and per-IP rate limiting.",
    debug=DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.include_router(router)


@app.on_event("startup")
async def on_startup():
    logger.info("Application started — %s v%s", APP_TITLE, APP_VERSION)


@app.on_event("shutdown")
async def on_shutdown():
    cache.clear()
    logger.info("Cache cleared. Application shutting down.")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": format_timestamp(),
        },
    )


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=True)
