from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Store
from app.schemas import StoreCreate, StoreUpdate
from app.services import StoreService


def make_store(
    store_id: int = 1,
    retailer_id: int = 1,
    name: str = "Main Store",
    code: str = "MAIN",
) -> Store:
    store = Store(
        id=store_id,
        retailer_id=retailer_id,
        name=name,
        code=code,
        country="India",
        is_active=True,
    )

    return store


def make_service():
    repository = Mock()
    retailer_repository = Mock()

    service = StoreService(
        repository=repository,
        retailer_repository=retailer_repository,
    )

    return service, repository, retailer_repository


def test_create_store():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_code.return_value = None

    store = make_store()

    repository.create.return_value = store

    store_data = StoreCreate(
        retailer_id=1,
        name="Main Store",
        code="MAIN",
    )

    result = service.create_store(
        Mock(),
        store_data,
    )

    assert result == store
    repository.create.assert_called_once_with(
        repository.create.call_args.args[0],
        store_data,
    )


def test_create_store_raises_when_retailer_not_found():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = None

    store_data = StoreCreate(
        retailer_id=999,
        name="Main Store",
        code="MAIN",
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Retailer not found.",
    ):
        service.create_store(
            Mock(),
            store_data,
        )

    repository.create.assert_not_called()


def test_create_store_rejects_duplicate_code():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_code.return_value = make_store()

    store_data = StoreCreate(
        retailer_id=1,
        name="Another Store",
        code="MAIN",
    )

    with pytest.raises(
        ResourceConflictError,
        match="A store with this code already exists for this retailer.",
    ):
        service.create_store(
            Mock(),
            store_data,
        )

    repository.create.assert_not_called()


def test_create_store_allows_same_code_for_different_retailers():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=2,
        is_active=True,
    )

    repository.get_by_code.return_value = None

    store = make_store(
        retailer_id=2,
        code="MAIN",
    )

    repository.create.return_value = store

    store_data = StoreCreate(
        retailer_id=2,
        name="Main Store",
        code="MAIN",
    )

    result = service.create_store(
        Mock(),
        store_data,
    )

    assert result == store
    repository.create.assert_called_once()


def test_get_store():
    service, repository, _ = make_service()

    store = make_store()

    repository.get_by_id.return_value = store

    result = service.get_store(
        Mock(),
        1,
    )

    assert result == store
    repository.get_by_id.assert_called_once()


def test_get_store_raises_when_not_found():
    service, repository, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Store not found.",
    ):
        service.get_store(
            Mock(),
            999,
        )


def test_list_stores():
    service, repository, _ = make_service()

    stores = [
        make_store(store_id=1),
        make_store(
            store_id=2,
            name="Second Store",
            code="SECOND",
        ),
    ]

    repository.get_all.return_value = stores

    result = service.list_stores(
        Mock(),
        offset=10,
        limit=20,
    )

    assert result == stores

    repository.get_all.assert_called_once_with(
        repository.get_all.call_args.args[0],
        offset=10,
        limit=20,
    )


def test_update_store():
    service, repository, _ = make_service()

    store = make_store()

    repository.get_by_id.return_value = store
    repository.update.return_value = store

    update_data = StoreUpdate(
        name="Updated Store",
    )

    result = service.update_store(
        Mock(),
        1,
        update_data,
    )

    assert result == store
    repository.update.assert_called_once_with(
        repository.update.call_args.args[0],
        store,
        update_data,
    )


def test_update_store_rejects_duplicate_code():
    service, repository, _ = make_service()

    store = make_store(
        store_id=1,
        retailer_id=1,
        code="MAIN",
    )

    duplicate_store = make_store(
        store_id=2,
        retailer_id=1,
        code="SECOND",
    )

    repository.get_by_id.return_value = store
    repository.get_by_code.return_value = duplicate_store

    update_data = StoreUpdate(
        code="SECOND",
    )

    with pytest.raises(
        ResourceConflictError,
        match="A store with this code already exists for this retailer.",
    ):
        service.update_store(
            Mock(),
            1,
            update_data,
        )

    repository.update.assert_not_called()


def test_update_store_allows_same_code():
    service, repository, _ = make_service()

    store = make_store(
        store_id=1,
        retailer_id=1,
        code="MAIN",
    )

    repository.get_by_id.return_value = store
    repository.update.return_value = store

    update_data = StoreUpdate(
        code="MAIN",
        name="Updated Store",
    )

    result = service.update_store(
        Mock(),
        1,
        update_data,
    )

    assert result == store
    repository.update.assert_called_once()


def test_delete_store():
    service, repository, _ = make_service()

    store = make_store()

    repository.get_by_id.return_value = store

    service.delete_store(
        Mock(),
        1,
    )

    repository.delete.assert_called_once()


def test_delete_store_raises_when_not_found():
    service, repository, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Store not found.",
    ):
        service.delete_store(
            Mock(),
            999,
        )

    repository.delete.assert_not_called()