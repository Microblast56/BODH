from sqlalchemy.orm import Session

from app.repositories.low_stock_report import LowStockReportRepository
from app.schemas.low_stock_report import (
    LowStockItem,
    LowStockReportResponse,
)


class LowStockReportService:
    """Business logic for read-only low-stock reporting."""

    def __init__(self) -> None:
        self.repository = LowStockReportRepository()

    def get_low_stock_report(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
    ) -> LowStockReportResponse:
        rows = self.repository.get_low_stock_items(
            db=db,
            retailer_id=retailer_id,
            store_id=store_id,
        )

        items = [LowStockItem(**row) for row in rows]

        return LowStockReportResponse(
            retailer_id=retailer_id,
            store_id=store_id,
            total_items=len(items),
            items=items,
        )