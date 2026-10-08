def create_retailer(db, name="Test Retailer"):
    from app.models import Retailer

    retailer = Retailer(
        name=name,
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def test_create_employee_api(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1111111111",
            "role": "Manager",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "1111111111"
    assert data["role"] == "Manager"
    assert data["is_active"] is True


def test_create_employee_api_without_email(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "John Doe",
            "role": "Manager",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "John Doe"
    assert data["email"] is None


def test_create_employee_api_rejects_missing_retailer(client):
    response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": 999999,
            "name": "Invalid Employee",
            "role": "Manager",
        },
    )

    assert response.status_code == 404


def test_create_employee_api_rejects_duplicate_email(client, db):
    retailer = create_retailer(db)

    payload = {
        "retailer_id": retailer.id,
        "name": "First Employee",
        "email": "duplicate@example.com",
        "role": "Manager",
    }

    first_response = client.post(
        "/api/v1/employees",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/employees",
        json={
            **payload,
            "name": "Second Employee",
        },
    )

    assert second_response.status_code == 409


def test_get_employee_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Get Employee",
            "role": "Cashier",
        },
    )

    employee_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/employees/{employee_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == employee_id
    assert data["name"] == "Get Employee"
    assert data["role"] == "Cashier"


def test_get_employee_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/employees/999999",
    )

    assert response.status_code == 404


def test_list_employees_api(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "First Employee",
            "role": "Cashier",
        },
    )

    client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Second Employee",
            "role": "Manager",
        },
    )

    response = client.get(
        "/api/v1/employees",
    )

    assert response.status_code == 200

    data = response.json()

    names = [employee["name"] for employee in data]

    assert "First Employee" in names
    assert "Second Employee" in names


def test_list_employees_api_supports_pagination(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "First Employee",
            "role": "Cashier",
        },
    )

    client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Second Employee",
            "role": "Manager",
        },
    )

    response = client.get(
        "/api/v1/employees?offset=1&limit=1",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_update_employee_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Original Employee",
            "email": "original@example.com",
            "phone": "3333333333",
            "role": "Cashier",
        },
    )

    employee_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{employee_id}",
        json={
            "name": "Updated Employee",
            "phone": "4444444444",
            "role": "Manager",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == employee_id
    assert data["name"] == "Updated Employee"
    assert data["email"] == "original@example.com"
    assert data["phone"] == "4444444444"
    assert data["role"] == "Manager"


def test_update_employee_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/employees/999999",
        json={
            "name": "Updated Employee",
        },
    )

    assert response.status_code == 404


def test_update_employee_api_rejects_duplicate_email(client, db):
    retailer = create_retailer(db)

    first_response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "First Employee",
            "email": "first@example.com",
            "role": "Cashier",
        },
    )

    second_response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Second Employee",
            "email": "second@example.com",
            "role": "Manager",
        },
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/employees/{second_id}",
        json={
            "email": "first@example.com",
        },
    )

    assert response.status_code == 409


def test_delete_employee_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/employees",
        json={
            "retailer_id": retailer.id,
            "name": "Delete Employee",
            "role": "Cashier",
        },
    )

    employee_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/employees/{employee_id}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/employees/{employee_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_delete_employee_api_returns_404_when_not_found(client):
    response = client.delete(
        "/api/v1/employees/999999",
    )

    assert response.status_code == 404
