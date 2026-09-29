import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Outlet, Restaurant
from app.schemas.outlet import (
    OutletCreate,
    OutletUpdate,
)
from app.services.outlet import OutletService


service = OutletService()


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


def test_create_outlet(db):
    restaurant = create_restaurant(db)

    outlet_data = OutletCreate(
        restaurant_id=restaurant.id,
        name="Main Outlet",
        code="MAIN",
        city="Lucknow",
        state="Uttar Pradesh",
        phone="1111111111",
    )

    outlet = service.create_outlet(
        db,
        outlet_data,
    )

    assert outlet.id is not None
    assert outlet.restaurant_id == restaurant.id
    assert outlet.name == "Main Outlet"
    assert outlet.code == "MAIN"
    assert outlet.city == "Lucknow"
    assert outlet.state == "Uttar Pradesh"
    assert outlet.phone == "1111111111"
    assert outlet.is_active is True


def test_create_outlet_raises_when_restaurant_not_found(db):
    outlet_data = OutletCreate(
        restaurant_id=999999,
        name="Main Outlet",
        code="MAIN",
    )

    with pytest.raises(ResourceNotFoundError):
        service.create_outlet(
            db,
            outlet_data,
        )


def test_create_outlet_rejects_duplicate_code(db):
    restaurant = create_restaurant(db)

    first_data = OutletCreate(
        restaurant_id=restaurant.id,
        name="First Outlet",
        code="MAIN",
    )

    service.create_outlet(
        db,
        first_data,
    )

    second_data = OutletCreate(
        restaurant_id=restaurant.id,
        name="Second Outlet",
        code="MAIN",
    )

    with pytest.raises(ResourceConflictError):
        service.create_outlet(
            db,
            second_data,
        )


def test_create_outlet_allows_same_code_for_different_restaurants(db):
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

    first_outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=first_restaurant.id,
            name="Main Outlet",
            code="MAIN",
        ),
    )

    second_outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=second_restaurant.id,
            name="Main Outlet",
            code="MAIN",
        ),
    )

    assert first_outlet.id != second_outlet.id
    assert first_outlet.code == "MAIN"
    assert second_outlet.code == "MAIN"


def test_get_outlet(db):
    restaurant = create_restaurant(db)

    created = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="Get Outlet",
            code="GET",
        ),
    )

    outlet = service.get_outlet(
        db,
        created.id,
    )

    assert outlet.id == created.id
    assert outlet.restaurant_id == restaurant.id
    assert outlet.name == "Get Outlet"
    assert outlet.code == "GET"


def test_get_outlet_raises_when_not_found(db):
    with pytest.raises(ResourceNotFoundError):
        service.get_outlet(
            db,
            999999,
        )


def test_list_outlets(db):
    restaurant = create_restaurant(db)

    first = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="First Outlet",
            code="FIRST",
        ),
    )

    second = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="Second Outlet",
            code="SECOND",
        ),
    )

    outlets = service.list_outlets(
        db,
    )

    outlet_ids = [outlet.id for outlet in outlets]

    assert first.id in outlet_ids
    assert second.id in outlet_ids


def test_list_outlets_by_restaurant(db):
    first_restaurant = create_restaurant(
        db,
        name="First Restaurant",
        email="first-list@example.com",
    )

    second_restaurant = create_restaurant(
        db,
        name="Second Restaurant",
        email="second-list@example.com",
    )

    first_outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=first_restaurant.id,
            name="First Outlet",
            code="FIRST",
        ),
    )

    second_outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=second_restaurant.id,
            name="Second Outlet",
            code="SECOND",
        ),
    )

    outlets = service.list_outlets(
        db,
        restaurant_id=first_restaurant.id,
    )

    outlet_ids = [outlet.id for outlet in outlets]

    assert first_outlet.id in outlet_ids
    assert second_outlet.id not in outlet_ids


def test_update_outlet(db):
    restaurant = create_restaurant(db)

    outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="Original Outlet",
            code="ORIGINAL",
            phone="3333333333",
        ),
    )

    updated = service.update_outlet(
        db,
        outlet.id,
        OutletUpdate(
            name="Updated Outlet",
            code="UPDATED",
            phone="4444444444",
            city="Lucknow",
        ),
    )

    assert updated.id == outlet.id
    assert updated.restaurant_id == restaurant.id
    assert updated.name == "Updated Outlet"
    assert updated.code == "UPDATED"
    assert updated.phone == "4444444444"
    assert updated.city == "Lucknow"


def test_update_outlet_rejects_duplicate_code(db):
    restaurant = create_restaurant(db)

    first = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="First Outlet",
            code="FIRST",
        ),
    )

    second = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="Second Outlet",
            code="SECOND",
        ),
    )

    with pytest.raises(ResourceConflictError):
        service.update_outlet(
            db,
            second.id,
            OutletUpdate(
                code=first.code,
            ),
        )


def test_delete_outlet_soft_deletes_outlet(db):
    restaurant = create_restaurant(db)

    outlet = service.create_outlet(
        db,
        OutletCreate(
            restaurant_id=restaurant.id,
            name="Delete Outlet",
            code="DELETE",
        ),
    )

    service.delete_outlet(
        db,
        outlet.id,
    )

    db.refresh(outlet)

    assert outlet.is_active is False