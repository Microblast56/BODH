from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Category
from app.repositories import (
    CategoryRepository,
    RetailerRepository,
)
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
    ) -> None:
        self.repository = repository or CategoryRepository()
        self.retailer_repository = (
            retailer_repository or RetailerRepository()
        )

    def create_category(
        self,
        db: Session,
        category_data: CategoryCreate,
    ) -> Category:
        retailer = self.retailer_repository.get_by_id(
            db,
            category_data.retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError(
                "Retailer not found."
            )

        existing_category = self.repository.get_by_name(
            db,
            category_data.retailer_id,
            category_data.name,
        )

        if existing_category:
            raise ResourceConflictError(
                "A category with this name already exists for this retailer."
            )

        return self.repository.create(
            db,
            category_data,
        )

    def get_category(
        self,
        db: Session,
        category_id: int,
    ) -> Category:
        category = self.repository.get_by_id(
            db,
            category_id,
        )

        if category is None:
            raise ResourceNotFoundError(
                "Category not found."
            )

        return category

    def list_categories(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_category(
        self,
        db: Session,
        category_id: int,
        category_data: CategoryUpdate,
    ) -> Category:
        category = self.get_category(
            db,
            category_id,
        )

        if (
            "name" in category_data.model_fields_set
            and category_data.name is not None
            and category_data.name != category.name
        ):
            existing_category = self.repository.get_by_name(
                db,
                category.retailer_id,
                category_data.name,
            )

            if existing_category:
                raise ResourceConflictError(
                    "A category with this name already exists for this retailer."
                )

        return self.repository.update(
            db,
            category,
            category_data,
        )

    def delete_category(
        self,
        db: Session,
        category_id: int,
    ) -> None:
        category = self.get_category(
            db,
            category_id,
        )

        self.repository.delete(
            db,
            category,
        )