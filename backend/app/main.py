from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Decision Intelligence Platform",
    version=settings.APP_VERSION,
)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/")
async def root():
    return {
        "project": "BODH",
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }