from typing import List

from sqlalchemy.orm import Session

from app.models.outlet import Outlet


class OutletRepository:

    def create(
        self,
        db: Session,
        outlet: Outlet,
    ) -> Outlet:
        db.add(outlet)
        db.commit()
        db.refresh(outlet)
        return outlet

    def get_by_id(
        self,
        db: Session,
        outlet_id: int,
    ) -> Outlet | None:
        return (
            db.query(Outlet)
            .filter(Outlet.id == outlet_id)
            .first()
        )

    def get_by_restaurant_and_code(
        self,
        db: Session,
        restaurant_id: int,
        code: str,
    ) -> Outlet | None:
        return (
            db.query(Outlet)
            .filter(
                Outlet.restaurant_id == restaurant_id,
                Outlet.code == code,
            )
            .first()
        )

    def list(
        self,
        db: Session,
        restaurant_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Outlet]:

        query = db.query(Outlet)

        if restaurant_id is not None:
            query = query.filter(
                Outlet.restaurant_id == restaurant_id
            )

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_by_restaurant(
        self,
        db: Session,
        restaurant_id: int,
    ) -> List[Outlet]:
        return (
            db.query(Outlet)
            .filter(
                Outlet.restaurant_id == restaurant_id
            )
            .all()
        )

    def update(
        self,
        db: Session,
        outlet: Outlet,
    ) -> Outlet:
        db.commit()
        db.refresh(outlet)
        return outlet

    def delete(
        self,
        db: Session,
        outlet: Outlet,
    ) -> None:
        outlet.is_active = False
        db.commit()
        db.refresh(outlet)