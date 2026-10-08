from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory
from app.schemas import StockInCreate, StockOutCreate
from app.services.inventory import InventoryService


def make_service():
    repository = Mock()
    store_repository = Mock()
    product_repository = Mock()
    stock_movement_repository = Mock()
    employee_repository = Mock()

    def adjust_quantity(
        db,
        inventory,
        quantity_change,
    ):
        inventory.quantity_on_hand += quantity_change
        return inventory

    repository.adjust_quantity.side_effect = adjust_quantity

    service = InventoryService(
        repository=repository,
        store_repository=store_repository,
        product_repository=product_repository,
        stock_movement_repository=stock_movement_repository,
        employee_repository=employee_repository,
    )

    return (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    )


def test_stock_in_increases_inventory():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
        reorder_quantity=50,
    )

    repository.get_by_id_for_update.return_value = inventory

    result = service.stock_in(
        Mock(),
        1,
        StockInCreate(
            quantity=25,
        ),
    )

    assert result.quantity_on_hand == 125
    assert inventory.last_restocked_at is not None

    repository.adjust_quantity.assert_called_once_with(
        repository.adjust_quantity.call_args.args[0],
        inventory,
        25,
    )

    stock_movement_repository.create_pending.assert_called_once()

    movement = (
        stock_movement_repository
        .create_pending
        .call_args.args[1]
    )

    assert movement.inventory_id == 1
    assert movement.movement_type == "stock_in"
    assert movement.quantity_change == 25


def test_stock_out_decreases_inventory():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
        reorder_quantity=50,
    )

    repository.get_by_id_for_update.return_value = inventory

    result = service.stock_out(
        Mock(),
        1,
        StockOutCreate(
            quantity=30,
        ),
    )

    assert result.quantity_on_hand == 70

    repository.adjust_quantity.assert_called_once_with(
        repository.adjust_quantity.call_args.args[0],
        inventory,
        -30,
    )

    movement = (
        stock_movement_repository
        .create_pending
        .call_args.args[1]
    )

    assert movement.inventory_id == 1
    assert movement.movement_type == "stock_out"
    assert movement.quantity_change == -30


def test_stock_in_raises_when_inventory_not_found():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    repository.get_by_id_for_update.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.stock_in(
            Mock(),
            999,
            StockInCreate(
                quantity=10,
            ),
        )

    repository.adjust_quantity.assert_not_called()
    stock_movement_repository.create_pending.assert_not_called()


def test_stock_out_raises_when_inventory_not_found():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    repository.get_by_id_for_update.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.stock_out(
            Mock(),
            999,
            StockOutCreate(
                quantity=10,
            ),
        )

    repository.adjust_quantity.assert_not_called()
    stock_movement_repository.create_pending.assert_not_called()


def test_stock_out_rejects_insufficient_stock():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=5,
        reorder_level=10,
        reorder_quantity=50,
    )

    repository.get_by_id_for_update.return_value = inventory

    with pytest.raises(
        ResourceConflictError,
        match="Insufficient stock.",
    ):
        service.stock_out(
            Mock(),
            1,
            StockOutCreate(
                quantity=10,
            ),
        )

    assert inventory.quantity_on_hand == 5

    repository.adjust_quantity.assert_not_called()
    stock_movement_repository.create_pending.assert_not_called()


def test_stock_in_validates_employee():
    (
        service,
        repository,
        stock_movement_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
        reorder_quantity=50,
    )

    repository.get_by_id_for_update.return_value = inventory
    employee_repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.stock_in(
            Mock(),
            1,
            StockInCreate(
                quantity=10,
                employee_id=999,
            ),
        )

    repository.adjust_quantity.assert_not_called()
    stock_movement_repository.create_pending.assert_not_called()