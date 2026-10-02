from unittest.mock import Mock

import pytest

from app.core.exceptions import ResourceNotFoundError
from app.models import Employee, Inventory, StockMovement
from app.schemas import StockMovementCreate, StockMovementUpdate
from app.services import StockMovementService


def make_service():
    repository = Mock()
    inventory_repository = Mock()
    employee_repository = Mock()

    service = StockMovementService(
        repository=repository,
        inventory_repository=inventory_repository,
        employee_repository=employee_repository,
    )

    return (
        service,
        repository,
        inventory_repository,
        employee_repository,
    )


def test_create_stock_movement():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
    )

    employee = Employee(
        id=1,
        retailer_id=1,
        store_id=1,
        name="John",
        role="Manager",
    )

    movement = StockMovement(
        id=1,
        inventory_id=1,
        employee_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    inventory_repository.get_by_id.return_value = inventory
    employee_repository.get_by_id.return_value = employee
    repository.create.return_value = movement

    movement_data = StockMovementCreate(
        inventory_id=1,
        employee_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    result = service.create_stock_movement(
        Mock(),
        movement_data,
    )

    assert result == movement
    inventory_repository.get_by_id.assert_called_once_with(
        repository.create.call_args.args[0],
        1,
    )
    employee_repository.get_by_id.assert_called_once()
    repository.create.assert_called_once()


def test_create_stock_movement_without_employee():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
    )

    movement = StockMovement(
        id=1,
        inventory_id=1,
        employee_id=None,
        movement_type="adjustment",
        quantity_change=10,
    )

    inventory_repository.get_by_id.return_value = inventory
    repository.create.return_value = movement

    movement_data = StockMovementCreate(
        inventory_id=1,
        movement_type="adjustment",
        quantity_change=10,
    )

    result = service.create_stock_movement(
        Mock(),
        movement_data,
    )

    assert result == movement
    employee_repository.get_by_id.assert_not_called()
    repository.create.assert_called_once()


def test_create_stock_movement_raises_when_inventory_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory_repository.get_by_id.return_value = None

    movement_data = StockMovementCreate(
        inventory_id=999,
        movement_type="sale",
        quantity_change=-5,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.create_stock_movement(
            Mock(),
            movement_data,
        )

    repository.create.assert_not_called()


def test_create_stock_movement_raises_when_employee_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory_repository.get_by_id.return_value = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
    )

    employee_repository.get_by_id.return_value = None

    movement_data = StockMovementCreate(
        inventory_id=1,
        employee_id=999,
        movement_type="sale",
        quantity_change=-5,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.create_stock_movement(
            Mock(),
            movement_data,
        )

    repository.create.assert_not_called()


def test_get_stock_movement():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    movement = StockMovement(
        id=1,
        inventory_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    repository.get_by_id.return_value = movement

    result = service.get_stock_movement(
        Mock(),
        1,
    )

    assert result == movement
    repository.get_by_id.assert_called_once()


def test_get_stock_movement_raises_when_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Stock movement not found.",
    ):
        service.get_stock_movement(
            Mock(),
            999,
        )


def test_list_stock_movements():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    movements = [
        StockMovement(
            id=1,
            inventory_id=1,
            movement_type="sale",
            quantity_change=-5,
        ),
        StockMovement(
            id=2,
            inventory_id=1,
            movement_type="restock",
            quantity_change=20,
        ),
    ]

    repository.get_all.return_value = movements

    result = service.list_stock_movements(
        Mock(),
        offset=0,
        limit=100,
    )

    assert result == movements
    repository.get_all.assert_called_once_with(
        repository.get_all.call_args.args[0],
        offset=0,
        limit=100,
    )


def test_list_by_inventory():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory = Inventory(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=100,
        reorder_level=10,
    )

    movements = [
        StockMovement(
            id=1,
            inventory_id=1,
            movement_type="sale",
            quantity_change=-5,
        )
    ]

    inventory_repository.get_by_id.return_value = inventory
    repository.get_by_inventory.return_value = movements

    result = service.list_by_inventory(
        Mock(),
        1,
    )

    assert result == movements
    repository.get_by_inventory.assert_called_once()


def test_list_by_inventory_raises_when_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    inventory_repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Inventory not found.",
    ):
        service.list_by_inventory(
            Mock(),
            999,
        )

    repository.get_by_inventory.assert_not_called()


def test_list_by_employee():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    employee = Employee(
        id=1,
        retailer_id=1,
        store_id=1,
        name="John",
        role="Manager",
    )

    movements = [
        StockMovement(
            id=1,
            inventory_id=1,
            employee_id=1,
            movement_type="sale",
            quantity_change=-5,
        )
    ]

    employee_repository.get_by_id.return_value = employee
    repository.get_by_employee.return_value = movements

    result = service.list_by_employee(
        Mock(),
        1,
    )

    assert result == movements
    repository.get_by_employee.assert_called_once()


def test_list_by_employee_raises_when_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    employee_repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.list_by_employee(
            Mock(),
            999,
        )

    repository.get_by_employee.assert_not_called()


def test_update_stock_movement():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    movement = StockMovement(
        id=1,
        inventory_id=1,
        employee_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    repository.get_by_id.return_value = movement

    updated_movement = StockMovement(
        id=1,
        inventory_id=1,
        employee_id=1,
        movement_type="return",
        quantity_change=5,
    )

    repository.update.return_value = updated_movement

    movement_data = StockMovementUpdate(
        movement_type="return",
        quantity_change=5,
    )

    result = service.update_stock_movement(
        Mock(),
        1,
        movement_data,
    )

    assert result == updated_movement
    repository.update.assert_called_once()


def test_update_stock_movement_raises_when_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    repository.get_by_id.return_value = None

    movement_data = StockMovementUpdate(
        movement_type="return",
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Stock movement not found.",
    ):
        service.update_stock_movement(
            Mock(),
            999,
            movement_data,
        )

    repository.update.assert_not_called()


def test_update_stock_movement_raises_when_employee_not_found():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    movement = StockMovement(
        id=1,
        inventory_id=1,
        employee_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    repository.get_by_id.return_value = movement
    employee_repository.get_by_id.return_value = None

    movement_data = StockMovementUpdate(
        employee_id=999,
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.update_stock_movement(
            Mock(),
            1,
            movement_data,
        )

    repository.update.assert_not_called()


def test_delete_stock_movement():
    (
        service,
        repository,
        inventory_repository,
        employee_repository,
    ) = make_service()

    movement = StockMovement(
        id=1,
        inventory_id=1,
        movement_type="sale",
        quantity_change=-5,
    )

    repository.get_by_id.return_value = movement

    service.delete_stock_movement(
        Mock(),
        1,
    )

    repository.delete.assert_called_once_with(
        repository.delete.call_args.args[0],
        movement,
    )