from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Retailer
from app.repositories import RetailerRepository
from app.schemas import RetailerCreate, RetailerUpdate


class RetailerService:
    def __init__(
        self,
        repository: RetailerRepository | None = None,
    ) -> None:
        self.repository = repository or RetailerRepository()

    def create_retailer(
        self,
        db: Session,
        retailer_data: RetailerCreate,
    ) -> Retailer:
        if retailer_data.email:
            existing_retailer = self.repository.get_by_email(
                db,
                retailer_data.email,
            )

            if existing_retailer:
                raise ResourceConflictError(
                    "A retailer with this email already exists."
                )

        return self.repository.create(
            db,
            retailer_data,
        )

    def get_retailer(
        self,
        db: Session,
        retailer_id: int,
    ) -> Retailer:
        retailer = self.repository.get_by_id(
            db,
            retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError(
                "Retailer not found."
            )

        return retailer

    def list_retailers(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Retailer]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_retailer(
        self,
        db: Session,
        retailer_id: int,
        retailer_data: RetailerUpdate,
    ) -> Retailer:
        retailer = self.get_retailer(
            db,
            retailer_id,
        )

        if (
            "email" in retailer_data.model_fields_set
            and retailer_data.email is not None
            and retailer_data.email != retailer.email
        ):
            existing_retailer = self.repository.get_by_email(
                db,
                retailer_data.email,
            )

            if existing_retailer:
                raise ResourceConflictError(
                    "A retailer with this email already exists."
                )

        return self.repository.update(
            db,
            retailer,
            retailer_data,
        )

    def delete_retailer(
        self,
        db: Session,
        retailer_id: int,
    ) -> None:
        retailer = self.get_retailer(
            db,
            retailer_id,
        )

        self.repository.delete(
            db,
            retailer,
        )