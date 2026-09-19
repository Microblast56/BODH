from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models.restaurant import Restaurant
from app.repositories.outlet import OutletRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
)


class RestaurantService:

    def __init__(self):
        self.repository = RestaurantRepository()
        self.outlet_repository = OutletRepository()

    def create_restaurant(
        self,
        db: Session,
        restaurant_data: RestaurantCreate,
    ) -> Restaurant:

        if restaurant_data.email:
            existing = self.repository.get_by_email(
                db,
                restaurant_data.email,
            )

            if existing:
                raise ResourceConflictError(
                    "Restaurant with this email already exists."
                )

        restaurant = Restaurant(
            name=restaurant_data.name,
            email=restaurant_data.email,
            phone=restaurant_data.phone,
        )

        return self.repository.create(
            db,
            restaurant,
        )

    def get_restaurant(
        self,
        db: Session,
        restaurant_id: int,
    ) -> Restaurant:

        restaurant = self.repository.get_by_id(
            db,
            restaurant_id,
        )

        if not restaurant:
            raise ResourceNotFoundError(
                "Restaurant not found."
            )

        return restaurant

    def list_restaurants(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Restaurant]:

        return self.repository.list(
            db,
            offset=offset,
            limit=limit,
        )

    def update_restaurant(
        self,
        db: Session,
        restaurant_id: int,
        restaurant_data: RestaurantUpdate,
    ) -> Restaurant:

        restaurant = self.get_restaurant(
            db,
            restaurant_id,
        )

        update_data = restaurant_data.model_dump(
            exclude_unset=True,
        )

        if "email" in update_data and update_data["email"]:
            existing = self.repository.get_by_email(
                db,
                update_data["email"],
            )

            if existing and existing.id != restaurant_id:
                raise ResourceConflictError(
                    "Restaurant with this email already exists."
                )

        for field, value in update_data.items():
            setattr(restaurant, field, value)

        return self.repository.update(
            db,
            restaurant,
        )

    def delete_restaurant(
        self,
        db: Session,
        restaurant_id: int,
    ) -> None:

        restaurant = self.get_restaurant(
            db,
            restaurant_id,
        )

        # Soft-delete the restaurant.
        self.repository.delete(
            db,
            restaurant,
        )

        # Soft-delete all outlets belonging to this restaurant.
        outlets = self.outlet_repository.list_by_restaurant(
            db,
            restaurant_id,
        )

        for outlet in outlets:
            outlet.is_active = False

        db.commit()