
from datetime import date

from sqlalchemy.orm import Session

from app.repositories.product_performance import (
    ProductPerformanceRepository,
)
from app.schemas.product_performance import (
    ProductPerformanceItem,
    ProductPerformanceResponse,
)


class ProductPerformanceService:
    """Coordinates product performance reporting."""

    def __init__(
        self,
        repository: ProductPerformanceRepository | None = None,
    ):
        self.repository = (
            repository or ProductPerformanceRepository()
        )

    def get_product_performance(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> ProductPerformanceResponse:
        rows = self.repository.get_product_performance(
            db,
            retailer_id=retailer_id,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to,
        )

        products = [
            ProductPerformanceItem(**row)
            for row in rows
        ]

        return ProductPerformanceResponse(
            retailer_id=retailer_id,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to,
            products=products,
            total_products=len(products),
        )
