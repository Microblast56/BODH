import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Outlet, Restaurant
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
)
from app.services.restaurant import RestaurantService


service = RestaurantService()


def test_create_restaurant(db):
    restaurant_data = RestaurantCreate(
        name="Test Restaurant",
        email="test@example.com",
        phone="1111111111",
    )

    restaurant = service.create_restaurant(
        db,
        restaurant_data,
    )

    assert restaurant.id is not None
    assert restaurant.name == "Test Restaurant"
    assert restaurant.email == "test@example.com"
    assert restaurant.phone == "1111111111"
    assert restaurant.is_active is True


def test_create_restaurant_without_email(db):
    restaurant_data = RestaurantCreate(
        name="No Email Restaurant",
        phone="2222222222",
    )

    restaurant = service.create_restaurant(
        db,
        restaurant_data,
    )

    assert restaurant.id is not None
    assert restaurant.name == "No Email Restaurant"
    assert restaurant.email is None
    assert restaurant.is_active is True


def test_create_restaurant_rejects_duplicate_email(db):
    first_data = RestaurantCreate(
        name="First Restaurant",
        email="duplicate@example.com",
    )

    service.create_restaurant(
        db,
        first_data,
    )

    second_data = RestaurantCreate(
        name="Second Restaurant",
        email="duplicate@example.com",
    )

    with pytest.raises(ResourceConflictError):
        service.create_restaurant(
            db,
            second_data,
        )


def test_get_restaurant(db):
    restaurant_data = RestaurantCreate(
        name="Get Restaurant",
        email="get@example.com",
    )

    created = service.create_restaurant(
        db,
        restaurant_data,
    )

    restaurant = service.get_restaurant(
        db,
        created.id,
    )

    assert restaurant.id == created.id
    assert restaurant.name == "Get Restaurant"


def test_get_restaurant_raises_when_not_found(db):
    with pytest.raises(ResourceNotFoundError):
        service.get_restaurant(
            db,
            999999,
        )


def test_list_restaurants(db):
    first = service.create_restaurant(
        db,
        RestaurantCreate(
            name="First Restaurant",
            email="first@example.com",
        ),
    )

    second = service.create_restaurant(
        db,
        RestaurantCreate(
            name="Second Restaurant",
            email="second@example.com",
        ),
    )

    restaurants = service.list_restaurants(
        db,
    )

    restaurant_ids = [restaurant.id for restaurant in restaurants]

    assert first.id in restaurant_ids
    assert second.id in restaurant_ids


def test_update_restaurant(db):
    restaurant = service.create_restaurant(
        db,
        RestaurantCreate(
            name="Original Restaurant",
            email="original@example.com",
            phone="3333333333",
        ),
    )

    updated = service.update_restaurant(
        db,
        restaurant.id,
        RestaurantUpdate(
            name="Updated Restaurant",
            phone="4444444444",
        ),
    )

    assert updated.id == restaurant.id
    assert updated.name == "Updated Restaurant"
    assert updated.email == "original@example.com"
    assert updated.phone == "4444444444"


def test_update_restaurant_rejects_duplicate_email(db):
    first = service.create_restaurant(
        db,
        RestaurantCreate(
            name="First Restaurant",
            email="first-update@example.com",
        ),
    )

    second = service.create_restaurant(
        db,
        RestaurantCreate(
            name="Second Restaurant",
            email="second-update@example.com",
        ),
    )

    with pytest.raises(ResourceConflictError):
        service.update_restaurant(
            db,
            second.id,
            RestaurantUpdate(
                email=first.email,
            ),
        )


def test_delete_restaurant_soft_deletes_restaurant(db):
    restaurant = service.create_restaurant(
        db,
        RestaurantCreate(
            name="Delete Restaurant",
            email="delete@example.com",
        ),
    )

    service.delete_restaurant(
        db,
        restaurant.id,
    )

    db.refresh(restaurant)

    assert restaurant.is_active is False


def test_delete_restaurant_soft_deletes_outlets(db):
    restaurant = service.create_restaurant(
        db,
        RestaurantCreate(
            name="Restaurant With Outlets",
            email="outlets@example.com",
        ),
    )

    outlet_one = Outlet(
        restaurant_id=restaurant.id,
        name="Main Outlet",
        code="MAIN",
    )

    outlet_two = Outlet(
        restaurant_id=restaurant.id,
        name="Second Outlet",
        code="SECOND",
    )

    db.add_all([
        outlet_one,
        outlet_two,
    ])
    db.commit()
    db.refresh(outlet_one)
    db.refresh(outlet_two)

    service.delete_restaurant(
        db,
        restaurant.id,
    )

    db.refresh(restaurant)
    db.refresh(outlet_one)
    db.refresh(outlet_two)

    assert restaurant.is_active is False
    assert outlet_one.is_active is False
    assert outlet_two.is_active is False