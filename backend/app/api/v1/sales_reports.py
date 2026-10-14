from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.sales_report import SalesSummaryResponse
from app.services.sales_report import SalesReportService


router = APIRouter(
    prefix="/reports",
    tags=["Sales Reports"],
)

service = SalesReportService()


@router.get(
    "/sales-summary",
    response_model=SalesSummaryResponse,
)
def get_sales_summary(
    retailer_id: int | None = Query(default=None, gt=0),
    store_id: int | None = Query(default=None, gt=0),
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
):
    if (
        date_from is not None
        and date_to is not None
        and date_from > date_to
    ):
        raise HTTPException(
            status_code=422,
            detail="date_from must be on or before date_to.",
        )

    return service.get_sales_summary(
        db,
        retailer_id=retailer_id,
        store_id=store_id,
        date_from=date_from,
        date_to=date_to,
    )