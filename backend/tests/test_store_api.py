def create_retailer(db, name="Test Retailer"):
    from app.models import Retailer

    retailer = Retailer(
        name=name,
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def test_create_store_api(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Test Store",
            "code": "STORE001",
            "address_line1": "123 Test Street",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "postal_code": "226001",
            "country": "India",
            "phone": "1111111111",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Test Store"
    assert data["code"] == "STORE001"
    assert data["address_line1"] == "123 Test Street"
    assert data["city"] == "Lucknow"
    assert data["state"] == "Uttar Pradesh"
    assert data["postal_code"] == "226001"
    assert data["country"] == "India"
    assert data["phone"] == "1111111111"
    assert data["is_active"] is True


def test_create_store_api_rejects_missing_retailer(client):
    response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": 999999,
            "name": "Invalid Store",
            "code": "STORE001",
        },
    )

    assert response.status_code == 404


def test_create_store_api_rejects_duplicate_code(client, db):
    retailer = create_retailer(db)

    payload = {
        "retailer_id": retailer.id,
        "name": "First Store",
        "code": "STORE001",
    }

    first_response = client.post(
        "/api/v1/stores",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Second Store",
            "code": "STORE001",
        },
    )

    assert second_response.status_code == 409


def test_create_store_api_allows_same_code_for_different_retailers(
    client,
    db,
):
    first_retailer = create_retailer(
        db,
        name="First Retailer",
    )

    second_retailer = create_retailer(
        db,
        name="Second Retailer",
    )

    first_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": first_retailer.id,
            "name": "First Store",
            "code": "STORE001",
        },
    )

    second_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": second_retailer.id,
            "name": "Second Store",
            "code": "STORE001",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201


def test_get_store_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Get Store",
            "code": "GET001",
        },
    )

    assert create_response.status_code == 201

    store_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/stores/{store_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == store_id
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Get Store"
    assert data["code"] == "GET001"


def test_get_store_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/stores/999999",
    )

    assert response.status_code == 404


def test_list_stores_api(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "First Store",
            "code": "STORE001",
        },
    )

    client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Second Store",
            "code": "STORE002",
        },
    )

    response = client.get(
        "/api/v1/stores",
    )

    assert response.status_code == 200

    data = response.json()

    names = [store["name"] for store in data]

    assert "First Store" in names
    assert "Second Store" in names


def test_list_stores_api_supports_pagination(client, db):
    retailer = create_retailer(db)

    client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "First Store",
            "code": "STORE001",
        },
    )

    client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Second Store",
            "code": "STORE002",
        },
    )

    response = client.get(
        "/api/v1/stores?offset=1&limit=1",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_update_store_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Original Store",
            "code": "STORE001",
            "phone": "3333333333",
        },
    )

    assert create_response.status_code == 201

    store_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/stores/{store_id}",
        json={
            "name": "Updated Store",
            "phone": "4444444444",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == store_id
    assert data["name"] == "Updated Store"
    assert data["code"] == "STORE001"
    assert data["phone"] == "4444444444"


def test_update_store_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/stores/999999",
        json={
            "name": "Updated Store",
        },
    )

    assert response.status_code == 404


def test_update_store_api_rejects_duplicate_code(client, db):
    retailer = create_retailer(db)

    first_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "First Store",
            "code": "STORE001",
        },
    )

    second_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Second Store",
            "code": "STORE002",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    second_store_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/stores/{second_store_id}",
        json={
            "code": "STORE001",
        },
    )

    assert response.status_code == 409


def test_update_store_api_allows_same_code(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Original Store",
            "code": "STORE001",
        },
    )

    assert create_response.status_code == 201

    store_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/stores/{store_id}",
        json={
            "name": "Updated Store",
            "code": "STORE001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Store"
    assert data["code"] == "STORE001"


def test_delete_store_api(client, db):
    retailer = create_retailer(db)

    create_response = client.post(
        "/api/v1/stores",
        json={
            "retailer_id": retailer.id,
            "name": "Delete Store",
            "code": "DELETE001",
        },
    )

    assert create_response.status_code == 201

    store_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/stores/{store_id}",
    )

    assert response.status_code == 204


def test_delete_store_api_returns_404_when_not_found(client):
    response = client.delete(
        "/api/v1/stores/999999",
    )

    assert response.status_code == 404