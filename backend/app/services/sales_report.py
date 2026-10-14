from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories import SalesReportRepository
from app.schemas.sales_report import SalesSummaryResponse


class SalesReportService:
    def __init__(
        self,
        repository: SalesReportRepository | None = None,
    ):
        self.repository = (
            repository or SalesReportRepository()
        )

    def get_sales_summary(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> SalesSummaryResponse:
        summary = self.repository.get_summary(
            db,
            retailer_id=retailer_id,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to,
        )

        count = summary["transaction_count"]

        average = (
            (summary["total_revenue"] / count).quantize(
                Decimal("0.01")
            )
            if count
            else Decimal("0.00")
        )

        return SalesSummaryResponse(
            retailer_id=retailer_id,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to,
            total_revenue=summary["total_revenue"],
            transaction_count=count,
            average_transaction_value=average,
            units_sold=summary["units_sold"],
        )