from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def create(
        self,
        db: Session,
        category_data: CategoryCreate,
    ) -> Category:
        category = Category(
            **category_data.model_dump()
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    def get_by_id(
        self,
        db: Session,
        category_id: int,
    ) -> Category | None:
        statement = select(Category).where(
            Category.id == category_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        statement = (
            select(Category)
            .order_by(Category.id)
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def get_by_name(
        self,
        db: Session,
        retailer_id: int,
        name: str,
    ) -> Category | None:
        statement = select(Category).where(
            Category.retailer_id == retailer_id,
            Category.name == name,
        )

        return db.scalar(statement)

    def update(
        self,
        db: Session,
        category: Category,
        category_data: CategoryUpdate,
    ) -> Category:
        update_data = category_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(category, field, value)

        db.commit()
        db.refresh(category)

        return category

    def delete(
        self,
        db: Session,
        category: Category,
    ) -> None:
        db.delete(category)
        db.commit()
