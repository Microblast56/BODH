from app.models import (
    Employee,
    Inventory,
    Product,
    Retailer,
    StockMovement,
    Store,
)


def create_retailer(db):
    retailer = Retailer(
        name="Test Retailer",
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def create_store(db, retailer_id):
    store = Store(
        retailer_id=retailer_id,
        name="Test Store",
        code="TEST-STORE",
        address_line1="Test Address",
        city="Lucknow",
        state="Uttar Pradesh",
        postal_code="226001",
        country="India",
    )

    db.add(store)
    db.commit()
    db.refresh(store)

    return store


def create_product(db, retailer_id):
    product = Product(
        retailer_id=retailer_id,
        name="Test Product",
        sku="TEST-SKU-001",
        cost_price=100,
        selling_price=150,
        unit="piece",
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def create_inventory(db):
    retailer = create_retailer(db)
    store = create_store(db, retailer.id)
    product = create_product(db, retailer.id)

    inventory = Inventory(
        store_id=store.id,
        product_id=product.id,
        quantity_on_hand=100,
        reorder_level=10,
    )

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return inventory


def create_employee(db):
    retailer = create_retailer(db)
    store = create_store(db, retailer.id)

    employee = Employee(
        retailer_id=retailer.id,
        store_id=store.id,
        name="John",
        role="Manager",
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def create_stock_movement(db, inventory_id, employee_id=None):
    movement = StockMovement(
        inventory_id=inventory_id,
        employee_id=employee_id,
        movement_type="sale",
        quantity_change=-5,
        notes="Test movement",
    )

    db.add(movement)
    db.commit()
    db.refresh(movement)

    return movement


def test_create_stock_movement_api(client, db):
    inventory = create_inventory(db)
    employee = create_employee(db)

    response = client.post(
        "/api/v1/stock-movements",
        json={
            "inventory_id": inventory.id,
            "employee_id": employee.id,
            "movement_type": "sale",
            "quantity_change": -5,
            "notes": "Test sale",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["inventory_id"] == inventory.id
    assert data["employee_id"] == employee.id
    assert data["movement_type"] == "sale"
    assert data["quantity_change"] == -5
    assert data["notes"] == "Test sale"


def test_create_stock_movement_api_without_employee(client, db):
    inventory = create_inventory(db)

    response = client.post(
        "/api/v1/stock-movements",
        json={
            "inventory_id": inventory.id,
            "movement_type": "adjustment",
            "quantity_change": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["inventory_id"] == inventory.id
    assert data["employee_id"] is None
    assert data["movement_type"] == "adjustment"
    assert data["quantity_change"] == 10


def test_create_stock_movement_api_rejects_missing_inventory(client):
    response = client.post(
        "/api/v1/stock-movements",
        json={
            "inventory_id": 999999,
            "movement_type": "sale",
            "quantity_change": -5,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory not found."


def test_create_stock_movement_api_rejects_missing_employee(client, db):
    inventory = create_inventory(db)

    response = client.post(
        "/api/v1/stock-movements",
        json={
            "inventory_id": inventory.id,
            "employee_id": 999999,
            "movement_type": "sale",
            "quantity_change": -5,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_get_stock_movement_api(client, db):
    inventory = create_inventory(db)

    movement = create_stock_movement(
        db,
        inventory.id,
    )

    response = client.get(
        f"/api/v1/stock-movements/{movement.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == movement.id
    assert data["inventory_id"] == inventory.id
    assert data["movement_type"] == "sale"
    assert data["quantity_change"] == -5


def test_get_stock_movement_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/stock-movements/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock movement not found."


def test_list_stock_movements_api(client, db):
    inventory = create_inventory(db)

    create_stock_movement(
        db,
        inventory.id,
    )

    movement = StockMovement(
        inventory_id=inventory.id,
        movement_type="restock",
        quantity_change=20,
    )

    db.add(movement)
    db.commit()

    response = client.get(
        "/api/v1/stock-movements"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_list_stock_movements_api_supports_pagination(client, db):
    inventory = create_inventory(db)

    for quantity in [-5, 10, 20]:
        db.add(
            StockMovement(
                inventory_id=inventory.id,
                movement_type="adjustment",
                quantity_change=quantity,
            )
        )

    db.commit()

    response = client.get(
        "/api/v1/stock-movements?offset=1&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_list_stock_movements_api_by_inventory(client, db):
    inventory = create_inventory(db)

    create_stock_movement(
        db,
        inventory.id,
    )

    response = client.get(
        f"/api/v1/stock-movements/inventory/{inventory.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["inventory_id"] == inventory.id


def test_list_stock_movements_api_by_inventory_returns_404_when_not_found(
    client,
):
    response = client.get(
        "/api/v1/stock-movements/inventory/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Inventory not found."


def test_list_stock_movements_api_by_employee(client, db):
    inventory = create_inventory(db)
    employee = create_employee(db)

    create_stock_movement(
        db,
        inventory.id,
        employee.id,
    )

    response = client.get(
        f"/api/v1/stock-movements/employee/{employee.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["employee_id"] == employee.id


def test_list_stock_movements_api_by_employee_returns_404_when_not_found(
    client,
):
    response = client.get(
        "/api/v1/stock-movements/employee/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_update_stock_movement_api(client, db):
    inventory = create_inventory(db)

    movement = create_stock_movement(
        db,
        inventory.id,
    )

    response = client.patch(
        f"/api/v1/stock-movements/{movement.id}",
        json={
            "movement_type": "return",
            "quantity_change": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["movement_type"] == "return"
    assert data["quantity_change"] == 5


def test_update_stock_movement_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/stock-movements/999999",
        json={
            "movement_type": "return",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock movement not found."


def test_update_stock_movement_api_rejects_missing_employee(client, db):
    inventory = create_inventory(db)

    movement = create_stock_movement(
        db,
        inventory.id,
    )

    response = client.patch(
        f"/api/v1/stock-movements/{movement.id}",
        json={
            "employee_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found."


def test_delete_stock_movement_api(client, db):
    inventory = create_inventory(db)

    movement = create_stock_movement(
        db,
        inventory.id,
    )

    response = client.delete(
        f"/api/v1/stock-movements/{movement.id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/stock-movements/{movement.id}"
    )

    assert response.status_code == 404


def test_delete_stock_movement_api_returns_404_when_not_found(client):
    response = client.delete(
        "/api/v1/stock-movements/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock movement not found."