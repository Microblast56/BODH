from decimal import Decimal

from app.models import Category, Retailer

def test_create_product_api(client, db):
    # Arrange
    retailer = Retailer(
        name="API Test Retailer",
        email="api-test@bodh.local",
        phone="1111111111",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "API Test Product",
        "sku": "API-TEST-001",
        "barcode": "9876543210123",
        "description": "Product created through API",
        "cost_price": "25.00",
        "selling_price": "35.00",
        "unit": "piece",
        "tax_rate": "18.00",
    }

    # Act
    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    # Assert
    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "API Test Product"
    assert data["sku"] == "API-TEST-001"
    assert data["cost_price"] == "25.00"
    assert data["selling_price"] == "35.00"
    assert data["unit"] == "piece"
    assert data["is_active"] is True

def test_create_product_api_rejects_duplicate_sku(client, db):
    # Arrange
    retailer = Retailer(
        name="Duplicate API Retailer",
        email="duplicate-api@bodh.local",
        phone="2222222222",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "First API Product",
        "sku": "API-DUPLICATE-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    # Create the first product
    first_response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert first_response.status_code == 201

    # Act — attempt to create another product with the same SKU
    duplicate_response = client.post(
        "/api/v1/products",
        json={
            **payload,
            "name": "Second API Product",
        },
    )

    # Assert
    assert duplicate_response.status_code == 409

    data = duplicate_response.json()

    assert data["detail"] == (
        "A product with this SKU already exists for this retailer."
    )

def test_create_product_api_rejects_nonexistent_retailer(client):
    payload = {
        "retailer_id": 999999,
        "category_id": None,
        "name": "Invalid Retailer Product",
        "sku": "API-INVALID-RETAILER-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Retailer not found."

def test_get_product_api(client, db):
    # Arrange
    retailer = Retailer(
        name="Get API Retailer",
        email="get-api@bodh.local",
        phone="3333333333",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "GET API Product",
        "sku": "API-GET-001",
        "cost_price": "40.00",
        "selling_price": "60.00",
        "unit": "piece",
    }

    create_response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert create_response.status_code == 201

    created_product = create_response.json()
    product_id = created_product["id"]

    # Act
    response = client.get(
        f"/api/v1/products/{product_id}",
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "GET API Product"
    assert data["sku"] == "API-GET-001"
    assert data["cost_price"] == "40.00"
    assert data["selling_price"] == "60.00"
    assert data["is_active"] is True

def test_get_product_api_returns_404_for_nonexistent_product(client):
    response = client.get(
        "/api/v1/products/999999",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."

def test_list_products_api(client, db):
    # Arrange
    retailer = Retailer(
        name="List API Retailer",
        email="list-api@bodh.local",
        phone="4444444444",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    first_payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "List Product One",
        "sku": "API-LIST-001",
        "cost_price": "10.00",
        "selling_price": "15.00",
        "unit": "piece",
    }

    second_payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "List Product Two",
        "sku": "API-LIST-002",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    first_response = client.post(
        "/api/v1/products",
        json=first_payload,
    )

    second_response = client.post(
        "/api/v1/products",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    # Act
    response = client.get(
        "/api/v1/products",
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    assert data[0]["sku"] == "API-LIST-001"
    assert data[1]["sku"] == "API-LIST-002"

def test_update_product_api(client, db):
    # Arrange
    retailer = Retailer(
        name="Update API Retailer",
        email="update-api@bodh.local",
        phone="5555555555",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "Original API Product",
        "sku": "API-UPDATE-001",
        "cost_price": "50.00",
        "selling_price": "75.00",
        "unit": "piece",
    }

    create_response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Act
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Updated API Product",
            "selling_price": "85.00",
        },
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Updated API Product"
    assert data["selling_price"] == "85.00"

    # Fields that weren't updated should remain unchanged
    assert data["sku"] == "API-UPDATE-001"
    assert data["cost_price"] == "50.00"
    assert data["retailer_id"] == retailer.id


def test_update_product_api_returns_404_for_nonexistent_product(client):
    response = client.patch(
        "/api/v1/products/999999",
        json={
            "name": "Updated Product",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."

def test_update_product_api_rejects_duplicate_sku(client, db):
    # Arrange
    retailer = Retailer(
        name="Duplicate Update API Retailer",
        email="duplicate-update-api@bodh.local",
        phone="6666666666",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    first_payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "First Product",
        "sku": "API-UPDATE-DUP-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    second_payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "Second Product",
        "sku": "API-UPDATE-DUP-002",
        "cost_price": "40.00",
        "selling_price": "50.00",
        "unit": "piece",
    }

    first_response = client.post(
        "/api/v1/products",
        json=first_payload,
    )

    second_response = client.post(
        "/api/v1/products",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_product_id = first_response.json()["id"]

    # Act
    response = client.patch(
        f"/api/v1/products/{first_product_id}",
        json={
            "sku": "API-UPDATE-DUP-002",
        },
    )

    # Assert
    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == (
        "A product with this SKU already exists for this retailer."
    )

def test_update_product_api_rejects_nonexistent_category(client, db):
    # Arrange
    retailer = Retailer(
        name="Invalid Category API Retailer",
        email="invalid-category-api@bodh.local",
        phone="7777777777",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "Category Validation Product",
        "sku": "API-CATEGORY-001",
        "cost_price": "30.00",
        "selling_price": "45.00",
        "unit": "piece",
    }

    create_response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Act
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": 999999,
        },
    )

    # Assert
    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Category not found."

def test_update_product_api_rejects_category_from_another_retailer(
    client,
    db,
):
    # Arrange
    retailer_one = Retailer(
        name="Category Owner Retailer",
        email="category-owner@bodh.local",
        phone="8888888888",
    )

    retailer_two = Retailer(
        name="Product Owner Retailer",
        email="product-owner@bodh.local",
        phone="9999999999",
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
        name="Retailer One Category",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product_response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer_two.id,
            "category_id": None,
            "name": "Cross Retailer Product",
            "sku": "API-CROSS-RETAILER-001",
            "cost_price": "30.00",
            "selling_price": "45.00",
            "unit": "piece",
        },
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    # Act
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "category_id": category.id,
        },
    )

    # Assert
    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == (
        "Category does not belong to this retailer."
    )

def test_delete_product_api(client, db):
    # Arrange
    retailer = Retailer(
        name="Delete API Retailer",
        email="delete-api@bodh.local",
        phone="1010101010",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "Delete API Product",
        "sku": "API-DELETE-001",
        "cost_price": "30.00",
        "selling_price": "45.00",
        "unit": "piece",
    }

    create_response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    # Act
    response = client.delete(
        f"/api/v1/products/{product_id}",
    )

    # Assert
    assert response.status_code == 204
    assert response.content == b""

    # Verify the product is no longer accessible
    get_response = client.get(
        f"/api/v1/products/{product_id}",
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Product not found."


def test_delete_product_api_returns_404_for_nonexistent_product(client):
    response = client.delete(
        "/api/v1/products/999999",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."

def test_list_products_api_respects_limit(client, db):
    # Arrange
    retailer = Retailer(
        name="Pagination Limit Retailer",
        email="pagination-limit@bodh.local",
        phone="1212121212",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    for index in range(3):
        response = client.post(
            "/api/v1/products",
            json={
                "retailer_id": retailer.id,
                "category_id": None,
                "name": f"Pagination Product {index + 1}",
                "sku": f"API-PAGE-LIMIT-{index + 1:03d}",
                "cost_price": "10.00",
                "selling_price": "15.00",
                "unit": "piece",
            },
        )

        assert response.status_code == 201

    # Act
    response = client.get(
        "/api/v1/products",
        params={"limit": 2},
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["sku"] == "API-PAGE-LIMIT-001"
    assert data[1]["sku"] == "API-PAGE-LIMIT-002"


def test_list_products_api_respects_offset(client, db):
    # Arrange
    retailer = Retailer(
        name="Pagination Offset Retailer",
        email="pagination-offset@bodh.local",
        phone="1313131313",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    for index in range(3):
        response = client.post(
            "/api/v1/products",
            json={
                "retailer_id": retailer.id,
                "category_id": None,
                "name": f"Offset Product {index + 1}",
                "sku": f"API-PAGE-OFFSET-{index + 1:03d}",
                "cost_price": "20.00",
                "selling_price": "30.00",
                "unit": "piece",
            },
        )

        assert response.status_code == 201

    # Act
    response = client.get(
        "/api/v1/products",
        params={
            "offset": 1,
            "limit": 2,
        },
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["sku"] == "API-PAGE-OFFSET-002"
    assert data[1]["sku"] == "API-PAGE-OFFSET-003"


def test_list_products_api_rejects_invalid_limit(client):
    response = client.get(
        "/api/v1/products",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_list_products_api_rejects_invalid_offset(client):
    response = client.get(
        "/api/v1/products",
        params={"offset": -1},
    )

    assert response.status_code == 422

def test_create_product_api_rejects_invalid_price(client, db):
    retailer = Retailer(
        name="Validation Retailer",
        email="validation-price@bodh.local",
        phone="1414141414",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        "name": "Invalid Price Product",
        "sku": "API-INVALID-PRICE-001",
        "cost_price": "not-a-number",
        "selling_price": "30.00",
        "unit": "piece",
    }

    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert response.status_code == 422


def test_create_product_api_rejects_missing_required_field(client, db):
    retailer = Retailer(
        name="Validation Required Retailer",
        email="validation-required@bodh.local",
        phone="1515151515",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    payload = {
        "retailer_id": retailer.id,
        "category_id": None,
        # name intentionally omitted
        "sku": "API-MISSING-NAME-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert response.status_code == 422


def test_create_product_api_rejects_invalid_retailer_id_type(client):
    payload = {
        "retailer_id": "not-an-integer",
        "category_id": None,
        "name": "Invalid Retailer ID Product",
        "sku": "API-INVALID-ID-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert response.status_code == 422

def test_list_products_api_rejects_limit_above_maximum(client):
    response = client.get(
        "/api/v1/products",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_create_product_api_rejects_invalid_category_id_type(client):
    payload = {
        "retailer_id": 999999,
        "category_id": "not-an-integer",
        "name": "Invalid Category Type Product",
        "sku": "API-INVALID-CATEGORY-TYPE-001",
        "cost_price": "20.00",
        "selling_price": "30.00",
        "unit": "piece",
    }

    response = client.post(
        "/api/v1/products",
        json=payload,
    )

    assert response.status_code == 422


def test_update_product_api_rejects_invalid_payload(client, db):
    retailer = Retailer(
        name="Invalid Update Retailer",
        email="invalid-update@bodh.local",
        phone="1616161616",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    create_response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer.id,
            "category_id": None,
            "name": "Update Validation Product",
            "sku": "API-UPDATE-VALIDATION-001",
            "cost_price": "20.00",
            "selling_price": "30.00",
            "unit": "piece",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "selling_price": "not-a-number",
        },
    )

    assert response.status_code == 422

def test_create_product_api_rejects_nonexistent_category(client, db):
    retailer = Retailer(
        name="Invalid Create Category Retailer",
        email="invalid-create-category@bodh.local",
        phone="1717171717",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer.id,
            "category_id": 999999,
            "name": "Invalid Category Product",
            "sku": "API-INVALID-CATEGORY-001",
            "cost_price": "20.00",
            "selling_price": "30.00",
            "unit": "piece",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Category not found."


def test_create_product_api_rejects_category_from_another_retailer(
    client,
    db,
):
    retailer_one = Retailer(
        name="Create Category Owner",
        email="create-category-owner@bodh.local",
        phone="1818181818",
    )

    retailer_two = Retailer(
        name="Create Product Owner",
        email="create-product-owner@bodh.local",
        phone="1919191919",
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
        name="Retailer One Category",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer_two.id,
            "category_id": category.id,
            "name": "Cross Retailer Product",
            "sku": "API-CROSS-CREATE-001",
            "cost_price": "30.00",
            "selling_price": "45.00",
            "unit": "piece",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == (
        "Category does not belong to this retailer."
    )