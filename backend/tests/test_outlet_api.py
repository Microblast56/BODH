from app.models import Outlet, Restaurant


def create_restaurant(
    db,
    name="Test Restaurant",
    email="test@example.com",
):
    restaurant = Restaurant(
        name=name,
        email=email,
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant


def test_create_outlet_api(client, db):
    restaurant = create_restaurant(db)

    payload = {
        "restaurant_id": restaurant.id,
        "name": "Main Outlet",
        "code": "MAIN",
        "address_line1": "123 Main Street",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "postal_code": "226001",
        "country": "India",
        "phone": "1111111111",
    }

    response = client.post(
        "/api/v1/outlets",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["restaurant_id"] == restaurant.id
    assert data["name"] == "Main Outlet"
    assert data["code"] == "MAIN"
    assert data["city"] == "Lucknow"
    assert data["state"] == "Uttar Pradesh"
    assert data["is_active"] is True


def test_create_outlet_api_rejects_missing_restaurant(client):
    payload = {
        "restaurant_id": 999999,
        "name": "Main Outlet",
        "code": "MAIN",
    }

    response = client.post(
        "/api/v1/outlets",
        json=payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found."


def test_create_outlet_api_rejects_duplicate_code(client, db):
    restaurant = create_restaurant(db)

    first_payload = {
        "restaurant_id": restaurant.id,
        "name": "First Outlet",
        "code": "MAIN",
    }

    second_payload = {
        "restaurant_id": restaurant.id,
        "name": "Second Outlet",
        "code": "MAIN",
    }

    first_response = client.post(
        "/api/v1/outlets",
        json=first_payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/outlets",
        json=second_payload,
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "Outlet with this code already exists for this restaurant."
    )


def test_get_outlet_api(client, db):
    restaurant = create_restaurant(db)

    create_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "GET Outlet",
            "code": "GET",
        },
    )

    assert create_response.status_code == 201

    outlet_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/outlets/{outlet_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == outlet_id
    assert data["restaurant_id"] == restaurant.id
    assert data["name"] == "GET Outlet"
    assert data["code"] == "GET"


def test_get_outlet_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/outlets/999999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Outlet not found."


def test_list_outlets_api(client, db):
    restaurant = create_restaurant(db)

    client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "First Outlet",
            "code": "FIRST",
        },
    )

    client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "Second Outlet",
            "code": "SECOND",
        },
    )

    response = client.get(
        "/api/v1/outlets",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 2

    codes = [outlet["code"] for outlet in data]

    assert "FIRST" in codes
    assert "SECOND" in codes


def test_list_outlets_api_filters_by_restaurant(client, db):
    first_restaurant = create_restaurant(
        db,
        name="First Restaurant",
        email="first@example.com",
    )

    second_restaurant = create_restaurant(
        db,
        name="Second Restaurant",
        email="second@example.com",
    )

    first_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": first_restaurant.id,
            "name": "First Outlet",
            "code": "FIRST",
        },
    )

    second_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": second_restaurant.id,
            "name": "Second Outlet",
            "code": "SECOND",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get(
        "/api/v1/outlets",
        params={
            "restaurant_id": first_restaurant.id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["restaurant_id"] == first_restaurant.id
    assert data[0]["code"] == "FIRST"


def test_update_outlet_api(client, db):
    restaurant = create_restaurant(db)

    create_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "Original Outlet",
            "code": "ORIGINAL",
            "phone": "1111111111",
        },
    )

    assert create_response.status_code == 201

    outlet_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/outlets/{outlet_id}",
        json={
            "name": "Updated Outlet",
            "code": "UPDATED",
            "phone": "2222222222",
            "city": "Lucknow",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == outlet_id
    assert data["name"] == "Updated Outlet"
    assert data["code"] == "UPDATED"
    assert data["phone"] == "2222222222"
    assert data["city"] == "Lucknow"
    assert data["restaurant_id"] == restaurant.id


def test_update_outlet_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/outlets/999999",
        json={
            "name": "Updated Outlet",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Outlet not found."


def test_update_outlet_api_rejects_duplicate_code(client, db):
    restaurant = create_restaurant(db)

    first_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "First Outlet",
            "code": "FIRST",
        },
    )

    second_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "Second Outlet",
            "code": "SECOND",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/outlets/{second_id}",
        json={
            "code": "FIRST",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Outlet with this code already exists for this restaurant."
    )

    # Make sure the original outlet was not modified.
    get_response = client.get(
        f"/api/v1/outlets/{first_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["code"] == "FIRST"


def test_delete_outlet_api(client, db):
    restaurant = create_restaurant(db)

    create_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "Delete Outlet",
            "code": "DELETE",
        },
    )

    assert create_response.status_code == 201

    outlet_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/outlets/{outlet_id}",
    )

    assert response.status_code == 204
    assert response.content == b""

    outlet = (
        db.query(Outlet)
        .filter(Outlet.id == outlet_id)
        .first()
    )

    assert outlet is not None
    assert outlet.is_active is False


def test_delete_outlet_api_returns_404_when_not_found(client):
    response = client.delete(
        "/api/v1/outlets/999999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Outlet not found."

def test_delete_outlet_api_returns_404_after_deletion(client, db):
    # Arrange: create a restaurant for the outlet.
    restaurant = create_restaurant(
        db,
        name="Delete Test Restaurant",
        email="delete-test-restaurant@example.com",
    )

    create_response = client.post(
        "/api/v1/outlets",
        json={
            "restaurant_id": restaurant.id,
            "name": "Delete Test Outlet",
            "code": "DELETE-TEST",
        },
    )

    assert create_response.status_code == 201

    outlet_id = create_response.json()["id"]

    # Act: delete the outlet.
    delete_response = client.delete(
        f"/api/v1/outlets/{outlet_id}",
    )

    # Assert: deletion succeeds.
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Assert: the soft-deleted outlet is no longer accessible.
    get_response = client.get(
        f"/api/v1/outlets/{outlet_id}",
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Outlet not found."