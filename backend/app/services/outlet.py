from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models.outlet import Outlet
from app.repositories.outlet import OutletRepository
from app.repositories.restaurant import RestaurantRepository
from app.schemas.outlet import (
    OutletCreate,
    OutletUpdate,
)


class OutletService:

    def __init__(self):
        self.repository = OutletRepository()
        self.restaurant_repository = RestaurantRepository()

    def create_outlet(
        self,
        db: Session,
        outlet_data: OutletCreate,
    ) -> Outlet:

        restaurant = self.restaurant_repository.get_by_id(
            db,
            outlet_data.restaurant_id,
        )

        if not restaurant:
            raise ResourceNotFoundError(
                "Restaurant not found."
            )

        existing = self.repository.get_by_restaurant_and_code(
            db,
            outlet_data.restaurant_id,
            outlet_data.code,
        )

        if existing:
            raise ResourceConflictError(
                "Outlet with this code already exists for this restaurant."
            )

        outlet = Outlet(
            restaurant_id=outlet_data.restaurant_id,
            name=outlet_data.name,
            code=outlet_data.code,
            address_line1=outlet_data.address_line1,
            address_line2=outlet_data.address_line2,
            city=outlet_data.city,
            state=outlet_data.state,
            postal_code=outlet_data.postal_code,
            country=outlet_data.country,
            phone=outlet_data.phone,
        )

        return self.repository.create(
            db,
            outlet,
        )

    def get_outlet(
        self,
        db: Session,
        outlet_id: int,
    ) -> Outlet:

        outlet = self.repository.get_by_id(
            db,
            outlet_id,
        )

        if not outlet:
            raise ResourceNotFoundError(
                "Outlet not found."
            )

        return outlet

    def list_outlets(
        self,
        db: Session,
        restaurant_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Outlet]:

        return self.repository.list(
            db,
            restaurant_id=restaurant_id,
            offset=offset,
            limit=limit,
        )

    def update_outlet(
        self,
        db: Session,
        outlet_id: int,
        outlet_data: OutletUpdate,
    ) -> Outlet:

        outlet = self.get_outlet(
            db,
            outlet_id,
        )

        update_data = outlet_data.model_dump(
            exclude_unset=True,
        )

        if "code" in update_data:
            existing = self.repository.get_by_restaurant_and_code(
                db,
                outlet.restaurant_id,
                update_data["code"],
            )

            if existing and existing.id != outlet_id:
                raise ResourceConflictError(
                    "Outlet with this code already exists for this restaurant."
                )

        for field, value in update_data.items():
            setattr(outlet, field, value)

        db.commit()
        db.refresh(outlet)

        return outlet

    def delete_outlet(
        self,
        db: Session,
        outlet_id: int,
    ) -> None:

        outlet = self.get_outlet(
            db,
            outlet_id,
        )

        self.repository.delete(
            db,
            outlet,
        )