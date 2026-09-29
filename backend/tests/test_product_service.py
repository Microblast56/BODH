from decimal import Decimal
import pytest

from app.models import Category, Retailer
from app.schemas import ProductCreate, ProductUpdate
from app.services import ProductService
from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)


def test_create_product(db):
    # Arrange
    retailer = Retailer(
        name="Test Retailer",
        email="test@bodh.local",
        phone="9999999999",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    category = Category(
        retailer_id=retailer.id,
        name="Beverages",
        description="Test beverage category",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=category.id,
        name="Test Coca Cola",
        sku="TEST-COKE-500",
        barcode="1234567890123",
        description="Test product",
        cost_price=Decimal("30.00"),
        selling_price=Decimal("40.00"),
        unit="piece",
        tax_rate=Decimal("18.00"),
    )

    service = ProductService()

    # Act
    product = service.create_product(
        db,
        product_data,
    )

    # Assert
    assert product.id is not None
    assert product.retailer_id == retailer.id
    assert product.category_id == category.id
    assert product.name == "Test Coca Cola"
    assert product.sku == "TEST-COKE-500"
    assert product.cost_price == Decimal("30.00")
    assert product.selling_price == Decimal("40.00")
    assert product.is_active is True


def test_create_product_rejects_nonexistent_retailer(db):
    # Arrange
    product_data = ProductCreate(
        retailer_id=999999,
        category_id=None,
        name="Orphan Product",
        sku="ORPHAN-001",
        cost_price=Decimal("10.00"),
        selling_price=Decimal("15.00"),
        unit="piece",
    )

    service = ProductService()

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.create_product(
            db,
            product_data,
        )

def test_create_product_rejects_duplicate_sku(db):
    # Arrange
    retailer = Retailer(
        name="Duplicate SKU Retailer",
        email="duplicate@bodh.local",
        phone="8888888888",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    category = Category(
        retailer_id=retailer.id,
        name="Beverages",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=category.id,
        name="First Product",
        sku="DUPLICATE-SKU-001",
        cost_price=Decimal("20.00"),
        selling_price=Decimal("30.00"),
        unit="piece",
    )

    service = ProductService()

    # Act
    service.create_product(
        db,
        product_data,
    )

    # Assert
    with pytest.raises(ResourceConflictError):
        service.create_product(
            db,
            product_data,
        )

def test_create_product_rejects_nonexistent_category(db):
    # Arrange
    retailer = Retailer(
        name="Category Test Retailer",
        email="category@bodh.local",
        phone="7777777777",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=999999,
        name="Orphan Category Product",
        sku="ORPHAN-CATEGORY-001",
        cost_price=Decimal("20.00"),
        selling_price=Decimal("30.00"),
        unit="piece",
    )

    service = ProductService()

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.create_product(
            db,
            product_data,
        )

def test_create_product_rejects_category_from_another_retailer(db):
    # Arrange
    retailer_one = Retailer(
        name="Retailer One",
        email="retailer-one@bodh.local",
        phone="6666666666",
    )

    retailer_two = Retailer(
        name="Retailer Two",
        email="retailer-two@bodh.local",
        phone="5555555555",
    )

    db.add_all(
        [
            retailer_one,
            retailer_two,
        ]
    )
    db.commit()

    db.refresh(retailer_one)
    db.refresh(retailer_two)

    category = Category(
        retailer_id=retailer_one.id,
        name="Beverages",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product_data = ProductCreate(
        retailer_id=retailer_two.id,
        category_id=category.id,
        name="Wrong Retailer Product",
        sku="WRONG-RETAILER-001",
        cost_price=Decimal("20.00"),
        selling_price=Decimal("30.00"),
        unit="piece",
    )

    service = ProductService()

    # Act + Assert
    with pytest.raises(ResourceConflictError):
        service.create_product(
            db,
            product_data,
        )

def test_get_product(db):
    # Arrange
    retailer = Retailer(
        name="Get Product Retailer",
        email="get-product@bodh.local",
        phone="4444444444",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="Get Test Product",
        sku="GET-TEST-001",
        cost_price=Decimal("50.00"),
        selling_price=Decimal("75.00"),
        unit="piece",
    )

    service = ProductService()

    created_product = service.create_product(
        db,
        product_data,
    )

    # Act
    product = service.get_product(
        db,
        created_product.id,
    )

    # Assert
    assert product.id == created_product.id
    assert product.name == "Get Test Product"
    assert product.sku == "GET-TEST-001"
    assert product.retailer_id == retailer.id


def test_get_product_rejects_nonexistent_product(db):
    # Arrange
    service = ProductService()

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.get_product(
            db,
            999999,
        )

def test_update_product(db):
    # Arrange
    retailer = Retailer(
        name="Update Product Retailer",
        email="update-product@bodh.local",
        phone="3333333333",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="Original Product",
        sku="UPDATE-001",
        cost_price=Decimal("50.00"),
        selling_price=Decimal("75.00"),
        unit="piece",
    )

    service = ProductService()

    product = service.create_product(
        db,
        product_data,
    )

    update_data = ProductUpdate(
        name="Updated Product",
        selling_price=Decimal("85.00"),
    )

    # Act
    updated_product = service.update_product(
        db,
        product.id,
        update_data,
    )

    # Assert
    assert updated_product.id == product.id
    assert updated_product.name == "Updated Product"
    assert updated_product.selling_price == Decimal("85.00")

    # These should remain unchanged
    assert updated_product.sku == "UPDATE-001"
    assert updated_product.cost_price == Decimal("50.00")
    assert updated_product.retailer_id == retailer.id

def test_update_product_category(db):
    # Arrange
    retailer = Retailer(
        name="Category Update Retailer",
        email="category-update@bodh.local",
        phone="2222222222",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    old_category = Category(
        retailer_id=retailer.id,
        name="Old Category",
    )

    new_category = Category(
        retailer_id=retailer.id,
        name="New Category",
    )

    db.add_all(
        [
            old_category,
            new_category,
        ]
    )
    db.commit()

    db.refresh(old_category)
    db.refresh(new_category)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=old_category.id,
        name="Category Update Product",
        sku="CATEGORY-UPDATE-001",
        cost_price=Decimal("40.00"),
        selling_price=Decimal("60.00"),
        unit="piece",
    )

    service = ProductService()

    product = service.create_product(
        db,
        product_data,
    )

    update_data = ProductUpdate(
        category_id=new_category.id,
    )

    # Act
    updated_product = service.update_product(
        db,
        product.id,
        update_data,
    )

    # Assert
    assert updated_product.category_id == new_category.id
    assert updated_product.category_id != old_category.id

def test_update_product_rejects_nonexistent_product(db):
    # Arrange
    service = ProductService()

    update_data = ProductUpdate(
        name="Updated Product",
    )

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.update_product(
            db,
            999999,
            update_data,
        )

def test_update_product_rejects_duplicate_sku(db):
    # Arrange
    retailer = Retailer(
        name="SKU Update Retailer",
        email="sku-update@bodh.local",
        phone="1111111111",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    first_product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="First Product",
        sku="EXISTING-SKU-001",
        cost_price=Decimal("20.00"),
        selling_price=Decimal("30.00"),
        unit="piece",
    )

    second_product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="Second Product",
        sku="SECOND-SKU-001",
        cost_price=Decimal("25.00"),
        selling_price=Decimal("35.00"),
        unit="piece",
    )

    service = ProductService()

    first_product = service.create_product(
        db,
        first_product_data,
    )

    second_product = service.create_product(
        db,
        second_product_data,
    )

    update_data = ProductUpdate(
        sku=first_product.sku,
    )

    # Act + Assert
    with pytest.raises(ResourceConflictError):
        service.update_product(
            db,
            second_product.id,
            update_data,
        )

def test_update_product_rejects_nonexistent_category(db):
    # Arrange
    retailer = Retailer(
        name="Update Category Retailer",
        email="update-category@bodh.local",
        phone="1010101010",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="Category Update Test Product",
        sku="CATEGORY-UPDATE-TEST-001",
        cost_price=Decimal("30.00"),
        selling_price=Decimal("45.00"),
        unit="piece",
    )

    service = ProductService()

    product = service.create_product(
        db,
        product_data,
    )

    update_data = ProductUpdate(
        category_id=999999,
    )

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.update_product(
            db,
            product.id,
            update_data,
        )

def test_update_product_rejects_category_from_another_retailer(db):
    # Arrange
    retailer_one = Retailer(
        name="Update Retailer One",
        email="update-retailer-one@bodh.local",
        phone="1212121212",
    )

    retailer_two = Retailer(
        name="Update Retailer Two",
        email="update-retailer-two@bodh.local",
        phone="1313131313",
    )

    db.add_all(
        [
            retailer_one,
            retailer_two,
        ]
    )
    db.commit()

    db.refresh(retailer_one)
    db.refresh(retailer_two)

    category_one = Category(
        retailer_id=retailer_one.id,
        name="Retailer One Category",
    )

    db.add(category_one)
    db.commit()
    db.refresh(category_one)

    product_data = ProductCreate(
        retailer_id=retailer_two.id,
        category_id=None,
        name="Cross Retailer Update Product",
        sku="CROSS-RETAILER-UPDATE-001",
        cost_price=Decimal("25.00"),
        selling_price=Decimal("40.00"),
        unit="piece",
    )

    service = ProductService()

    product = service.create_product(
        db,
        product_data,
    )

    update_data = ProductUpdate(
        category_id=category_one.id,
    )

    # Act + Assert
    with pytest.raises(ResourceConflictError):
        service.update_product(
            db,
            product.id,
            update_data,
        )
def test_delete_product(db):
    # Arrange
    retailer = Retailer(
        name="Delete Product Retailer",
        email="delete-product@bodh.local",
        phone="1414141414",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    product_data = ProductCreate(
        retailer_id=retailer.id,
        category_id=None,
        name="Product To Delete",
        sku="DELETE-001",
        cost_price=Decimal("30.00"),
        selling_price=Decimal("45.00"),
        unit="piece",
    )

    service = ProductService()

    product = service.create_product(
        db,
        product_data,
    )

    product_id = product.id

    # Act
    service.delete_product(
        db,
        product_id,
    )

    # Assert
    with pytest.raises(ResourceNotFoundError):
        service.get_product(
            db,
            product_id,
        )

def test_delete_product_rejects_nonexistent_product(db):
    # Arrange
    service = ProductService()

    # Act + Assert
    with pytest.raises(ResourceNotFoundError):
        service.delete_product(
            db,
            999999,
        )

def test_list_products(db):
    # Arrange
    retailer = Retailer(
        name="List Products Retailer",
        email="list-products@bodh.local",
        phone="1515151515",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    service = ProductService()

    products_data = [
        ProductCreate(
            retailer_id=retailer.id,
            category_id=None,
            name="Product One",
            sku="LIST-001",
            cost_price=Decimal("10.00"),
            selling_price=Decimal("15.00"),
            unit="piece",
        ),
        ProductCreate(
            retailer_id=retailer.id,
            category_id=None,
            name="Product Two",
            sku="LIST-002",
            cost_price=Decimal("20.00"),
            selling_price=Decimal("30.00"),
            unit="piece",
        ),
        ProductCreate(
            retailer_id=retailer.id,
            category_id=None,
            name="Product Three",
            sku="LIST-003",
            cost_price=Decimal("30.00"),
            selling_price=Decimal("45.00"),
            unit="piece",
        ),
    ]

    for product_data in products_data:
        service.create_product(
            db,
            product_data,
        )

    # Act
    products = service.list_products(db)

    # Assert
    assert len(products) == 3
    assert products[0].name == "Product One"
    assert products[1].name == "Product Two"
    assert products[2].name == "Product Three"