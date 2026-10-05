from fastapi import APIRouter

from app.api.v1.retailers import router as retailer_router
from app.api.v1.stores import router as store_router
from app.api.v1.employees import router as employee_router
from app.api.v1.restaurants import router as restaurants_router
from app.api.v1.outlets import router as outlets_router
from app.api.v1.categories import router as category_router
from app.api.v1.products import router as product_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.product_suppliers import router as product_suppliers_router
from app.api.v1.inventories import router as inventories_router
from app.api.v1.stock_movements import router as stock_movements_router


api_router = APIRouter()


for router in (
    retailer_router,
    store_router,
    employee_router,
    restaurants_router,
    outlets_router,
    category_router,
    product_router,
    suppliers_router,
    product_suppliers_router,
    inventories_router,
    stock_movements_router,
):
    api_router.include_router(router)