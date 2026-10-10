
from uuid import uuid4

import pytest


def unique_suffix():
    return uuid4().hex[:8]


def create_retailer(client):
    suffix = unique_suffix()
    response = client.post(
        "/api/v1/retailers",
        json={
            "name": f"Transaction Retailer {suffix}",
            "email": f"transaction-{suffix}@example.com",
            "phone": f"98{uuid4().int % 10**8:08d}",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_store(client, retailer_id):
    suffix = unique_suffix()
    response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer_id,
            "name": f"Transaction Store {suffix}",
            "code": f"TX-{suffix}",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "country": "India",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_product(client, retailer_id):
    suffix = unique_suffix()
    response = client.post(
        "/api/v1/products",
        json={
            "retailer_id": retailer_id,
            "name": f"Transaction Product {suffix}",
            "sku": f"TX-{suffix}",
            "cost_price": "5.00",
            "selling_price": "10.00",
            "tax_rate": "10.00",
            "unit": "piece",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_inventory(client, store_id, product_id, quantity=10):
    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store_id,
            "product_id": product_id,
            "quantity_on_hand": quantity,
            "reorder_level": 2,
            "reorder_quantity": 5,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_sale(client, retailer_id, store_id, product_id, number=None, quantity=2):
    return client.post(
        "/api/v1/transactions",
        json={
            "retailer_id": retailer_id,
            "store_id": store_id,
            "transaction_number": number or f"TX-{unique_suffix()}",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )


def make_sale_context(client, quantity=10):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    inventory = create_inventory(
        client, store["id"], product["id"], quantity
    )
    return retailer, store, product, inventory


def test_create_transaction_returns_sale_and_items(client):
    retailer, store, product, inventory = make_sale_context(client)

    response = create_sale(
        client, retailer["id"], store["id"], product["id"]
    )

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["retailer_id"] == retailer["id"]
    assert data["store_id"] == store["id"]
    assert data["status"] == "completed"
    assert data["subtotal"] == "20.00"
    assert data["tax_amount"] == "2.00"
    assert data["discount_amount"] == "0.00"
    assert data["total_amount"] == "22.00"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product["id"]
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["line_total"] == "22.00"

    inventory_response = client.get(
        f"/api/v1/inventories/{inventory['id']}"
    )
    assert inventory_response.status_code == 200
    assert inventory_response.json()["quantity_on_hand"] == 8


def test_get_transaction_returns_items(client):
    retailer, store, product, _ = make_sale_context(client)
    create_response = create_sale(
        client, retailer["id"], store["id"], product["id"]
    )
    assert create_response.status_code == 201, create_response.text

    transaction_id = create_response.json()["id"]
    response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == transaction_id
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product["id"]


def test_get_transaction_returns_404_when_missing(client):
    response = client.get("/api/v1/transactions/999999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found."


def test_list_transactions_supports_pagination(client):
    retailer, store, product, _ = make_sale_context(client)

    first = create_sale(
        client, retailer["id"], store["id"], product["id"]
    )
    second = create_sale(
        client, retailer["id"], store["id"], product["id"]
    )
    assert first.status_code == 201, first.text
    assert second.status_code == 201, second.text

    response = client.get(
        "/api/v1/transactions",
        params={"offset": 0, "limit": 1},
    )

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


def test_create_transaction_rejects_insufficient_stock(client):
    retailer, store, product, inventory = make_sale_context(
        client, quantity=1
    )

    response = create_sale(
        client,
        retailer["id"],
        store["id"],
        product["id"],
        quantity=2,
    )

    assert response.status_code == 409, response.text
    assert "Insufficient stock" in response.json()["detail"]

    inventory_response = client.get(
        f"/api/v1/inventories/{inventory['id']}"
    )
    assert inventory_response.status_code == 200
    assert inventory_response.json()["quantity_on_hand"] == 1


def test_create_transaction_rejects_missing_product(client):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])

    response = create_sale(
        client,
        retailer["id"],
        store["id"],
        999999999,
    )

    assert response.status_code == 404, response.text
    assert "Product" in response.json()["detail"]


def test_create_transaction_rejects_duplicate_number(client):
    retailer, store, product, _ = make_sale_context(client)
    number = f"TX-{unique_suffix()}"

    first = create_sale(
        client, retailer["id"], store["id"], product["id"], number
    )
    assert first.status_code == 201, first.text

    second = create_sale(
        client, retailer["id"], store["id"], product["id"], number
    )

    assert second.status_code == 409, second.text
    assert "transaction number already exists" in (
        second.json()["detail"]
    )


def test_create_transaction_rejects_empty_items(client):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])

    response = client.post(
        "/api/v1/transactions",
        json={
            "retailer_id": retailer["id"],
            "store_id": store["id"],
            "transaction_number": f"TX-{unique_suffix()}",
            "payment_method": "cash",
            "items": [],
        },
    )

    assert response.status_code == 422
