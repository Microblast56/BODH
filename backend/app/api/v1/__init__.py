from fastapi import APIRouter

from app.api.v1.retailers import router as retailer_router
from app.api.v1.stores import router as store_router
from app.api.v1.employees import router as employee_router

api_router = APIRouter()

api_router.include_router(retailer_router)
api_router.include_router(store_router)
api_router.include_router(employee_router)