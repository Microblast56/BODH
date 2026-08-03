from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Store
from app.schemas import StoreCreate, StoreUpdate


class StoreRepository:
    def create(
        self,
        db: Session,
        store_data: StoreCreate,
    ) -> Store:
        store = Store(
            **store_data.model_dump()
        )

        db.add(store)
        db.commit()
        db.refresh(store)

        return store

    def get_by_id(
        self,
        db: Session,
        store_id: int,
    ) -> Store | None:
        statement = select(Store).where(
            Store.id == store_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Store]:
        statement = (
            select(Store)
            .order_by(Store.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def get_by_code(
        self,
        db: Session,
        retailer_id: int,
        code: str,
    ) -> Store | None:
        statement = select(Store).where(
            Store.retailer_id == retailer_id,
            Store.code == code,
        )

        return db.scalar(statement)

    def update(
        self,
        db: Session,
        store: Store,
        store_data: StoreUpdate,
    ) -> Store:
        update_data = store_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(store, field, value)

        db.commit()
        db.refresh(store)

        return store

    def delete(
        self,
        db: Session,
        store: Store,
    ) -> None:
        db.delete(store)
        db.commit()