
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Transaction


class TransactionRepository:
    """Database operations for sales transactions.

    These methods deliberately do not commit. The service layer
    owns the transaction boundary for an entire sale.
    """

    def create_pending(
        self,
        db: Session,
        transaction_data: dict,
    ) -> Transaction:
        transaction = Transaction(**transaction_data)
        db.add(transaction)
        db.flush()
        return transaction

    def get_by_id(
        self,
        db: Session,
        transaction_id: int,
    ) -> Transaction | None:
        statement = (
            select(Transaction)
            .options(selectinload(Transaction.items))
            .where(Transaction.id == transaction_id)
        )
        return db.scalar(statement)

    def get_by_number(
        self,
        db: Session,
        retailer_id: int,
        transaction_number: str,
    ) -> Transaction | None:
        statement = select(Transaction).where(
            Transaction.retailer_id == retailer_id,
            Transaction.transaction_number == transaction_number,
        )
        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .options(selectinload(Transaction.items))
            .order_by(Transaction.id)
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(statement).all())
