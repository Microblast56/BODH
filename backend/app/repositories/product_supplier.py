from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ProductSupplier
from app.schemas import (
    ProductSupplierCreate,
    ProductSupplierUpdate,
)


class ProductSupplierRepository:
    def create(
        self,
        db: Session,
        product_supplier_data: ProductSupplierCreate,
    ) -> ProductSupplier:
        product_supplier = ProductSupplier(
            **product_supplier_data.model_dump()
        )

        db.add(product_supplier)
        db.commit()
        db.refresh(product_supplier)

        return product_supplier

    def get_by_id(
        self,
        db: Session,
        product_supplier_id: int,
    ) -> ProductSupplier | None:
        statement = select(ProductSupplier).where(
            ProductSupplier.id == product_supplier_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ProductSupplier]:
        statement = (
            select(ProductSupplier)
            .order_by(ProductSupplier.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def get_by_product_and_supplier(
        self,
        db: Session,
        product_id: int,
        supplier_id: int,
    ) -> ProductSupplier | None:
        statement = select(ProductSupplier).where(
            ProductSupplier.product_id == product_id,
            ProductSupplier.supplier_id == supplier_id,
        )

        return db.scalar(statement)

    def get_by_product(
        self,
        db: Session,
        product_id: int,
    ) -> list[ProductSupplier]:
        statement = (
            select(ProductSupplier)
            .where(
                ProductSupplier.product_id == product_id
            )
            .order_by(ProductSupplier.id)
        )

        return list(db.scalars(statement).all())

    def get_by_supplier(
        self,
        db: Session,
        supplier_id: int,
    ) -> list[ProductSupplier]:
        statement = (
            select(ProductSupplier)
            .where(
                ProductSupplier.supplier_id == supplier_id
            )
            .order_by(ProductSupplier.id)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        product_supplier: ProductSupplier,
        product_supplier_data: ProductSupplierUpdate,
    ) -> ProductSupplier:
        update_data = product_supplier_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(product_supplier, field, value)

        db.commit()
        db.refresh(product_supplier)

        return product_supplier

    def delete(
        self,
        db: Session,
        product_supplier: ProductSupplier,
    ) -> None:
        db.delete(product_supplier)
        db.commit()
