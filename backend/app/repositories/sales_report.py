from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction, TransactionItem


class SalesReportRepository:
    """Read-only database aggregations for sales reporting."""

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
            filters.append(
                Transaction.created_at < end_exclusive
            )

        return filters

    def get_summary(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        filters = self._build_filters(
            retailer_id,
            store_id,
            date_from,
            date_to,
        )

        transaction_statement = select(
            func.count(Transaction.id),
            func.coalesce(
                func.sum(Transaction.total_amount),
                Decimal("0.00"),
            ),
        ).where(*filters)

        transaction_count, total_revenue = db.execute(
            transaction_statement
        ).one()

        item_statement = (
            select(
                func.coalesce(
                    func.sum(TransactionItem.quantity),
                    0,
                )
            )
            .join(
                Transaction,
                Transaction.id == TransactionItem.transaction_id,
            )
            .where(*filters)
        )

        units_sold = db.scalar(item_statement)

        return {
            "transaction_count": transaction_count,
            "total_revenue": Decimal(
                str(total_revenue)
            ).quantize(Decimal("0.01")),
            "units_sold": int(units_sold or 0),
        }