def create_retailer(db, name="Test Retailer"):
    from app.models import Retailer

    retailer = Retailer(
        name=name,
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def test_create_supplier_api(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Test Supplier",
            "contact_person": "John Doe",
            "email": "supplier@example.com",
            "phone": "1111111111",
            "address": "Test Address",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Test Supplier"
    assert data["contact_person"] == "John Doe"
    assert data["email"] == "supplier@example.com"
    assert data["phone"] == "1111111111"
    assert data["address"] == "Test Address"
    assert data["is_active"] is True


def test_create_supplier_api_rejects_missing_retailer(client):
    response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": 999999,
            "name": "Invalid Supplier",
        },
    )

    assert response.status_code == 404


def test_create_supplier_api_rejects_duplicate_name(client, db):
    retailer = create_retailer(db)

    payload = {
        "retailer_id": retailer.id,
        "name": "Duplicate Supplier",
    }

    first_response = client.post(
        "/api/v1/suppliers",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/suppliers",
        json=payload,
    )

    assert second_response.status_code == 409


def test_get_supplier_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Get Supplier",
        },
    )

    supplier_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/suppliers/{supplier_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == supplier_id
    assert data["name"] == "Get Supplier"


def test_get_supplier_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/suppliers/999999",
    )

    assert response.status_code == 404


def test_list_suppliers_api(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "First Supplier",
        },
    )

    client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Second Supplier",
        },
    )

    response = client.get(
        "/api/v1/suppliers",
    )

    assert response.status_code == 200

    data = response.json()

    names = [supplier["name"] for supplier in data]

    assert "First Supplier" in names
    assert "Second Supplier" in names


def test_list_suppliers_api_supports_pagination(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "First Supplier",
        },
    )

    client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Second Supplier",
        },
    )

    response = client.get(
        "/api/v1/suppliers?offset=1&limit=1",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_update_supplier_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Original Supplier",
            "email": "original@example.com",
            "phone": "3333333333",
        },
    )

    supplier_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/suppliers/{supplier_id}",
        json={
            "name": "Updated Supplier",
            "phone": "4444444444",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == supplier_id
    assert data["name"] == "Updated Supplier"
    assert data["email"] == "original@example.com"
    assert data["phone"] == "4444444444"


def test_update_supplier_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/suppliers/999999",
        json={
            "name": "Updated Supplier",
        },
    )

    assert response.status_code == 404


def test_update_supplier_api_rejects_duplicate_name(client, db):
    retailer = create_retailer(db)

    first_response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "First Supplier",
        },
    )

    second_response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Second Supplier",
        },
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/suppliers/{second_id}",
        json={
            "name": "First Supplier",
        },
    )

    assert response.status_code == 409


def test_delete_supplier_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/suppliers",
        json={
            "retailer_id": retailer.id,
            "name": "Delete Supplier",
        },
    )

    supplier_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/suppliers/{supplier_id}",
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/suppliers/{supplier_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_delete_supplier_api_returns_404_when_not_found(client):
    response = client.delete(
        "/api/v1/suppliers/999999",
    )

    assert response.status_code == 404