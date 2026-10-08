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
            "name": f"Stock Retailer {suffix}",
            "email": f"stock-{suffix}@example.com",
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
            "name": f"Stock Store {suffix}",
            "code": f"STK-{suffix}",
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
            "name": f"Stock Product {suffix}",
            "sku": f"STK-{suffix}",
            "cost_price": "100.00",
            "selling_price": "150.00",
            "unit": "piece",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_inventory(
    store_id,
    product_id,
    quantity=100,
):
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


def create_test_inventory(quantity=100):
    retailer = create_retailer()
    store = create_store(retailer["id"])
    product = create_product(retailer["id"])

    inventory = create_inventory(
        store["id"],
        product["id"],
        quantity,
    )

    return retailer, store, product, inventory


def test_stock_in_api():
    _, _, _, inventory = create_test_inventory(100)

    response = client.post(
        f"/api/v1/inventories/{inventory['id']}/stock-in",
        json={
            "quantity": 25,
            "reference_type": "purchase",
            "reference_id": 100,
            "notes": "Test stock in",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity_on_hand"] == 125
    assert data["last_restocked_at"] is not None


def test_stock_out_api():
    _, _, _, inventory = create_test_inventory(100)

    response = client.post(
        f"/api/v1/inventories/{inventory['id']}/stock-out",
        json={
            "quantity": 30,
            "reference_type": "sale",
            "reference_id": 200,
            "notes": "Test stock out",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity_on_hand"] == 70


def test_stock_out_api_rejects_insufficient_stock():
    _, _, _, inventory = create_test_inventory(5)

    response = client.post(
        f"/api/v1/inventories/{inventory['id']}/stock-out",
        json={
            "quantity": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == "Insufficient stock."


def test_stock_in_api_returns_404_for_missing_inventory():
    response = client.post(
        "/api/v1/inventories/999999/stock-in",
        json={
            "quantity": 10,
        },
    )

    assert response.status_code == 404


def test_stock_out_api_returns_404_for_missing_inventory():
    response = client.post(
        "/api/v1/inventories/999999/stock-out",
        json={
            "quantity": 10,
        },
    )

    assert response.status_code == 404


def test_stock_in_api_rejects_zero_quantity():
    _, _, _, inventory = create_test_inventory(100)

    response = client.post(
        f"/api/v1/inventories/{inventory['id']}/stock-in",
        json={
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_stock_out_api_rejects_zero_quantity():
    _, _, _, inventory = create_test_inventory(100)

    response = client.post(
        f"/api/v1/inventories/{inventory['id']}/stock-out",
        json={
            "quantity": 0,
        },
    )

    assert response.status_code == 422
