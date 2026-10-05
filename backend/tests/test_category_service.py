from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Category, Retailer
from app.schemas import CategoryCreate, CategoryUpdate


def create_retailer(db):
    retailer = Retailer(
        name="Test Retailer",
        email="category-service@example.com",
    )
    db.add(retailer)
    db.commit()
    db.refresh(retailer)

    return retailer


def create_category(db, retailer_id, name="Electronics"):
    category = Category(
        retailer_id=retailer_id,
        name=name,
        description="Test category",
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def test_create_category(db):
    retailer = create_retailer(db)

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    category = service.create_category(
        db,
        CategoryCreate(
            retailer_id=retailer.id,
            name="Electronics",
            description="Electronic products",
        ),
    )

    assert category.id is not None
    assert category.retailer_id == retailer.id
    assert category.name == "Electronics"
    assert category.description == "Electronic products"
    assert category.is_active is True


def test_create_category_without_description(db):
    retailer = create_retailer(db)

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    category = service.create_category(
        db,
        CategoryCreate(
            retailer_id=retailer.id,
            name="Groceries",
        ),
    )

    assert category.id is not None
    assert category.name == "Groceries"
    assert category.description is None


def test_create_category_raises_when_retailer_not_found(db):
    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    try:
        service.create_category(
            db,
            CategoryCreate(
                retailer_id=999999,
                name="Electronics",
            ),
        )
        assert False
    except ResourceNotFoundError as exc:
        assert str(exc) == "Retailer not found."


def test_create_category_rejects_duplicate_name(db):
    retailer = create_retailer(db)

    create_category(
        db,
        retailer.id,
        "Electronics",
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    try:
        service.create_category(
            db,
            CategoryCreate(
                retailer_id=retailer.id,
                name="Electronics",
            ),
        )
        assert False
    except ResourceConflictError as exc:
        assert (
            str(exc)
            == "A category with this name already exists for this retailer."
        )


def test_create_category_allows_same_name_for_different_retailers(db):
    retailer_1 = create_retailer(db)

    retailer_2 = Retailer(
        name="Second Retailer",
        email="second-category-service@example.com",
    )
    db.add(retailer_2)
    db.commit()
    db.refresh(retailer_2)

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    category_1 = service.create_category(
        db,
        CategoryCreate(
            retailer_id=retailer_1.id,
            name="Electronics",
        ),
    )

    category_2 = service.create_category(
        db,
        CategoryCreate(
            retailer_id=retailer_2.id,
            name="Electronics",
        ),
    )

    assert category_1.id != category_2.id
    assert category_1.retailer_id == retailer_1.id
    assert category_2.retailer_id == retailer_2.id


def test_get_category(db):
    retailer = create_retailer(db)
    category = create_category(
        db,
        retailer.id,
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    result = service.get_category(
        db,
        category.id,
    )

    assert result.id == category.id
    assert result.name == "Electronics"


def test_get_category_raises_when_not_found(db):
    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    try:
        service.get_category(
            db,
            999999,
        )
        assert False
    except ResourceNotFoundError as exc:
        assert str(exc) == "Category not found."


def test_list_categories(db):
    retailer = create_retailer(db)

    create_category(
        db,
        retailer.id,
        "Electronics",
    )

    create_category(
        db,
        retailer.id,
        "Groceries",
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    categories = service.list_categories(
        db,
    )

    assert len(categories) == 2


def test_update_category(db):
    retailer = create_retailer(db)

    category = create_category(
        db,
        retailer.id,
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    updated = service.update_category(
        db,
        category.id,
        CategoryUpdate(
            name="Consumer Electronics",
            description="Updated description",
        ),
    )

    assert updated.name == "Consumer Electronics"
    assert updated.description == "Updated description"


def test_update_category_rejects_duplicate_name(db):
    retailer = create_retailer(db)

    category_1 = create_category(
        db,
        retailer.id,
        "Electronics",
    )

    category_2 = create_category(
        db,
        retailer.id,
        "Groceries",
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    try:
        service.update_category(
            db,
            category_2.id,
            CategoryUpdate(
                name="Electronics",
            ),
        )
        assert False
    except ResourceConflictError as exc:
        assert (
            str(exc)
            == "A category with this name already exists for this retailer."
        )


def test_delete_category_soft_deletes_category(db):
    retailer = create_retailer(db)

    category = create_category(
        db,
        retailer.id,
    )

    service = __import__(
        "app.services",
        fromlist=["CategoryService"],
    ).CategoryService()

    service.delete_category(
        db,
        category.id,
    )

    assert category.is_active is False