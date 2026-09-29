from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Product
from app.repositories import (
    CategoryRepository,
    ProductRepository,
    RetailerRepository,
)
from app.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(
        self,
        repository: ProductRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
        category_repository: CategoryRepository | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.retailer_repository = (
            retailer_repository or RetailerRepository()
        )
        self.category_repository = (
            category_repository or CategoryRepository()
        )

    def _validate_category(
        self,
        db: Session,
        retailer_id: int,
        category_id: int | None,
    ) -> None:
        if category_id is None:
            return

        category = self.category_repository.get_by_id(
            db,
            category_id,
        )

        if category is None:
            raise ResourceNotFoundError(
                "Category not found."
            )

        if category.retailer_id != retailer_id:
            raise ResourceConflictError(
                "Category does not belong to this retailer."
            )

    def create_product(
        self,
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        retailer = self.retailer_repository.get_by_id(
            db,
            product_data.retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError(
                "Retailer not found."
            )

        self._validate_category(
            db,
            product_data.retailer_id,
            product_data.category_id,
        )

        existing_product = self.repository.get_by_sku(
            db,
            product_data.retailer_id,
            product_data.sku,
        )

        if existing_product:
            raise ResourceConflictError(
                "A product with this SKU already exists for this retailer."
            )

        return self.repository.create(
            db,
            product_data,
        )

    def get_product(
        self,
        db: Session,
        product_id: int,
    ) -> Product:
        product = self.repository.get_by_id(
            db,
            product_id,
        )

        if product is None:
            raise ResourceNotFoundError(
                "Product not found."
            )

        return product

    def list_products(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> Product:
        product = self.get_product(
            db,
            product_id,
        )

        if "category_id" in product_data.model_fields_set:
            self._validate_category(
                db,
                product.retailer_id,
                product_data.category_id,
            )

        if (
            "sku" in product_data.model_fields_set
            and product_data.sku is not None
            and product_data.sku != product.sku
        ):
            existing_product = self.repository.get_by_sku(
                db,
                product.retailer_id,
                product_data.sku,
            )

            if existing_product:
                raise ResourceConflictError(
                    "A product with this SKU already exists for this retailer."
                )

        return self.repository.update(
            db,
            product,
            product_data,
        )

    def delete_product(
        self,
        db: Session,
        product_id: int,
    ) -> None:
        product = self.get_product(
            db,
            product_id,
        )

        self.repository.delete(
            db,
            product,
        )