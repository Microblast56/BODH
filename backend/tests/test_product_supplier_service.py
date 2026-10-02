import pytest
from decimal import Decimal

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import ProductSupplier, Retailer
from app.repositories import ProductRepository, SupplierRepository
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.product_supplier import (
    ProductSupplierCreate,
    ProductSupplierUpdate,
)
from app.services.product_supplier import ProductSupplierService


service = ProductSupplierService()


def create_retailer(db):
    retailer = Retailer(
        name="Test Retailer",
        email="retailer@example.com",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def create_product(db, retailer_id, sku="SKU-001"):
    repository = ProductRepository()

    return repository.create(
        db,
        ProductCreate(
            retailer_id=retailer_id,
            name=f"Test Product {sku}",
            sku=sku,
            cost_price=Decimal("50.00"),
            selling_price=Decimal("75.00"),
            unit="piece",
        ),
    )


def create_supplier(db, retailer_id, name="Test Supplier"):
    repository = SupplierRepository()

    return repository.create(
        db,
        SupplierCreate(
            retailer_id=retailer_id,
            name=name,
        ),
    )


def test_create_product_supplier(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    data = ProductSupplierCreate(
        product_id=product.id,
        supplier_id=supplier.id,
        supplier_product_code="SUP-001",
        purchase_price=Decimal("50.00"),
        is_preferred=True,
    )

    result = service.create_product_supplier(
        db,
        data,
    )

    assert result.id is not None
    assert result.product_id == product.id
    assert result.supplier_id == supplier.id
    assert result.supplier_product_code == "SUP-001"
    assert result.purchase_price == Decimal("50.00")
    assert result.is_preferred is True


def test_create_product_supplier_without_optional_fields(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    result = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product.id,
            supplier_id=supplier.id,
        ),
    )

    assert result.id is not None
    assert result.product_id == product.id
    assert result.supplier_id == supplier.id
    assert result.supplier_product_code is None
    assert result.purchase_price is None
    assert result.is_preferred is False


def test_create_product_supplier_raises_when_product_not_found(db):
    retailer = create_retailer(db)
    supplier = create_supplier(db, retailer.id)

    with pytest.raises(ResourceNotFoundError):
        service.create_product_supplier(
            db,
            ProductSupplierCreate(
                product_id=999999,
                supplier_id=supplier.id,
            ),
        )


def test_create_product_supplier_raises_when_supplier_not_found(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)

    with pytest.raises(ResourceNotFoundError):
        service.create_product_supplier(
            db,
            ProductSupplierCreate(
                product_id=product.id,
                supplier_id=999999,
            ),
        )


def test_create_product_supplier_rejects_duplicate_link(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    data = ProductSupplierCreate(
        product_id=product.id,
        supplier_id=supplier.id,
    )

    service.create_product_supplier(db, data)

    with pytest.raises(ResourceConflictError):
        service.create_product_supplier(db, data)


def test_create_product_supplier_allows_same_supplier_for_different_products(db):
    retailer = create_retailer(db)
    supplier = create_supplier(db, retailer.id)

    product_one = create_product(
        db,
        retailer.id,
        "SKU-001",
    )

    product_two = create_product(
        db,
        retailer.id,
        "SKU-002",
    )

    first = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product_one.id,
            supplier_id=supplier.id,
        ),
    )

    second = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product_two.id,
            supplier_id=supplier.id,
        ),
    )

    assert first.id != second.id
    assert first.supplier_id == second.supplier_id


def test_get_product_supplier(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product.id,
            supplier_id=supplier.id,
        ),
    )

    result = service.get_product_supplier(
        db,
        created.id,
    )

    assert result.id == created.id
    assert result.product_id == product.id
    assert result.supplier_id == supplier.id


def test_get_product_supplier_raises_when_not_found(db):
    with pytest.raises(ResourceNotFoundError):
        service.get_product_supplier(
            db,
            999999,
        )


def test_list_product_suppliers(db):
    retailer = create_retailer(db)
    supplier = create_supplier(db, retailer.id)

    product_one = create_product(
        db,
        retailer.id,
        "SKU-001",
    )

    product_two = create_product(
        db,
        retailer.id,
        "SKU-002",
    )

    first = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product_one.id,
            supplier_id=supplier.id,
        ),
    )

    second = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product_two.id,
            supplier_id=supplier.id,
        ),
    )

    results = service.list_product_suppliers(db)

    ids = [item.id for item in results]

    assert first.id in ids
    assert second.id in ids


def test_update_product_supplier(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product.id,
            supplier_id=supplier.id,
            supplier_product_code="OLD-CODE",
            purchase_price=Decimal("50.00"),
            is_preferred=False,
        ),
    )

    updated = service.update_product_supplier(
        db,
        created.id,
        ProductSupplierUpdate(
            supplier_product_code="NEW-CODE",
            purchase_price=Decimal("65.00"),
            is_preferred=True,
        ),
    )

    assert updated.id == created.id
    assert updated.supplier_product_code == "NEW-CODE"
    assert updated.purchase_price == Decimal("65.00")
    assert updated.is_preferred is True


def test_update_product_supplier_raises_when_not_found(db):
    with pytest.raises(ResourceNotFoundError):
        service.update_product_supplier(
            db,
            999999,
            ProductSupplierUpdate(
                purchase_price=Decimal("100.00"),
            ),
        )


def test_delete_product_supplier(db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = service.create_product_supplier(
        db,
        ProductSupplierCreate(
            product_id=product.id,
            supplier_id=supplier.id,
        ),
    )

    service.delete_product_supplier(
        db,
        created.id,
    )

    result = db.get(
        ProductSupplier,
        created.id,
    )

    assert result is None