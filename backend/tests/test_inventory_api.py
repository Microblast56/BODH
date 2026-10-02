from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def unique_suffix():
    return uuid4().hex[:8]


def create_retailer():
    suffix = unique_suffix()

    response = client.post(
        "/api/v1/retailers",
        json={
            "name": f"Inventory Retailer {suffix}",
            "email": f"inventory-{suffix}@example.com",
            "phone": f"98{uuid4().int % 10**8:08d}",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_store(retailer_id):
    suffix = unique_suffix()

    response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer_id,
            "name": f"Inventory Store {suffix}",
            "code": f"INV-{suffix}",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "country": "India",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_product(retailer_id):
    suffix = unique_suffix()

    response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer_id,
            "name": f"Inventory Product {suffix}",
            "sku": f"INV-{suffix}",
            "cost_price": "100.00",
            "selling_price": "150.00",
            "unit": "piece",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_inventory(store_id, product_id, quantity=100):
    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store_id,
            "product_id": product_id,
            "quantity_on_hand": quantity,
            "reorder_level": 10,
            "reorder_quantity": 50,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_inventory():
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store["id"],
            "product_id": product["id"],
            "quantity_on_hand": 100,
            "reorder_level": 10,
            "reorder_quantity": 50,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["store_id"] == store["id"]
    assert data["product_id"] == product["id"]
    assert data["quantity_on_hand"] == 100
    assert data["reorder_level"] == 10
    assert data["reorder_quantity"] == 50
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_inventory_rejects_missing_store():
    retailer = create_retailer()
    product = create_product(retailer["id"])

    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": 999999,
            "product_id": product["id"],
            "quantity_on_hand": 100,
            "reorder_level": 10,
            "reorder_quantity": 50,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found."


def test_create_inventory_rejects_missing_product():
    retailer = create_retailer()
    store = create_store(retailer["id"])

    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store["id"],
            "product_id": 999999,
            "quantity_on_hand": 100,
            "reorder_level": 10,
            "reorder_quantity": 50,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_create_inventory_rejects_duplicate():
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    create_inventory(
        store["id"],
        product["id"],
    )

    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store["id"],
            "product_id": product["id"],
            "quantity_on_hand": 200,
            "reorder_level": 20,
            "reorder_quantity": 100,
        },
    )

    assert response.status_code == 409


def test_create_inventory_allows_same_product_for_different_store():
    retailer = create_retailer()

    store_one = create_store(retailer["id"])
    store_two = create_store(retailer["id"])

    product = create_product(retailer["id"])

    first = create_inventory(
        store_one["id"],
        product["id"],
    )

    second = create_inventory(
        store_two["id"],
        product["id"],
    )

    assert first["id"] != second["id"]
    assert first["product_id"] == second["product_id"]
    assert first["store_id"] != second["store_id"]


def test_get_inventory():
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    inventory = create_inventory(
        store["id"],
        product["id"],
    )

    response = client.get(
        f"/api/v1/inventories/{inventory['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == inventory["id"]
    assert data["store_id"] == store["id"]
    assert data["product_id"] == product["id"]


def test_get_inventory_returns_404_when_not_found():
    response = client.get(
        "/api/v1/inventories/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory not found."


def test_list_inventories():
    retailer = create_retailer()
    store = create_store(retailer["id"])

    product_one = create_product(retailer["id"])
    product_two = create_product(retailer["id"])

    create_inventory(
        store["id"],
        product_one["id"],
    )

    create_inventory(
        store["id"],
        product_two["id"],
    )

    response = client.get(
        "/api/v1/inventories"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_inventories_supports_pagination():
    retailer = create_retailer()
    store = create_store(retailer["id"])

    product_one = create_product(retailer["id"])
    product_two = create_product(retailer["id"])

    create_inventory(
        store["id"],
        product_one["id"],
    )

    create_inventory(
        store["id"],
        product_two["id"],
    )

    response = client.get(
        "/api/v1/inventories",
        params={
            "offset": 0,
            "limit": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_list_inventories_by_store():
    retailer = create_retailer()
    store = create_store(retailer["id"])

    product_one = create_product(retailer["id"])
    product_two = create_product(retailer["id"])

    create_inventory(
        store["id"],
        product_one["id"],
    )

    create_inventory(
        store["id"],
        product_two["id"],
    )

    response = client.get(
        f"/api/v1/inventories/store/{store['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    for inventory in data:
        assert inventory["store_id"] == store["id"]


def test_list_inventories_by_store_returns_404_when_store_not_found():
    response = client.get(
        "/api/v1/inventories/store/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Store not found."


def test_list_inventories_by_product():
    retailer = create_retailer()
    store = create_store(retailer["id"])

    product = create_product(retailer["id"])

    create_inventory(
        store["id"],
        product["id"],
    )

    response = client.get(
        f"/api/v1/inventories/product/{product['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["product_id"] == product["id"]


def test_list_inventories_by_product_returns_404_when_product_not_found():
    response = client.get(
        "/api/v1/inventories/product/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_update_inventory():
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    inventory = create_inventory(
        store["id"],
        product["id"],
        quantity=100,
    )

    response = client.patch(
        f"/api/v1/inventories/{inventory['id']}",
        json={
            "quantity_on_hand": 250,
            "reorder_level": 25,
            "reorder_quantity": 100,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == inventory["id"]
    assert data["quantity_on_hand"] == 250
    assert data["reorder_level"] == 25
    assert data["reorder_quantity"] == 100


def test_update_inventory_returns_404_when_not_found():
    response = client.patch(
        "/api/v1/inventories/999999",
        json={
            "quantity_on_hand": 100,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory not found."


def test_delete_inventory():
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    inventory = create_inventory(
        store["id"],
        product["id"],
    )

    response = client.delete(
        f"/api/v1/inventories/{inventory['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/inventories/{inventory['id']}"
    )

    assert get_response.status_code == 404


def test_delete_inventory_returns_404_when_not_found():
    response = client.delete(
        "/api/v1/inventories/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory not found."