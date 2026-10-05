from app.models import Category, Retailer


def create_retailer(db, name="Test Retailer"):
    retailer = Retailer(
        name=name,
    )

    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def create_category(db, retailer_id, name="Beverages"):
    category = Category(
        retailer_id=retailer_id,
        name=name,
        description="Drinks and beverages",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def test_create_category_api(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/categories",
        json={
            "retailer_id": retailer.id,
            "name": "Beverages",
            "description": "Drinks and beverages",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Beverages"
    assert data["description"] == "Drinks and beverages"


def test_create_category_api_without_description(client, db):
    retailer = create_retailer(db)

    response = client.post(
        "/api/v1/categories",
        json={
            "retailer_id": retailer.id,
            "name": "Snacks",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Snacks"
    assert data["description"] is None


def test_create_category_api_rejects_missing_retailer(client):
    response = client.post(
        "/api/v1/categories",
        json={
            "retailer_id": 999999,
            "name": "Beverages",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Retailer not found."


def test_create_category_api_rejects_duplicate_name(client, db):
    retailer = create_retailer(db)

    create_category(
        db,
        retailer.id,
        name="Beverages",
    )

    response = client.post(
        "/api/v1/categories",
        json={
            "retailer_id": retailer.id,
            "name": "Beverages",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "A category with this name already exists for this retailer."
    )


def test_get_category_api(client, db):
    retailer = create_retailer(db)

    category = create_category(
        db,
        retailer.id,
    )

    response = client.get(
        f"/api/v1/categories/{category.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == category.id
    assert data["retailer_id"] == retailer.id
    assert data["name"] == "Beverages"


def test_get_category_api_returns_404_when_not_found(client):
    response = client.get(
        "/api/v1/categories/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."


def test_list_categories_api(client, db):
    retailer = create_retailer(db)

    create_category(
        db,
        retailer.id,
        name="Beverages",
    )

    category = Category(
        retailer_id=retailer.id,
        name="Snacks",
    )

    db.add(category)
    db.commit()

    response = client.get(
        "/api/v1/categories"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_list_categories_api_supports_pagination(client, db):
    retailer = create_retailer(db)

    for name in ["Beverages", "Snacks", "Bakery"]:
        db.add(
            Category(
                retailer_id=retailer.id,
                name=name,
            )
        )

    db.commit()

    response = client.get(
        "/api/v1/categories?offset=1&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_update_category_api(client, db):
    retailer = create_retailer(db)

    category = create_category(
        db,
        retailer.id,
    )

    response = client.patch(
        f"/api/v1/categories/{category.id}",
        json={
            "name": "Cold Beverages",
            "description": "Cold drinks",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Cold Beverages"
    assert data["description"] == "Cold drinks"


def test_update_category_api_returns_404_when_not_found(client):
    response = client.patch(
        "/api/v1/categories/999999",
        json={
            "name": "Updated Category",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."


def test_update_category_api_rejects_duplicate_name(client, db):
    retailer = create_retailer(db)

    create_category(
        db,
        retailer.id,
        name="Beverages",
    )

    second_category = Category(
        retailer_id=retailer.id,
        name="Snacks",
    )

    db.add(second_category)
    db.commit()
    db.refresh(second_category)

    response = client.patch(
        f"/api/v1/categories/{second_category.id}",
        json={
            "name": "Beverages",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "A category with this name already exists for this retailer."
    )


def test_delete_category_api(client, db):
    retailer = create_retailer(db)

    category = create_category(
        db,
        retailer.id,
    )

    response = client.delete(
        f"/api/v1/categories/{category.id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/categories/{category.id}"
    )

    assert response.status_code == 404