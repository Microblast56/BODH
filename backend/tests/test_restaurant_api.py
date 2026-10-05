def test_create_restaurant_api(client):
    payload = {
        "name": "API Test Restaurant",
        "email": "api-restaurant@example.com",
        "phone": "1111111111",
    }

    response = client.post(
        "/api/v1/restaurants",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "API Test Restaurant"
    assert data["email"] == "api-restaurant@example.com"
    assert data["phone"] == "1111111111"
    assert data["is_active"] is True


def test_create_restaurant_api_without_email(client):
    response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "No Email Restaurant",
            "phone": "2222222222",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "No Email Restaurant"
    assert data["email"] is None
    assert data["phone"] == "2222222222"
    assert data["is_active"] is True


def test_create_restaurant_api_rejects_duplicate_email(client):
    payload = {
        "name": "First Restaurant",
        "email": "duplicate@example.com",
        "phone": "3333333333",
    }

    first_response = client.post(
        "/api/v1/restaurants",
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/restaurants",
        json={
            **payload,
            "name": "Second Restaurant",
        },
    )

    assert duplicate_response.status_code == 409

    data = duplicate_response.json()

    assert data["detail"] == (
        "Restaurant with this email already exists."
    )


def test_get_restaurant_api(client):
    response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "GET API Restaurant",
            "email": "get-restaurant@example.com",
            "phone": "4444444444",
        },
    )

    assert response.status_code == 201

    restaurant_id = response.json()["id"]

    response = client.get(
        f"/api/v1/restaurants/{restaurant_id}",
    )

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


def test_list_restaurants_api(client):
    client.post(
        "/api/v1/restaurants",
        json={
            "name": "First Listed Restaurant",
            "email": "list-first@example.com",
        },
    )

    client.post(
        "/api/v1/restaurants",
        json={
            "name": "Second Listed Restaurant",
            "email": "list-second@example.com",
        },
    )

    response = client.get(
        "/api/v1/restaurants",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_list_restaurants_api_supports_pagination(client):
    for index in range(3):
        response = client.post(
            "/api/v1/restaurants",
            json={
                "name": f"Pagination Restaurant {index}",
                "email": f"pagination-{index}@example.com",
            },
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/restaurants?offset=1&limit=1",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_update_restaurant_api(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "Original Restaurant",
            "email": "update@example.com",
            "phone": "5555555555",
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/restaurants/{restaurant_id}",
        json={
            "name": "Updated Restaurant",
            "phone": "6666666666",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == restaurant_id
    assert data["name"] == "Updated Restaurant"
    assert data["email"] == "update@example.com"
    assert data["phone"] == "6666666666"
    assert data["is_active"] is True


def test_update_restaurant_api_returns_404_for_nonexistent_restaurant(
    client,
):
    response = client.patch(
        "/api/v1/restaurants/999999",
        json={
            "name": "Updated Restaurant",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Restaurant not found."


def test_update_restaurant_api_rejects_duplicate_email(client):
    first_response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "First Restaurant",
            "email": "first-update@example.com",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "Second Restaurant",
            "email": "second-update@example.com",
        },
    )

    assert second_response.status_code == 201

    second_id = second_response.json()["id"]

    response = client.patch(
        f"/api/v1/restaurants/{second_id}",
        json={
            "email": "first-update@example.com",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"] == (
        "Restaurant with this email already exists."
    )


def test_delete_restaurant_api(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "Delete Restaurant",
            "email": "delete-api@example.com",
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/restaurants/{restaurant_id}",
    )

    assert response.status_code == 204


def test_delete_restaurant_api_returns_404_after_deletion(client):
    create_response = client.post(
        "/api/v1/restaurants",
        json={
            "name": "Delete Then Get Restaurant",
            "email": "delete-get@example.com",
        },
    )

    assert create_response.status_code == 201

    restaurant_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/restaurants/{restaurant_id}",
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/restaurants/{restaurant_id}",
    )

    assert get_response.status_code == 404

    data = get_response.json()

    assert data["detail"] == "Restaurant not found."