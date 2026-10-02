from decimal import Decimal

from app.models import Retailer
from app.repositories import ProductRepository, SupplierRepository
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate


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


def create_product_supplier(
    client,
    product_id,
    supplier_id,
    supplier_product_code=None,
    purchase_price=None,
    is_preferred=False,
):
    payload = {
        "product_id": product_id,
        "supplier_id": supplier_id,
        "supplier_product_code": supplier_product_code,
        "purchase_price": purchase_price,
        "is_preferred": is_preferred,
    }

    return client.post(
        "/api/v1/product-suppliers",
        json=payload,
    )


def test_create_product_supplier_api(client, db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    response = create_product_supplier(
        client,
        product.id,
        supplier.id,
        "SUP-001",
        50.00,
        True,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["product_id"] == product.id
    assert data["supplier_id"] == supplier.id
    assert data["supplier_product_code"] == "SUP-001"
    assert float(data["purchase_price"]) == 50.00
    assert data["is_preferred"] is True


def test_create_product_supplier_api_rejects_missing_product(
    client,
    db,
):
    retailer = create_retailer(db)
    supplier = create_supplier(db, retailer.id)

    response = create_product_supplier(
        client,
        999999,
        supplier.id,
    )

    assert response.status_code == 404


def test_create_product_supplier_api_rejects_missing_supplier(
    client,
    db,
):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)

    response = create_product_supplier(
        client,
        product.id,
        999999,
    )

    assert response.status_code == 404


def test_create_product_supplier_api_rejects_duplicate_link(
    client,
    db,
):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    first = create_product_supplier(
        client,
        product.id,
        supplier.id,
    )

    assert first.status_code == 201

    second = create_product_supplier(
        client,
        product.id,
        supplier.id,
    )

    assert second.status_code == 409


def test_get_product_supplier_api(client, db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = create_product_supplier(
        client,
        product.id,
        supplier.id,
    )

    product_supplier_id = created.json()["id"]

    response = client.get(
        f"/api/v1/product-suppliers/{product_supplier_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_supplier_id
    assert data["product_id"] == product.id
    assert data["supplier_id"] == supplier.id


def test_get_product_supplier_api_returns_404_when_not_found(
    client,
):
    response = client.get(
        "/api/v1/product-suppliers/999999",
    )

    assert response.status_code == 404


def test_list_product_suppliers_api(client, db):
    retailer = create_retailer(db)
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
    supplier = create_supplier(db, retailer.id)

    first = create_product_supplier(
        client,
        product_one.id,
        supplier.id,
    )

    second = create_product_supplier(
        client,
        product_two.id,
        supplier.id,
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(
        "/api/v1/product-suppliers",
    )

    assert response.status_code == 200

    data = response.json()

    ids = [item["id"] for item in data]

    assert first.json()["id"] in ids
    assert second.json()["id"] in ids


def test_list_product_suppliers_api_supports_pagination(
    client,
    db,
):
    retailer = create_retailer(db)
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
    supplier = create_supplier(db, retailer.id)

    create_product_supplier(
        client,
        product_one.id,
        supplier.id,
    )

    create_product_supplier(
        client,
        product_two.id,
        supplier.id,
    )

    response = client.get(
        "/api/v1/product-suppliers?offset=0&limit=1",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_product_suppliers_api_by_product(
    client,
    db,
):
    retailer = create_retailer(db)

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

    supplier = create_supplier(db, retailer.id)

    first = create_product_supplier(
        client,
        product_one.id,
        supplier.id,
    )

    second = create_product_supplier(
        client,
        product_two.id,
        supplier.id,
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(
        f"/api/v1/product-suppliers/product/{product_one.id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["product_id"] == product_one.id
    assert data[0]["supplier_id"] == supplier.id


def test_list_product_suppliers_api_by_supplier(
    client,
    db,
):
    retailer = create_retailer(db)

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

    supplier = create_supplier(db, retailer.id)

    create_product_supplier(
        client,
        product_one.id,
        supplier.id,
    )

    create_product_supplier(
        client,
        product_two.id,
        supplier.id,
    )

    response = client.get(
        f"/api/v1/product-suppliers/supplier/{supplier.id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    product_ids = {
        item["product_id"]
        for item in data
    }

    assert product_one.id in product_ids
    assert product_two.id in product_ids


def test_update_product_supplier_api(client, db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = create_product_supplier(
        client,
        product.id,
        supplier.id,
        "OLD-CODE",
        50.00,
        False,
    )

    product_supplier_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/product-suppliers/{product_supplier_id}",
        json={
            "supplier_product_code": "NEW-CODE",
            "purchase_price": 65.00,
            "is_preferred": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_supplier_id
    assert data["supplier_product_code"] == "NEW-CODE"
    assert float(data["purchase_price"]) == 65.00
    assert data["is_preferred"] is True


def test_update_product_supplier_api_returns_404_when_not_found(
    client,
):
    response = client.patch(
        "/api/v1/product-suppliers/999999",
        json={
            "purchase_price": 100.00,
        },
    )

    assert response.status_code == 404


def test_delete_product_supplier_api(client, db):
    retailer = create_retailer(db)
    product = create_product(db, retailer.id)
    supplier = create_supplier(db, retailer.id)

    created = create_product_supplier(
        client,
        product.id,
        supplier.id,
    )

    product_supplier_id = created.json()["id"]

    response = client.delete(
        f"/api/v1/product-suppliers/{product_supplier_id}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/product-suppliers/{product_supplier_id}",
    )

    assert get_response.status_code == 404


def test_delete_product_supplier_api_returns_404_when_not_found(
    client,
):
    response = client.delete(
        "/api/v1/product-suppliers/999999",
    )

    assert response.status_code == 404