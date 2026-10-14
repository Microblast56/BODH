from uuid import uuid4


def unique_suffix():
    return uuid4().hex[:8]


def create_retailer(client):
    suffix = unique_suffix()
    response = client.post(
        "/api/v1/retailers",
        json={
            "name": f"Low Stock Retailer {suffix}",
            "email": f"lowstock-{suffix}@example.com",
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
            "name": f"Low Stock Store {suffix}",
            "code": f"LS-{suffix}",
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
            "name": f"Low Stock Product {suffix}",
            "sku": f"LS-{suffix}",
            "cost_price": "5.00",
            "selling_price": "10.00",
            "tax_rate": "10.00",
            "unit": "piece",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_inventory(
    client,
    store_id,
    product_id,
    quantity,
    reorder_level=5,
    reorder_quantity=10,
):
    response = client.post(
        "/api/v1/inventories",
        json={
            "store_id": store_id,
            "product_id": product_id,
            "quantity_on_hand": quantity,
            "reorder_level": reorder_level,
            "reorder_quantity": reorder_quantity,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_inventory_setup(client, quantity, reorder_level=5):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])
    inventory = create_inventory(
        client,
        store["id"],
        product["id"],
        quantity=quantity,
        reorder_level=reorder_level,
    )
    return retailer, store, product, inventory


def test_low_stock_report_includes_items_below_reorder_level(client):
    retailer, store, product, inventory = create_inventory_setup(
        client,
        quantity=3,
        reorder_level=5,
    )

    response = client.get(
        "/api/v1/reports/low-stock",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["retailer_id"] == retailer["id"]
    assert data["total_items"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["inventory_id"] == inventory["id"]
    assert item["store_id"] == store["id"]
    assert item["store_name"] == store["name"]
    assert item["product_id"] == product["id"]
    assert item["product_name"] == product["name"]
    assert item["sku"] == product["sku"]
    assert item["quantity_on_hand"] == 3
    assert item["reorder_level"] == 5
    assert item["reorder_quantity"] == 10
    assert item["shortage_quantity"] == 2


def test_low_stock_report_includes_quantity_equal_to_reorder_level(client):
    retailer, _, _, _ = create_inventory_setup(
        client,
        quantity=5,
        reorder_level=5,
    )

    response = client.get(
        "/api/v1/reports/low-stock",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_items"] == 1
    assert data["items"][0]["quantity_on_hand"] == 5
    assert data["items"][0]["shortage_quantity"] == 0


def test_low_stock_report_excludes_items_above_reorder_level(client):
    retailer, _, _, _ = create_inventory_setup(
        client,
        quantity=6,
        reorder_level=5,
    )

    response = client.get(
        "/api/v1/reports/low-stock",
        params={"retailer_id": retailer["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_items"] == 0
    assert data["items"] == []


def test_low_stock_report_filters_by_store(client):
    retailer = create_retailer(client)
    matching_store = create_store(client, retailer["id"])
    other_store = create_store(client, retailer["id"])

    matching_product = create_product(client, retailer["id"])
    other_product = create_product(client, retailer["id"])

    create_inventory(
        client,
        matching_store["id"],
        matching_product["id"],
        quantity=1,
        reorder_level=5,
    )
    create_inventory(
        client,
        other_store["id"],
        other_product["id"],
        quantity=2,
        reorder_level=5,
    )

    response = client.get(
        "/api/v1/reports/low-stock",
        params={"store_id": matching_store["id"]},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["store_id"] == matching_store["id"]
    assert data["total_items"] == 1
    assert data["items"][0]["store_id"] == matching_store["id"]


def test_low_stock_report_returns_empty_list_without_low_stock(client):
    response = client.get(
        "/api/v1/reports/low-stock",
        params={"retailer_id": 999999999},
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["total_items"] == 0
    assert data["items"] == []


def test_low_stock_report_rejects_invalid_ids(client):
    for params in (
        {"retailer_id": 0},
        {"store_id": 0},
    ):
        response = client.get(
            "/api/v1/reports/low-stock",
            params=params,
        )
        assert response.status_code == 422, response.text

def test_low_stock_report_does_not_change_inventory_quantity(client):
    retailer = create_retailer(client)
    store = create_store(client, retailer["id"])
    product = create_product(client, retailer["id"])

    inventory = create_inventory(
        client,
        store["id"],
        product["id"],
        quantity=2,
        reorder_level=5,
    )

    inventory_url = f"/api/v1/inventories/{inventory['id']}"

    before_response = client.get(inventory_url)
    assert before_response.status_code == 200, before_response.text
    quantity_before = before_response.json()["quantity_on_hand"]

    report_response = client.get(
        "/api/v1/reports/low-stock",
        params={"store_id": store["id"]},
    )
    assert report_response.status_code == 200, report_response.text
    assert report_response.json()["total_items"] == 1

    after_response = client.get(inventory_url)
    assert after_response.status_code == 200, after_response.text
    quantity_after = after_response.json()["quantity_on_hand"]

    assert quantity_after == quantity_before == 2