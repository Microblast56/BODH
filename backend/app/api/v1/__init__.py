from fastapi import APIRouter

from app.api.v1.retailers import router as retailers_router


api_router = APIRouter()

api_router.include_router(retailers_router)