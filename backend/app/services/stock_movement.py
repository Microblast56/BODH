from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models import StockMovement
from app.repositories import (
    EmployeeRepository,
    InventoryRepository,
    StockMovementRepository,
)
from app.schemas import (
    StockMovementCreate,
    StockMovementUpdate,
)


class StockMovementService:
    def __init__(
        self,
        repository: StockMovementRepository | None = None,
        inventory_repository: InventoryRepository | None = None,
        employee_repository: EmployeeRepository | None = None,
    ) -> None:
        self.repository = repository or StockMovementRepository()
        self.inventory_repository = (
            inventory_repository or InventoryRepository()
        )
        self.employee_repository = (
            employee_repository or EmployeeRepository()
        )

    def create_stock_movement(
        self,
        db: Session,
        movement_data: StockMovementCreate,
    ) -> StockMovement:
        inventory = self.inventory_repository.get_by_id(
            db,
            movement_data.inventory_id,
        )

        if inventory is None:
            raise ResourceNotFoundError(
                "Inventory not found."
            )

        if movement_data.employee_id is not None:
            employee = self.employee_repository.get_by_id(
                db,
                movement_data.employee_id,
            )

            if employee is None:
                raise ResourceNotFoundError(
                    "Employee not found."
                )

        return self.repository.create(
            db,
            movement_data,
        )

    def get_stock_movement(
        self,
        db: Session,
        movement_id: int,
    ) -> StockMovement:
        movement = self.repository.get_by_id(
            db,
            movement_id,
        )

        if movement is None:
            raise ResourceNotFoundError(
                "Stock movement not found."
            )

        return movement

    def list_stock_movements(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[StockMovement]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def list_by_inventory(
        self,
        db: Session,
        inventory_id: int,
    ) -> list[StockMovement]:
        inventory = self.inventory_repository.get_by_id(
            db,
            inventory_id,
        )

        if inventory is None:
            raise ResourceNotFoundError(
                "Inventory not found."
            )

        return self.repository.get_by_inventory(
            db,
            inventory_id,
        )

    def list_by_employee(
        self,
        db: Session,
        employee_id: int,
    ) -> list[StockMovement]:
        employee = self.employee_repository.get_by_id(
            db,
            employee_id,
        )

        if employee is None:
            raise ResourceNotFoundError(
                "Employee not found."
            )

        return self.repository.get_by_employee(
            db,
            employee_id,
        )

    def update_stock_movement(
        self,
        db: Session,
        movement_id: int,
        movement_data: StockMovementUpdate,
    ) -> StockMovement:
        movement = self.get_stock_movement(
            db,
            movement_id,
        )

        if (
            "employee_id" in movement_data.model_fields_set
            and movement_data.employee_id is not None
        ):
            employee = self.employee_repository.get_by_id(
                db,
                movement_data.employee_id,
            )

            if employee is None:
                raise ResourceNotFoundError(
                    "Employee not found."
                )

        return self.repository.update(
            db,
            movement,
            movement_data,
        )

    def delete_stock_movement(
        self,
        db: Session,
        movement_id: int,
    ) -> None:
        movement = self.get_stock_movement(
            db,
            movement_id,
        )

        self.repository.delete(
            db,
            movement,
        )