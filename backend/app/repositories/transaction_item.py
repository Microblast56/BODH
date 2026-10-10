
from sqlalchemy.orm import Session

from app.models import TransactionItem


class TransactionItemRepository:
    """Database operations for individual sale lines.

    The parent transaction service controls commits and rollbacks.
    """

    def create_pending(
        self,
        db: Session,
        item_data: dict,
    ) -> TransactionItem:
        item = TransactionItem(**item_data)
        db.add(item)
        db.flush()
        return item
