from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Store
from app.repositories import (
    RetailerRepository,
    StoreRepository,
)
from app.schemas import StoreCreate, StoreUpdate


class StoreService:
    def __init__(
        self,
        repository: StoreRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
    ) -> None:
        self.repository = repository or StoreRepository()
        self.retailer_repository = (
            retailer_repository or RetailerRepository()
        )

    def create_store(
        self,
        db: Session,
        store_data: StoreCreate,
    ) -> Store:
        retailer = self.retailer_repository.get_by_id(
            db,
            store_data.retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError(
                "Retailer not found."
            )

        existing_store = self.repository.get_by_code(
            db,
            store_data.retailer_id,
            store_data.code,
        )

        if existing_store:
            raise ResourceConflictError(
                "A store with this code already exists for this retailer."
            )

        return self.repository.create(
            db,
            store_data,
        )

    def get_store(
        self,
        db: Session,
        store_id: int,
    ) -> Store:
        store = self.repository.get_by_id(
            db,
            store_id,
        )

        if store is None:
            raise ResourceNotFoundError(
                "Store not found."
            )

        return store

    def list_stores(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Store]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_store(
        self,
        db: Session,
        store_id: int,
        store_data: StoreUpdate,
    ) -> Store:
        store = self.get_store(
            db,
            store_id,
        )

        if (
            "code" in store_data.model_fields_set
            and store_data.code is not None
            and store_data.code != store.code
        ):
            existing_store = self.repository.get_by_code(
                db,
                store.retailer_id,
                store_data.code,
            )

            if existing_store:
                raise ResourceConflictError(
                    "A store with this code already exists for this retailer."
                )

        return self.repository.update(
            db,
            store,
            store_data,
        )

    def delete_store(
        self,
        db: Session,
        store_id: int,
    ) -> None:
        store = self.get_store(
            db,
            store_id,
        )

        self.repository.delete(
            db,
            store,
        )