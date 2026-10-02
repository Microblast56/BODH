from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory, Product, Store
from app.schemas import InventoryCreate, InventoryUpdate
from app.services import InventoryService


def make_store(store_id: int = 1) -> Store:
    return Store(
        id=store_id,
        retailer_id=1,
        name="Main Store",
        code=f"STORE-{store_id}",
        country="India",
        is_active=True,
    )


def make_product(product_id: int = 1) -> Product:
    return Product(
        id=product_id,
        retailer_id=1,
        name=f"Product {product_id}",
        sku=f"SKU-{product_id}",
        cost_price=100,
        selling_price=150,
        unit="piece",
        is_active=True,
    )


def make_inventory(
    inventory_id: int = 1,
    store_id: int = 1,
    product_id: int = 1,
) -> Inventory:
    return Inventory(
        id=inventory_id,
        store_id=store_id,
        product_id=product_id,
        quantity_on_hand=50,
        reorder_level=10,
        reorder_quantity=20,
        last_restocked_at=None,
    )


def make_service() -> tuple[
    InventoryService,
    Mock,
    Mock,
    Mock,
]:
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

    store = make_store()
    product = make_product()
    inventory = make_inventory()

    store_repository.get_by_id.return_value = store
    product_repository.get_by_id.return_value = product
    repository.get_by_store_and_product.return_value = None
    repository.create.return_value = inventory

    data = InventoryCreate(
        store_id=1,
        product_id=1,
        quantity_on_hand=50,
        reorder_level=10,
        reorder_quantity=20,
    )

    result = service.create_inventory(
        Mock(),
        data,
    )

    assert result == inventory
    repository.create.assert_called_once_with(
        repository.create.call_args.args[0],
        data,
    )


def test_create_inventory_raises_when_store_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = None

    data = InventoryCreate(
        store_id=999,
        product_id=1,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Store not found.",
    ):
        service.create_inventory(
            Mock(),
            data,
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

    store_repository.get_by_id.return_value = make_store()
    product_repository.get_by_id.return_value = None

    data = InventoryCreate(
        store_id=1,
        product_id=999,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Product not found.",
    ):
        service.create_inventory(
            Mock(),
            data,
        )

    repository.create.assert_not_called()


def test_create_inventory_rejects_duplicate():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = make_store()
    product_repository.get_by_id.return_value = make_product()
    repository.get_by_store_and_product.return_value = (
        make_inventory()
    )

    data = InventoryCreate(
        store_id=1,
        product_id=1,
    )

    with pytest.raises(
        ResourceConflictError,
        match="Inventory already exists",
    ):
        service.create_inventory(
            Mock(),
            data,
        )

    repository.create.assert_not_called()


def test_create_inventory_allows_same_product_for_different_store():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = make_store(2)
    product_repository.get_by_id.return_value = make_product(1)
    repository.get_by_store_and_product.return_value = None
    repository.create.return_value = make_inventory(
        store_id=2,
        product_id=1,
    )

    data = InventoryCreate(
        store_id=2,
        product_id=1,
    )

    result = service.create_inventory(
        Mock(),
        data,
    )

    assert result.store_id == 2
    assert result.product_id == 1
    repository.create.assert_called_once()


def test_get_inventory():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    inventory = make_inventory()
    repository.get_by_id.return_value = inventory

    result = service.get_inventory(
        Mock(),
        1,
    )

    assert result == inventory
    repository.get_by_id.assert_called_once()


def test_get_inventory_raises_when_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

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
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    inventories = [
        make_inventory(1),
        make_inventory(2),
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
        product_repository,
    ) = make_service()

    store_repository.get_by_id.return_value = make_store()
    inventories = [make_inventory()]
    repository.get_by_store.return_value = inventories

    result = service.list_by_store(
        Mock(),
        1,
    )

    assert result == inventories
    repository.get_by_store.assert_called_once()


def test_list_by_store_raises_when_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
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
        store_repository,
        product_repository,
    ) = make_service()

    product_repository.get_by_id.return_value = make_product()
    inventories = [make_inventory()]
    repository.get_by_product.return_value = inventories

    result = service.list_by_product(
        Mock(),
        1,
    )

    assert result == inventories
    repository.get_by_product.assert_called_once()


def test_list_by_product_raises_when_not_found():
    (
        service,
        repository,
        store_repository,
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
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    inventory = make_inventory()
    repository.get_by_id.return_value = inventory
    repository.update.return_value = inventory

    data = InventoryUpdate(
        quantity_on_hand=75,
        reorder_level=15,
    )

    result = service.update_inventory(
        Mock(),
        1,
        data,
    )

    assert result == inventory
    repository.update.assert_called_once()


def test_update_inventory_raises_when_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    repository.get_by_id.return_value = None

    data = InventoryUpdate(
        quantity_on_hand=75,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.update_inventory(
            Mock(),
            999,
            data,
        )

    repository.update.assert_not_called()


def test_delete_inventory():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

    inventory = make_inventory()
    repository.get_by_id.return_value = inventory

    service.delete_inventory(
        Mock(),
        1,
    )

    repository.delete.assert_called_once_with(
        repository.delete.call_args.args[0],
        inventory,
    )


def test_delete_inventory_raises_when_not_found():
    (
        service,
        repository,
        store_repository,
        product_repository,
    ) = make_service()

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