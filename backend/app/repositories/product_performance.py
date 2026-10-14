
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Product, Transaction, TransactionItem


class ProductPerformanceRepository:
    """Read-only SQL aggregations for product sales performance."""

    @staticmethod
    def _build_filters(
        retailer_id: int | None,
        store_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list:
        filters = [Transaction.status == "completed"]

        if retailer_id is not None:
            filters.append(Transaction.retailer_id == retailer_id)

        if store_id is not None:
            filters.append(Transaction.store_id == store_id)

        if date_from is not None:
            start = datetime.combine(
                date_from,
                time.min,
                tzinfo=timezone.utc,
            )
            filters.append(Transaction.created_at >= start)

        if date_to is not None:
            end_exclusive = datetime.combine(
                date_to + timedelta(days=1),
                time.min,
                tzinfo=timezone.utc,
            )
            filters.append(Transaction.created_at < end_exclusive)

        return filters

    def get_product_performance(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict]:
        filters = self._build_filters(
            retailer_id=retailer_id,
            store_id=store_id,
            date_from=date_from,
            date_to=date_to,
        )

        statement = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.sku.label("sku"),
                Product.retailer_id.label("retailer_id"),
                func.coalesce(
                    func.sum(TransactionItem.quantity),
                    0,
                ).label("units_sold"),
                func.count(
                    func.distinct(Transaction.id)
                ).label("transaction_count"),
                func.coalesce(
                    func.sum(TransactionItem.line_total),
                    Decimal("0.00"),
                ).label("total_revenue"),
            )
            .join(
                TransactionItem,
                TransactionItem.product_id == Product.id,
            )
            .join(
                Transaction,
                Transaction.id == TransactionItem.transaction_id,
            )
            .where(*filters)
            .group_by(
                Product.id,
                Product.name,
                Product.sku,
                Product.retailer_id,
            )
            .order_by(
                func.sum(TransactionItem.line_total).desc(),
                Product.name.asc(),
            )
        )

        rows = db.execute(statement).mappings().all()

        results = []

        for row in rows:
            units_sold = int(row["units_sold"] or 0)
            total_revenue = Decimal(
                str(row["total_revenue"] or 0)
            ).quantize(Decimal("0.01"))

            average_selling_value_per_unit = (
                (total_revenue / units_sold).quantize(
                    Decimal("0.01")
                )
                if units_sold
                else Decimal("0.00")
            )

            results.append(
                {
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "sku": row["sku"],
                    "retailer_id": row["retailer_id"],
                    "units_sold": units_sold,
                    "transaction_count": int(
                        row["transaction_count"]
                    ),
                    "total_revenue": total_revenue,
                    "average_selling_value_per_unit": (
                        average_selling_value_per_unit
                    ),
                }
            )

        return results
