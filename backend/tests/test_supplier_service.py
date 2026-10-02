import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Retailer, Supplier
from app.schemas import SupplierCreate, SupplierUpdate
from app.services import SupplierService


service = SupplierService()


def create_retailer(db, name="Test Retailer"):
    retailer = Retailer(
        name=name,
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def test_create_supplier(db):
    retailer = create_retailer(db)

    supplier_data = SupplierCreate(
        retailer_id=retailer.id,
        name="Test Supplier",
        contact_person="John Doe",
        email="supplier@example.com",
        phone="1111111111",
        address="Test Address",
    )

    supplier = service.create_supplier(
        db,
        supplier_data,
    )

    assert supplier.id is not None
    assert supplier.retailer_id == retailer.id
    assert supplier.name == "Test Supplier"
    assert supplier.contact_person == "John Doe"
    assert supplier.email == "supplier@example.com"
    assert supplier.phone == "1111111111"
    assert supplier.address == "Test Address"
    assert supplier.is_active is True


def test_create_supplier_without_optional_fields(db):
    retailer = create_retailer(db)

    supplier_data = SupplierCreate(
        retailer_id=retailer.id,
        name="Minimal Supplier",
    )

    supplier = service.create_supplier(
        db,
        supplier_data,
    )

    assert supplier.id is not None
    assert supplier.name == "Minimal Supplier"
    assert supplier.contact_person is None
    assert supplier.email is None
    assert supplier.phone is None
    assert supplier.address is None
    assert supplier.is_active is True


def test_create_supplier_raises_when_retailer_not_found(db):
    supplier_data = SupplierCreate(
        retailer_id=999999,
        name="Invalid Supplier",
    )

    with pytest.raises(ResourceNotFoundError):
        service.create_supplier(
            db,
            supplier_data,
        )


def test_create_supplier_rejects_duplicate_name(db):
    retailer = create_retailer(db)

    first_data = SupplierCreate(
        retailer_id=retailer.id,
        name="Duplicate Supplier",
    )

    service.create_supplier(
        db,
        first_data,
    )

    second_data = SupplierCreate(
        retailer_id=retailer.id,
        name="Duplicate Supplier",
    )

    with pytest.raises(ResourceConflictError):
        service.create_supplier(
            db,
            second_data,
        )


def test_create_supplier_allows_same_name_for_different_retailers(db):
    first_retailer = create_retailer(
        db,
        name="First Retailer",
    )

    second_retailer = create_retailer(
        db,
        name="Second Retailer",
    )

    first_supplier = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=first_retailer.id,
            name="Same Supplier",
        ),
    )

    second_supplier = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=second_retailer.id,
            name="Same Supplier",
        ),
    )

    assert first_supplier.id != second_supplier.id
    assert first_supplier.retailer_id == first_retailer.id
    assert second_supplier.retailer_id == second_retailer.id


def test_get_supplier(db):
    retailer = create_retailer(db)

    created = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="Get Supplier",
        ),
    )

    supplier = service.get_supplier(
        db,
        created.id,
    )

    assert supplier.id == created.id
    assert supplier.name == "Get Supplier"


def test_get_supplier_raises_when_not_found(db):
    with pytest.raises(ResourceNotFoundError):
        service.get_supplier(
            db,
            999999,
        )


def test_list_suppliers(db):
    retailer = create_retailer(db)

    first = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="First Supplier",
        ),
    )

    second = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="Second Supplier",
        ),
    )

    suppliers = service.list_suppliers(
        db,
    )

    supplier_ids = [supplier.id for supplier in suppliers]

    assert first.id in supplier_ids
    assert second.id in supplier_ids


def test_update_supplier(db):
    retailer = create_retailer(db)

    supplier = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="Original Supplier",
            email="original@example.com",
            phone="3333333333",
        ),
    )

    updated = service.update_supplier(
        db,
        supplier.id,
        SupplierUpdate(
            name="Updated Supplier",
            phone="4444444444",
        ),
    )

    assert updated.id == supplier.id
    assert updated.name == "Updated Supplier"
    assert updated.email == "original@example.com"
    assert updated.phone == "4444444444"


def test_update_supplier_rejects_duplicate_name(db):
    retailer = create_retailer(db)

    first = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="First Supplier",
        ),
    )

    second = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="Second Supplier",
        ),
    )

    with pytest.raises(ResourceConflictError):
        service.update_supplier(
            db,
            second.id,
            SupplierUpdate(
                name=first.name,
            ),
        )


def test_delete_supplier_soft_deletes_supplier(db):
    retailer = create_retailer(db)

    supplier = service.create_supplier(
        db,
        SupplierCreate(
            retailer_id=retailer.id,
            name="Delete Supplier",
        ),
    )

    service.delete_supplier(
        db,
        supplier.id,
    )

    db.refresh(supplier)

    assert supplier.is_active is False