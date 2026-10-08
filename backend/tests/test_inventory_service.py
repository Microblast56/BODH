from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory
from app.schemas import InventoryCreate, InventoryUpdate
from app.services import InventoryService


def make_inventory(
    inventory_id: int = 1,
    store_id: int = 1,
    product_id: int = 1,
    quantity_on_hand: int = 100,
    reorder_level: int = 10,
    reorder_quantity: int = 50,
) -> Inventory:
    inventory = Inventory(
        id=inventory_id,
        store_id=store_id,
        product_id=product_id,
        quantity_on_hand=quantity_on_hand,
        reorder_level=reorder_level,
        reorder_quantity=reorder_quantity,
        
    )

    return inventory


def make_service():
    repository = Mock()
    store_repository = Mock()
    product_repository = Mock()

    service = InventoryService(
        repository=repository,
        store_repository=store_repository,
        product_repository=product_repository,
    )

    return (
        service,
        repository,
        store_repository,
        product_repository,
    )


def test_create_inventory():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    product_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_store_and_product.return_value = None

    inventory = make_inventory()

    repository.create.return_value = inventory

    inventory_data = InventoryCreate(
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
        reorder_quantity=50,
    )

    result = service.create_inventory(
        Mock(),
        inventory_data,
    )

    assert result == inventory

    repository.create.assert_called_once_with(
        repository.create.call_args.args[0],
        inventory_data,
    )


def test_create_inventory_raises_when_store_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = None

    inventory_data = InventoryCreate(
        store_id=999,
        product_id=1,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Store not found.",
    ):
        service.create_inventory(
            Mock(),
            inventory_data,
        )

    product_repository.get_by_id.assert_not_called()
    repository.create.assert_not_called()


def test_create_inventory_raises_when_product_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    product_repository.get_by_id.return_value = None

    inventory_data = InventoryCreate(
        store_id=1,
        product_id=999,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Product not found.",
    ):
        service.create_inventory(
            Mock(),
            inventory_data,
        )

    repository.create.assert_not_called()


def test_create_inventory_rejects_duplicate():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    product_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_store_and_product.return_value = (
        make_inventory()
    )

    inventory_data = InventoryCreate(
        store_id=1,
        product_id=1,
    )

    with pytest.raises(
        ResourceConflictError,
        match="Inventory already exists for this store and product.",
    ):
        service.create_inventory(
            Mock(),
            inventory_data,
        )

    repository.create.assert_not_called()


def test_create_inventory_allows_same_product_for_different_store():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = Mock(
        id=2,
        is_active=True,
    )

    product_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_store_and_product.return_value = None

    inventory = make_inventory(
        store_id=2,
        product_id=1,
    )

    repository.create.return_value = inventory

    inventory_data = InventoryCreate(
        store_id=2,
        product_id=1,
    )

    result = service.create_inventory(
        Mock(),
        inventory_data,
    )

    assert result == inventory
    repository.create.assert_called_once()


def test_get_inventory():
    service, repository, _, _ = make_service()

    inventory = make_inventory()

    repository.get_by_id.return_value = inventory

    result = service.get_inventory(
        Mock(),
        1,
    )

    assert result == inventory

    repository.get_by_id.assert_called_once()


def test_get_inventory_raises_when_not_found():
    service, repository, _, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.get_inventory(
            Mock(),
            999,
        )


def test_list_inventories():
    service, repository, _, _ = make_service()

    inventories = [
        make_inventory(inventory_id=1),
        make_inventory(
            inventory_id=2,
            product_id=2,
        ),
    ]

    repository.get_all.return_value = inventories

    result = service.list_inventories(
        Mock(),
        offset=10,
        limit=20,
    )

    assert result == inventories

    repository.get_all.assert_called_once_with(
        repository.get_all.call_args.args[0],
        offset=10,
        limit=20,
    )


def test_list_by_store():
    (
        service,
        repository,
        store_repository,
        _,
    ) = make_service()

    store_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    inventories = [
        make_inventory(
            inventory_id=1,
            store_id=1,
        ),
        make_inventory(
            inventory_id=2,
            store_id=1,
            product_id=2,
        ),
    ]

    repository.get_by_store.return_value = inventories

    result = service.list_by_store(
        Mock(),
        1,
    )

    assert result == inventories

    repository.get_by_store.assert_called_once()


def test_list_by_store_raises_when_store_not_found():
    (
        service,
        repository,
        store_repository,
        _,
    ) = make_service()

    store_repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Store not found.",
    ):
        service.list_by_store(
            Mock(),
            999,
        )

    repository.get_by_store.assert_not_called()


def test_list_by_product():
    (
        service,
        repository,
        _,
        product_repository,
    ) = make_service()

    product_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    inventories = [
        make_inventory(
            inventory_id=1,
            product_id=1,
        ),
        make_inventory(
            inventory_id=2,
            store_id=2,
            product_id=1,
        ),
    ]

    repository.get_by_product.return_value = inventories

    result = service.list_by_product(
        Mock(),
        1,
    )

    assert result == inventories

    repository.get_by_product.assert_called_once()


def test_list_by_product_raises_when_product_not_found():
    (
        service,
        repository,
        _,
        product_repository,
    ) = make_service()

    product_repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Product not found.",
    ):
        service.list_by_product(
            Mock(),
            999,
        )

    repository.get_by_product.assert_not_called()


def test_update_inventory():
    service, repository, _, _ = make_service()

    inventory = make_inventory()

    repository.get_by_id.return_value = inventory
    repository.update.return_value = inventory

    update_data = InventoryUpdate(
        quantity_on_hand=150,
        reorder_level=20,
    )

    result = service.update_inventory(
        Mock(),
        1,
        update_data,
    )

    assert result == inventory

    repository.update.assert_called_once_with(
        repository.update.call_args.args[0],
        inventory,
        update_data,
    )


def test_update_inventory_raises_when_not_found():
    service, repository, _, _ = make_service()

    repository.get_by_id.return_value = None

    update_data = InventoryUpdate(
        quantity_on_hand=150,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.update_inventory(
            Mock(),
            999,
            update_data,
        )

    repository.update.assert_not_called()


def test_delete_inventory():
    service, repository, _, _ = make_service()

    inventory = make_inventory()

    repository.get_by_id.return_value = inventory

    service.delete_inventory(
        Mock(),
        1,
    )

    repository.delete.assert_called_once()


def test_delete_inventory_raises_when_not_found():
    service, repository, _, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.delete_inventory(
            Mock(),
            999,
        )

    repository.delete.assert_not_called()