from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Supplier
from app.repositories import (
    RetailerRepository,
    SupplierRepository,
)
from app.schemas import SupplierCreate, SupplierUpdate


class SupplierService:
    def __init__(
        self,
        repository: SupplierRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
    ) -> None:
        self.repository = repository or SupplierRepository()
        self.retailer_repository = (
            retailer_repository or RetailerRepository()
        )

    def create_supplier(
        self,
        db: Session,
        supplier_data: SupplierCreate,
    ) -> Supplier:
        retailer = self.retailer_repository.get_by_id(
            db,
            supplier_data.retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError(
                "Retailer not found."
            )

        existing_supplier = self.repository.get_by_name(
            db,
            supplier_data.retailer_id,
            supplier_data.name,
        )

        if existing_supplier:
            raise ResourceConflictError(
                "A supplier with this name already exists for this retailer."
            )

        return self.repository.create(
            db,
            supplier_data,
        )

    def get_supplier(
        self,
        db: Session,
        supplier_id: int,
    ) -> Supplier:
        supplier = self.repository.get_by_id(
            db,
            supplier_id,
        )

        if supplier is None:
            raise ResourceNotFoundError(
                "Supplier not found."
            )

        return supplier

    def list_suppliers(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Supplier]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_supplier(
        self,
        db: Session,
        supplier_id: int,
        supplier_data: SupplierUpdate,
    ) -> Supplier:
        supplier = self.get_supplier(
            db,
            supplier_id,
        )

        if (
            "name" in supplier_data.model_fields_set
            and supplier_data.name is not None
            and supplier_data.name != supplier.name
        ):
            existing_supplier = self.repository.get_by_name(
                db,
                supplier.retailer_id,
                supplier_data.name,
            )

            if existing_supplier:
                raise ResourceConflictError(
                    "A supplier with this name already exists for this retailer."
                )

        return self.repository.update(
            db,
            supplier,
            supplier_data,
        )

    def delete_supplier(
        self,
        db: Session,
        supplier_id: int,
    ) -> None:
        supplier = self.get_supplier(
            db,
            supplier_id,
        )

        self.repository.delete(
            db,
            supplier,
        )