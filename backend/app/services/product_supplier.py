from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import ProductSupplier
from app.repositories import (
    ProductRepository,
    ProductSupplierRepository,
    SupplierRepository,
)
from app.schemas import (
    ProductSupplierCreate,
    ProductSupplierUpdate,
)


class ProductSupplierService:
    def __init__(
        self,
        repository: ProductSupplierRepository | None = None,
        product_repository: ProductRepository | None = None,
        supplier_repository: SupplierRepository | None = None,
    ) -> None:
        self.repository = (
            repository or ProductSupplierRepository()
        )
        self.product_repository = (
            product_repository or ProductRepository()
        )
        self.supplier_repository = (
            supplier_repository or SupplierRepository()
        )

    def create_product_supplier(
        self,
        db: Session,
        product_supplier_data: ProductSupplierCreate,
    ) -> ProductSupplier:
        product = self.product_repository.get_by_id(
            db,
            product_supplier_data.product_id,
        )

        if product is None:
            raise ResourceNotFoundError(
                "Product not found."
            )

        supplier = self.supplier_repository.get_by_id(
            db,
            product_supplier_data.supplier_id,
        )

        if supplier is None:
            raise ResourceNotFoundError(
                "Supplier not found."
            )

        existing_link = (
            self.repository.get_by_product_and_supplier(
                db,
                product_supplier_data.product_id,
                product_supplier_data.supplier_id,
            )
        )

        if existing_link:
            raise ResourceConflictError(
                "This product is already linked to this supplier."
            )

        return self.repository.create(
            db,
            product_supplier_data,
        )

    def get_product_supplier(
        self,
        db: Session,
        product_supplier_id: int,
    ) -> ProductSupplier:
        product_supplier = self.repository.get_by_id(
            db,
            product_supplier_id,
        )

        if product_supplier is None:
            raise ResourceNotFoundError(
                "Product-supplier link not found."
            )

        return product_supplier

    def list_product_suppliers(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductSupplier]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def list_by_product(
        self,
        db: Session,
        product_id: int,
    ) -> list[ProductSupplier]:
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

    def list_by_supplier(
        self,
        db: Session,
        supplier_id: int,
    ) -> list[ProductSupplier]:
        supplier = self.supplier_repository.get_by_id(
            db,
            supplier_id,
        )

        if supplier is None:
            raise ResourceNotFoundError(
                "Supplier not found."
            )

        return self.repository.get_by_supplier(
            db,
            supplier_id,
        )

    def update_product_supplier(
        self,
        db: Session,
        product_supplier_id: int,
        product_supplier_data: ProductSupplierUpdate,
    ) -> ProductSupplier:
        product_supplier = self.get_product_supplier(
            db,
            product_supplier_id,
        )

        return self.repository.update(
            db,
            product_supplier,
            product_supplier_data,
        )

    def delete_product_supplier(
        self,
        db: Session,
        product_supplier_id: int,
    ) -> None:
        product_supplier = self.get_product_supplier(
            db,
            product_supplier_id,
        )

        self.repository.delete(
            db,
            product_supplier,
        )
