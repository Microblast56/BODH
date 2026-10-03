from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:

    def create(
        self,
        db: Session,
        category_data: CategoryCreate,
    ) -> Category:
        category = Category(
            retailer_id=category_data.retailer_id,
            name=category_data.name,
            description=category_data.description,
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
        return db.get(Category, category_id)

    def get_by_name(
        self,
        db: Session,
        retailer_id: int,
        name: str,
    ) -> Category | None:
        statement = select(Category).where(
            Category.retailer_id == retailer_id,
            Category.name == name,
            Category.is_active.is_(True),
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
            .where(Category.is_active.is_(True))
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

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
        category.is_active = False

        db.commit()