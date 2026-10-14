
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.product_performance import ProductPerformanceResponse
from app.services.product_performance import ProductPerformanceService


router = APIRouter(
    prefix="/reports",
    tags=["Product Performance"],
)

service = ProductPerformanceService()


@router.get(
    "/product-performance",
    response_model=ProductPerformanceResponse,
)
def get_product_performance(
    retailer_id: int | None = Query(default=None, gt=0),
    store_id: int | None = Query(default=None, gt=0),
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> ProductPerformanceResponse:
    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=422,
            detail="date_from must be on or before date_to.",
        )

    return service.get_product_performance(
        db,
        retailer_id=retailer_id,
        store_id=store_id,
        date_from=date_from,
        date_to=date_to,
    )
