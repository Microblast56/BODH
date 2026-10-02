from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory
from app.repositories import (
    InventoryRepository,
    ProductRepository,
    StoreRepository,
)
from app.schemas import InventoryCreate, InventoryUpdate


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository | None = None,
        store_repository: StoreRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        self.repository = repository or InventoryRepository()
        self.store_repository = (
            store_repository or StoreRepository()
        )
        self.product_repository = (
            product_repository or ProductRepository()
        )

    def create_inventory(
        self,
        db: Session,
        inventory_data: InventoryCreate,
    ) -> Inventory:
        store = self.store_repository.get_by_id(
            db,
            inventory_data.store_id,
        )

        if store is None:
            raise ResourceNotFoundError(
                "Store not found."
            )

        product = self.product_repository.get_by_id(
            db,
            inventory_data.product_id,
        )

        if product is None:
            raise ResourceNotFoundError(
                "Product not found."
            )

        existing_inventory = (
            self.repository.get_by_store_and_product(
                db,
                inventory_data.store_id,
                inventory_data.product_id,
            )
        )

        if existing_inventory:
            raise ResourceConflictError(
                "Inventory already exists for this store and product."
            )

        return self.repository.create(
            db,
            inventory_data,
        )

    def get_inventory(
        self,
        db: Session,
        inventory_id: int,
    ) -> Inventory:
        inventory = self.repository.get_by_id(
            db,
            inventory_id,
        )

        if inventory is None:
            raise ResourceNotFoundError(
                "Inventory not found."
            )

        return inventory

    def list_inventories(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Inventory]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def list_by_store(
        self,
        db: Session,
        store_id: int,
    ) -> list[Inventory]:
        store = self.store_repository.get_by_id(
            db,
            store_id,
        )

        if store is None:
            raise ResourceNotFoundError(
                "Store not found."
            )

        return self.repository.get_by_store(
            db,
            store_id,
        )

    def list_by_product(
        self,
        db: Session,
        product_id: int,
    ) -> list[Inventory]:
        product = self.product_repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ResourceNotFoundError(
                "Product not found."
            )

        return self.repository.get_by_product(
            db,
            product_id,
        )

    def update_inventory(
        self,
        db: Session,
        inventory_id: int,
        inventory_data: InventoryUpdate,
    ) -> Inventory:
        inventory = self.get_inventory(
            db,
            inventory_id,
        )

        return self.repository.update(
            db,
            inventory,
            inventory_data,
        )

    def delete_inventory(
        self,
        db: Session,
        inventory_id: int,
    ) -> None:
        inventory = self.get_inventory(
            db,
            inventory_id,
        )

        self.repository.delete(
            db,
            inventory,
        )