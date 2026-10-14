from datetime import date, datetime, time, timedelta, timezone
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
            "name": f"Sales Report Retailer {suffix}",
            "email": f"sales-report-{suffix}@example.com",
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
            "name": f"Sales Report Store {suffix}",
            "code": f"SR-{suffix}",
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
            "name": f"Sales Report Product {suffix}",
            "sku": f"SR-{suffix}",
            "cost_price": "5.00",
            "selling_price": "10.00",
            "tax_rate": "10.00",
            "unit": "piece",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_inventory(client, store_id, product_id, quantity=30):
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
    response = client.post(
        "/api/v1/transactions",
        json={
            "retailer_id": retailer_id,
            "store_id": store_id,
            "transaction_number": f"SR-{unique_suffix()}",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_sales_summary_aggregates_completed_sales(client):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    create_inventory(client, store["id"], product["id"])

    create_sale(client, retailer["id"], store["id"], product["id"], 2)
    create_sale(client, retailer["id"], store["id"], product["id"], 3)

    response = client.get(
        "/api/v1/reports/sales-summary",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["retailer_id"] == retailer["id"]
    assert data["store_id"] is None
    assert data["total_revenue"] == "55.00"
    assert data["transaction_count"] == 2
    assert data["average_transaction_value"] == "27.50"
    assert data["units_sold"] == 5


def test_sales_summary_excludes_non_completed_transactions(client, db):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    create_inventory(client, store["id"], product["id"])

    create_sale(client, retailer["id"], store["id"], product["id"], 2)

    pending = Transaction(
        retailer_id=retailer["id"],
        store_id=store["id"],
        transaction_number=f"SR-PENDING-{unique_suffix()}",
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
        "/api/v1/reports/sales-summary",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_revenue"] == "22.00"
    assert data["transaction_count"] == 1
    assert data["average_transaction_value"] == "22.00"
    assert data["units_sold"] == 2


def test_sales_summary_filters_by_store(client):
    retailer = create_retailer(client)
    first_store = create_store(client, retailer["id"])
    second_store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])

    create_inventory(client, first_store["id"], product["id"])
    create_inventory(client, second_store["id"], product["id"])

    create_sale(
        client, retailer["id"], first_store["id"], product["id"], 2
    )
    create_sale(
        client, retailer["id"], second_store["id"], product["id"], 3
    )

    response = client.get(
        "/api/v1/reports/sales-summary",
        params={"store_id": first_store["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["store_id"] == first_store["id"]
    assert data["total_revenue"] == "22.00"
    assert data["transaction_count"] == 1
    assert data["units_sold"] == 2


def test_sales_summary_filters_by_date_range(client, db):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    create_inventory(client, store["id"], product["id"])

    create_sale(client, retailer["id"], store["id"], product["id"], 2)

    today = datetime.now(timezone.utc).date()
    yesterday = today - timedelta(days=1)

    response = client.get(
        "/api/v1/reports/sales-summary",
        params={
            "retailer_id": retailer["id"],
            "date_from": today.isoformat(),
            "date_to": today.isoformat(),
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["date_from"] == today.isoformat()
    assert data["date_to"] == today.isoformat()
    assert data["transaction_count"] == 1
    assert data["total_revenue"] == "22.00"

    response_before_range = client.get(
        "/api/v1/reports/sales-summary",
        params={
            "retailer_id": retailer["id"],
            "date_from": yesterday.isoformat(),
            "date_to": yesterday.isoformat(),
        },
    )

    assert response_before_range.status_code == 200
    assert response_before_range.json()["transaction_count"] == 0
    assert response_before_range.json()["units_sold"] == 0


def test_sales_summary_returns_zeroes_when_no_sales_match(client):
    response = client.get(
        "/api/v1/reports/sales-summary",
        params={"retailer_id": 999999999},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_revenue"] == "0.00"
    assert data["transaction_count"] == 0
    assert data["average_transaction_value"] == "0.00"
    assert data["units_sold"] == 0


def test_sales_summary_rejects_invalid_date_range(client):
    response = client.get(
        "/api/v1/reports/sales-summary",
        params={
            "date_from": date(2026, 10, 20).isoformat(),
            "date_to": date(2026, 10, 10).isoformat(),
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "date_from must be on or before date_to."
    )
