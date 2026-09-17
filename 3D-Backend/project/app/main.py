"""FastAPI application entry point.

Run with:  uvicorn app.main:app --reload
Swagger UI: http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import auth, avatars, clothing, outfits, uploads, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered 3D Virtual Dressing Room — backend API",
    version="1.0.0",
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the separate Vite frontend at localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files at /uploads/<filename>
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Route registration under the /api prefix
api_prefix = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=f"{api_prefix}/auth")
app.include_router(users.router, prefix=api_prefix)
app.include_router(avatars.router, prefix=api_prefix)
app.include_router(clothing.router, prefix=api_prefix)
app.include_router(outfits.router, prefix=api_prefix)
app.include_router(uploads.router, prefix=api_prefix)


@app.get("/", tags=["health"])
def root():
    return {"app": settings.APP_NAME, "status": "ok", "docs": "/docs"}
