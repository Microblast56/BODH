from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory
from app.repositories import (
    EmployeeRepository,
    InventoryRepository,
    ProductRepository,
    StockMovementRepository,
    StoreRepository,
)
from app.schemas import (
    InventoryCreate,
    InventoryUpdate,
    StockInCreate,
    StockMovementCreate,
    StockOutCreate,
)


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository | None = None,
        store_repository: StoreRepository | None = None,
        product_repository: ProductRepository | None = None,
        stock_movement_repository: StockMovementRepository | None = None,
        employee_repository: EmployeeRepository | None = None,
    ) -> None:
        self.repository = repository or InventoryRepository()
        self.store_repository = (
            store_repository or StoreRepository()
        )
        self.product_repository = (
            product_repository or ProductRepository()
        )
        self.stock_movement_repository = (
            stock_movement_repository
            or StockMovementRepository()
        )
        self.employee_repository = (
            employee_repository or EmployeeRepository()
        )

    # ------------------------------------------------------------------
    # Standard inventory operations
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Stock-in
    # ------------------------------------------------------------------

    def stock_in(
        self,
        db: Session,
        inventory_id: int,
        stock_data: StockInCreate,
    ) -> Inventory:
        quantity = stock_data.quantity

        if quantity <= 0:
            raise ValueError(
                "Stock-in quantity must be greater than zero."
            )

        inventory = self.repository.get_by_id_for_update(
            db,
            inventory_id,
        )

        if inventory is None:
            raise ResourceNotFoundError(
                "Inventory not found."
            )

        if stock_data.employee_id is not None:
            employee = self.employee_repository.get_by_id(
                db,
                stock_data.employee_id,
            )

            if employee is None:
                raise ResourceNotFoundError(
                    "Employee not found."
                )

        # The repository performs the actual quantity mutation.
        self.repository.adjust_quantity(
            db,
            inventory,
            quantity,
        )

        inventory.last_restocked_at = datetime.now(
            timezone.utc
        )

        movement_data = StockMovementCreate(
            inventory_id=inventory.id,
            employee_id=stock_data.employee_id,
            movement_type="stock_in",
            quantity_change=quantity,
            reference_type=stock_data.reference_type,
            reference_id=stock_data.reference_id,
            notes=stock_data.notes,
        )

        self.stock_movement_repository.create_pending(
            db,
            movement_data,
        )

        db.commit()
        db.refresh(inventory)

        return inventory

    # ------------------------------------------------------------------
    # Stock-out
    # ------------------------------------------------------------------

    def stock_out(
        self,
        db: Session,
        inventory_id: int,
        stock_data: StockOutCreate,
    ) -> Inventory:
        quantity = stock_data.quantity

        if quantity <= 0:
            raise ValueError(
                "Stock-out quantity must be greater than zero."
            )

        inventory = self.repository.get_by_id_for_update(
            db,
            inventory_id,
        )

        if inventory is None:
            raise ResourceNotFoundError(
                "Inventory not found."
            )

        if inventory.quantity_on_hand < quantity:
            raise ResourceConflictError(
                "Insufficient stock."
            )

        if stock_data.employee_id is not None:
            employee = self.employee_repository.get_by_id(
                db,
                stock_data.employee_id,
            )

            if employee is None:
                raise ResourceNotFoundError(
                    "Employee not found."
                )

        # The repository performs the actual quantity mutation.
        self.repository.adjust_quantity(
            db,
            inventory,
            -quantity,
        )

        movement_data = StockMovementCreate(
            inventory_id=inventory.id,
            employee_id=stock_data.employee_id,
            movement_type="stock_out",
            quantity_change=-quantity,
            reference_type=stock_data.reference_type,
            reference_id=stock_data.reference_id,
            notes=stock_data.notes,
        )

        self.stock_movement_repository.create_pending(
            db,
            movement_data,
        )

        db.commit()
        db.refresh(inventory)

        return inventory