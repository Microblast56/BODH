from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Retailer
from app.schemas import RetailerCreate, RetailerUpdate


class RetailerRepository:
    def create(
        self,
        db: Session,
        retailer_data: RetailerCreate,
    ) -> Retailer:
        retailer = Retailer(
            **retailer_data.model_dump()
        )

        db.add(retailer)
        db.commit()
        db.refresh(retailer)

        return retailer

    def get_by_id(
        self,
        db: Session,
        retailer_id: int,
    ) -> Retailer | None:
        statement = select(Retailer).where(
            Retailer.id == retailer_id
        )

        return db.scalar(statement)

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> Retailer | None:
        statement = select(Retailer).where(
            Retailer.email == email
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Retailer]:
        statement = (
            select(Retailer)
            .order_by(Retailer.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update(
        self,
        db: Session,
        retailer: Retailer,
        retailer_data: RetailerUpdate,
    ) -> Retailer:
        update_data = retailer_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(retailer, field, value)

        db.commit()
        db.refresh(retailer)

        return retailer

    def delete(
        self,
        db: Session,
        retailer: Retailer,
    ) -> None:
        db.delete(retailer)
        db.commit()