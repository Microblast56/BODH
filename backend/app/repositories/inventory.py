from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Inventory
from app.schemas import InventoryCreate, InventoryUpdate


class InventoryRepository:
    def create(
        self,
        db: Session,
        inventory_data: InventoryCreate,
    ) -> Inventory:
        inventory = Inventory(
            **inventory_data.model_dump()
        )

        db.add(inventory)
        db.commit()
        db.refresh(inventory)

        return inventory

    def get_by_id(
        self,
        db: Session,
        inventory_id: int,
    ) -> Inventory | None:
        statement = select(Inventory).where(
            Inventory.id == inventory_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Inventory]:
        statement = (
            select(Inventory)
            .order_by(Inventory.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def get_by_store_and_product(
        self,
        db: Session,
        store_id: int,
        product_id: int,
    ) -> Inventory | None:
        statement = select(Inventory).where(
            Inventory.store_id == store_id,
            Inventory.product_id == product_id,
        )

        return db.scalar(statement)

    def get_by_store(
        self,
        db: Session,
        store_id: int,
    ) -> list[Inventory]:
        statement = (
            select(Inventory)
            .where(Inventory.store_id == store_id)
            .order_by(Inventory.id)
        )

        return list(db.scalars(statement).all())

    def get_by_product(
        self,
        db: Session,
        product_id: int,
    ) -> list[Inventory]:
        statement = (
            select(Inventory)
            .where(Inventory.product_id == product_id)
            .order_by(Inventory.id)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        inventory: Inventory,
        inventory_data: InventoryUpdate,
    ) -> Inventory:
        update_data = inventory_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(inventory, field, value)

        db.commit()
        db.refresh(inventory)

        return inventory

    def delete(
        self,
        db: Session,
        inventory: Inventory,
    ) -> None:
        db.delete(inventory)
        db.commit()