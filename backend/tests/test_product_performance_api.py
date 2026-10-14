from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from app.models import Transaction, TransactionItem


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


def test_product_performance_excludes_pending_transactions(client, db):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    create_inventory(client, store["id"], product["id"])

    sale = create_sale(
        client, retailer["id"], store["id"], product["id"], 2
    )
    assert sale.status_code == 201, sale.text

    pending = Transaction(
        retailer_id=retailer["id"],
        store_id=store["id"],
        transaction_number=f"PF-PENDING-{unique_suffix()}",
        status="pending",
        payment_method="cash",
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("10.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("110.00"),
    )
    db.add(pending)
    db.flush()

    db.add(
        TransactionItem(
            transaction_id=pending.id,
            product_id=product["id"],
            quantity=10,
            unit_price=Decimal("10.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("10.00"),
            line_total=Decimal("110.00"),
        )
    )
    db.flush()

    response = client.get(
        "/api/v1/reports/product-performance",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_products"] == 1
    item = data["products"][0]
    assert item["product_id"] == product["id"]
    assert item["units_sold"] == 2
    assert item["transaction_count"] == 1
    assert item["total_revenue"] == "22.00"
    assert item["average_selling_value_per_unit"] == "11.00"


def test_product_performance_filters_by_store_and_date(client):
    retailer = create_retailer(client)
    first_store = create_store(client, retailer["id"])
    second_store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])

    create_inventory(client, first_store["id"], product["id"])
    create_inventory(client, second_store["id"], product["id"])

    first_sale = create_sale(
        client, retailer["id"], first_store["id"], product["id"], 2
    )
    second_sale = create_sale(
        client, retailer["id"], second_store["id"], product["id"], 3
    )

    assert first_sale.status_code == 201, first_sale.text
    assert second_sale.status_code == 201, second_sale.text

    today = datetime.now(timezone.utc).date()

    response = client.get(
        "/api/v1/reports/product-performance",
        params={
            "retailer_id": retailer["id"],
            "store_id": first_store["id"],
            "date_from": today.isoformat(),
            "date_to": today.isoformat(),
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["store_id"] == first_store["id"]
    assert data["date_from"] == today.isoformat()
    assert data["date_to"] == today.isoformat()
    assert data["total_products"] == 1

    item = data["products"][0]
    assert item["product_id"] == product["id"]
    assert item["units_sold"] == 2
    assert item["transaction_count"] == 1
    assert item["total_revenue"] == "22.00"
