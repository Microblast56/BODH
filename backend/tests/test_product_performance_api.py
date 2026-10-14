from datetime import date
from uuid import uuid4


def unique_suffix():
    return uuid4().hex[:8]


def create_retailer(client):
    suffix = unique_suffix()
    response = client.post(
        "/api/v1/retailers",
        json={
            "name": f"Performance Retailer {suffix}",
            "email": f"performance-{suffix}@example.com",
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
            "name": f"Performance Store {suffix}",
            "code": f"PF-{suffix}",
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
            "name": f"Performance Product {suffix}",
            "sku": f"PF-{suffix}",
            "cost_price": "5.00",
            "selling_price": "10.00",
            "tax_rate": "10.00",
            "unit": "piece",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_inventory(client, store_id, product_id, quantity=20):
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


def create_sale(client, retailer_id, store_id, product_id, quantity):
    return client.post(
        "/api/v1/transactions",
        json={
            "retailer_id": retailer_id,
            "store_id": store_id,
            "transaction_number": f"PF-{unique_suffix()}",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )


def test_product_performance_aggregates_completed_sales(client):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    create_inventory(client, store["id"], product["id"])

    first_sale = create_sale(
        client, retailer["id"], store["id"], product["id"], 2
    )
    second_sale = create_sale(
        client, retailer["id"], store["id"], product["id"], 3
    )

    assert first_sale.status_code == 201, first_sale.text
    assert second_sale.status_code == 201, second_sale.text

    response = client.get(
        "/api/v1/reports/product-performance",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["retailer_id"] == retailer["id"]
    assert data["total_products"] == 1
    assert len(data["products"]) == 1

    item = data["products"][0]
    assert item["product_id"] == product["id"]
    assert item["product_name"] == product["name"]
    assert item["sku"] == product["sku"]
    assert item["units_sold"] == 5
    assert item["transaction_count"] == 2
    assert item["total_revenue"] == "55.00"
    assert item["average_selling_value_per_unit"] == "11.00"


def test_product_performance_returns_empty_list_without_sales(client):
    response = client.get(
        "/api/v1/reports/product-performance"
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["products"] == []
    assert data["total_products"] == 0


def test_product_performance_rejects_invalid_date_range(client):
    response = client.get(
        "/api/v1/reports/product-performance",
        params={
            "date_from": date(2026, 10, 20).isoformat(),
            "date_to": date(2026, 10, 10).isoformat(),
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "date_from must be on or before date_to."
    )
