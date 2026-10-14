from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Inventory, Product, Store


class LowStockReportRepository:
    """Read-only database queries for low-stock reporting."""

    def get_low_stock_items(
        self,
        db: Session,
        retailer_id: int | None = None,
        store_id: int | None = None,
    ) -> list[dict]:
        statement = (
            select(
                Inventory.id.label("inventory_id"),
                Store.retailer_id.label("retailer_id"),
                Store.id.label("store_id"),
                Store.name.label("store_name"),
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.sku.label("sku"),
                Inventory.quantity_on_hand.label("quantity_on_hand"),
                Inventory.reorder_level.label("reorder_level"),
                Inventory.reorder_quantity.label("reorder_quantity"),
            )
            .join(Store, Store.id == Inventory.store_id)
            .join(Product, Product.id == Inventory.product_id)
            .where(
                Inventory.quantity_on_hand <= Inventory.reorder_level
            )
        )

        if retailer_id is not None:
            statement = statement.where(
                Store.retailer_id == retailer_id
            )

        if store_id is not None:
            statement = statement.where(
                Inventory.store_id == store_id
            )

        statement = statement.order_by(
            Inventory.quantity_on_hand.asc(),
            Product.name.asc(),
        )

        rows = db.execute(statement).mappings().all()

        return [
            {
                **dict(row),
                "shortage_quantity": max(
                    row["reorder_level"] - row["quantity_on_hand"],
                    0,
                ),
            }
            for row in rows
        ]