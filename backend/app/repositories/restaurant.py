from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant


class RestaurantRepository:

    def create(
        self,
        db: Session,
        restaurant: Restaurant,
    ) -> Restaurant:
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    def get_by_id(
        self,
        db: Session,
        restaurant_id: int,
    ) -> Restaurant | None:
        return (
            db.query(Restaurant)
            .filter(Restaurant.id == restaurant_id)
            .first()
        )

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> Restaurant | None:
        return (
            db.query(Restaurant)
            .filter(Restaurant.email == email)
            .first()
        )

    def list(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Restaurant]:
        return (
            db.query(Restaurant)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update(
        self,
        db: Session,
        restaurant: Restaurant,
    ) -> Restaurant:
        db.commit()
        db.refresh(restaurant)
        return restaurant

    def delete(
        self,
        db: Session,
        restaurant: Restaurant,
    ) -> None:
        restaurant.is_active = False
        db.commit()
        db.refresh(restaurant)