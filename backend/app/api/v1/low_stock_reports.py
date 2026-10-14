from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.low_stock_report import LowStockReportResponse
from app.services.low_stock_report import LowStockReportService


router = APIRouter(tags=["Low Stock Reports"])
service = LowStockReportService()


@router.get(
    "/reports/low-stock",
    response_model=LowStockReportResponse,
)
def get_low_stock_report(
    retailer_id: int | None = Query(default=None, gt=0),
    store_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> LowStockReportResponse:
    """Return inventory items whose stock is at or below reorder level."""
    return service.get_low_stock_report(
        db=db,
        retailer_id=retailer_id,
        store_id=store_id,
    )