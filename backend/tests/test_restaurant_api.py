from app.models import Restaurant


def test_create_restaurant_api(client):
    # Arrange
    payload = {
        "name": "API Test Restaurant",
        "email": "api-restaurant@example.com",
        "phone": "1111111111",
    }

    # Act
    response = client.post(
        "/api/v1/restaurants",
        json=payload,
    )

    # Assert
    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "API Test Restaurant"
    assert data["email"] == "api-restaurant@example.com"
    assert data["phone"] == "1111111111"
    assert data["is_active"] is True


def test_create_restaurant_api_rejects_duplicate_email(
    client,
):
    # Arrange
    first_payload = {
        "name": "First Restaurant",
        "email": "duplicate@example.com",
        "phone": "2222222222",
    }

    second_payload = {
        "name": "Second Restaurant",
        "email": "duplicate@example.com",
        "phone": "3333333333",
    }

    # Create first restaurant
    first_response = client.post(
        "/api/v1/restaurants",
        json=first_payload,
    )

    assert first_response.status_code == 201

    # Act
    duplicate_response = client.post(
        "/api/v1/restaurants",
        json=second_payload,
    )

    # Assert
    assert duplicate_response.status_code == 409

    data = duplicate_response.json()

    assert data["detail"] == (
        "Restaurant with this email already exists."
    )


def test_get_restaurant_api(client):
    # Arrange
    payload = {
        "name": "GET API Restaurant",
        "email": "get-restaurant@example.com",
        "phone": "4444444444",
    }

    create_response = client.post(
        "/api/v1/restaurants",
        json=payload,
    )

    assert create_response.status_code == 201

    created_restaurant = create_response.json()
    restaurant_id = created_restaurant["id"]

    # Act
    response = client.get(
        f"/api/v1/restaurants/{restaurant_id}",
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == restaurant_id
    assert data["name"] == "GET API Restaurant"
    assert data["email"] == "get-restaurant@example.com"
    assert data["phone"] == "4444444444"
    assert data["is_active"] is True


def test_get_restaurant_api_returns_404_for_nonexistent_restaurant(
    client,
):
    response = client.get(
        "/api/v1/restaurants/999999",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Restaurant not found."