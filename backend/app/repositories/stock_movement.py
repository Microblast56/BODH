from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import StockMovement
from app.schemas import StockMovementCreate, StockMovementUpdate


class StockMovementRepository:
    def create(
        self,
        db: Session,
        movement_data: StockMovementCreate,
    ) -> StockMovement:
        movement = StockMovement(
            **movement_data.model_dump()
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement

    def get_by_id(
        self,
        db: Session,
        movement_id: int,
    ) -> StockMovement | None:
        statement = select(StockMovement).where(
            StockMovement.id == movement_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[StockMovement]:
        statement = (
            select(StockMovement)
            .order_by(StockMovement.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def get_by_inventory(
        self,
        db: Session,
        inventory_id: int,
    ) -> list[StockMovement]:
        statement = (
            select(StockMovement)
            .where(
                StockMovement.inventory_id == inventory_id
            )
            .order_by(StockMovement.id)
        )

        return list(db.scalars(statement).all())

    def get_by_employee(
        self,
        db: Session,
        employee_id: int,
    ) -> list[StockMovement]:
        statement = (
            select(StockMovement)
            .where(
                StockMovement.employee_id == employee_id
            )
            .order_by(StockMovement.id)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        movement: StockMovement,
        movement_data: StockMovementUpdate,
    ) -> StockMovement:
        update_data = movement_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(movement, field, value)

        db.commit()
        db.refresh(movement)

        return movement

    def delete(
        self,
        db: Session,
        movement: StockMovement,
    ) -> None:
        db.delete(movement)
        db.commit()