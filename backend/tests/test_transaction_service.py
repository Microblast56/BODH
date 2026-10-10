
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.schemas import TransactionCreate
from app.services.transaction import TransactionService


def make_service(stock_quantity=100):
    db = Mock()

    transaction_repository = Mock()
    transaction_repository.get_by_number.return_value = None
    transaction_item_repository = Mock()
    retailer_repository = Mock()
    store_repository = Mock()
    employee_repository = Mock()
    product_repository = Mock()
    inventory_repository = Mock()
    stock_movement_repository = Mock()

    retailer_repository.get_by_id.return_value = SimpleNamespace(
        id=1,
        is_active=True,
    )

    store_repository.get_by_id.return_value = SimpleNamespace(
        id=1,
        retailer_id=1,
        is_active=True,
    )

    product = SimpleNamespace(
        id=1,
        retailer_id=1,
        is_active=True,
        selling_price=Decimal("10.00"),
        tax_rate=Decimal("10.00"),
    )
    product_repository.get_by_id.return_value = product

    inventory = SimpleNamespace(
        id=1,
        store_id=1,
        product_id=1,
        quantity_on_hand=stock_quantity,
    )

    inventory_repository.get_by_store_and_product_for_update.return_value = (
        inventory
    )

    def adjust_quantity(db_arg, inventory_arg, quantity_change):
        inventory_arg.quantity_on_hand += quantity_change
        return inventory_arg

    inventory_repository.adjust_quantity.side_effect = adjust_quantity

    transaction = SimpleNamespace(
        id=50,
        transaction_number="TX-001",
    )
    transaction_repository.create_pending.return_value = transaction

    service = TransactionService(
        transaction_repository=transaction_repository,
        transaction_item_repository=transaction_item_repository,
        retailer_repository=retailer_repository,
        store_repository=store_repository,
        employee_repository=employee_repository,
        product_repository=product_repository,
        inventory_repository=inventory_repository,
        stock_movement_repository=stock_movement_repository,
    )

    return {
        "db": db,
        "service": service,
        "transaction_repository": transaction_repository,
        "transaction_item_repository": transaction_item_repository,
        "retailer_repository": retailer_repository,
        "store_repository": store_repository,
        "product_repository": product_repository,
        "inventory_repository": inventory_repository,
        "stock_movement_repository": stock_movement_repository,
        "inventory": inventory,
        "product": product,
        "transaction": transaction,
    }


def make_transaction_data(
    transaction_number="TX-001",
    quantity=2,
    product_id=1,
    discount_amount=Decimal("0.00"),
    items=None,
):
    return TransactionCreate(
        retailer_id=1,
        store_id=1,
        transaction_number=transaction_number,
        payment_method="cash",
        discount_amount=discount_amount,
        items=items or [
            {
                "product_id": product_id,
                "quantity": quantity,
            }
        ],
    )


def test_successful_sale_calculates_totals_and_deducts_stock():
    ctx = make_service()
    db = ctx["db"]

    result = ctx["service"].create_transaction(
        db,
        make_transaction_data(quantity=2),
    )

    assert result == ctx["transaction"]
    assert ctx["inventory"].quantity_on_hand == 98

    transaction_data = (
        ctx["transaction_repository"].create_pending.call_args.args[1]
    )
    assert transaction_data["subtotal"] == Decimal("20.00")
    assert transaction_data["tax_amount"] == Decimal("2.00")
    assert transaction_data["discount_amount"] == Decimal("0.00")
    assert transaction_data["total_amount"] == Decimal("22.00")

    item_data = (
        ctx["transaction_item_repository"].create_pending.call_args.args[1]
    )
    assert item_data["quantity"] == 2
    assert item_data["unit_price"] == Decimal("10.00")
    assert item_data["tax_amount"] == Decimal("2.00")
    assert item_data["line_total"] == Decimal("22.00")

    movement = (
        ctx["stock_movement_repository"].create_pending.call_args.args[1]
    )
    assert movement.movement_type == "stock_out"
    assert movement.quantity_change == -2
    assert movement.reference_type == "transaction"
    assert movement.reference_id == 50

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_insufficient_stock_rolls_back_without_creating_sale():
    ctx = make_service(stock_quantity=1)
    db = ctx["db"]

    with pytest.raises(ResourceConflictError, match="Insufficient stock"):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(quantity=2),
        )

    ctx["transaction_repository"].create_pending.assert_not_called()
    ctx["transaction_item_repository"].create_pending.assert_not_called()
    ctx["stock_movement_repository"].create_pending.assert_not_called()
    ctx["inventory_repository"].adjust_quantity.assert_not_called()

    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_duplicate_transaction_number_is_rejected():
    ctx = make_service()
    ctx["transaction_repository"].get_by_number.return_value = (
        SimpleNamespace(id=99)
    )
    db = ctx["db"]

    with pytest.raises(
        ResourceConflictError,
        match="transaction number already exists",
    ):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    ctx["transaction_repository"].create_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_missing_product_rolls_back_sale():
    ctx = make_service()
    ctx["product_repository"].get_by_id.return_value = None
    db = ctx["db"]

    with pytest.raises(ResourceNotFoundError, match="Product 1 not found"):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    ctx["transaction_repository"].create_pending.assert_not_called()
    ctx["inventory_repository"].adjust_quantity.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_inactive_product_is_rejected():
    ctx = make_service()
    ctx["product"].is_active = False
    db = ctx["db"]

    with pytest.raises(ResourceConflictError, match="Product 1 is inactive"):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    ctx["transaction_repository"].create_pending.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_repeated_product_lines_aggregate_stock_requirement():
    ctx = make_service(stock_quantity=4)
    db = ctx["db"]

    data = make_transaction_data(
        items=[
            {"product_id": 1, "quantity": 2},
            {"product_id": 1, "quantity": 3},
        ]
    )

    with pytest.raises(ResourceConflictError, match="Insufficient stock"):
        ctx["service"].create_transaction(db, data)

    # The product appears twice, but its combined requirement is five units.
    ctx["inventory_repository"].get_by_store_and_product_for_update.assert_called_once_with(
        db,
        1,
        1,
    )
    ctx["transaction_repository"].create_pending.assert_not_called()
    ctx["inventory_repository"].adjust_quantity.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


def test_repeated_product_lines_create_one_aggregated_stock_movement():
    ctx = make_service(stock_quantity=5)
    db = ctx["db"]

    data = make_transaction_data(
        items=[
            {"product_id": 1, "quantity": 2},
            {"product_id": 1, "quantity": 3},
        ]
    )

    ctx["service"].create_transaction(db, data)

    assert ctx["inventory"].quantity_on_hand == 0
    assert (
        ctx["inventory_repository"]
        .get_by_store_and_product_for_update.call_count
        == 1
    )
    assert (
        ctx["transaction_item_repository"].create_pending.call_count
        == 2
    )
    assert (
        ctx["stock_movement_repository"].create_pending.call_count
        == 1
    )

    movement = (
        ctx["stock_movement_repository"].create_pending.call_args.args[1]
    )
    assert movement.quantity_change == -5

    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_stock_movement_failure_triggers_rollback():
    ctx = make_service()
    db = ctx["db"]

    ctx["stock_movement_repository"].create_pending.side_effect = RuntimeError(
        "Simulated stock movement failure"
    )

    with pytest.raises(RuntimeError, match="Simulated stock movement failure"):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    # The mock cannot emulate a real database rollback, but it can verify
    # that the service does not commit and requests rollback on failure.
    db.commit.assert_not_called()
    db.rollback.assert_called_once()

def test_refresh_failure_after_commit_does_not_attempt_rollback():
    ctx = make_service()
    db = ctx["db"]

    db.refresh.side_effect = RuntimeError(
        "Simulated refresh failure"
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated refresh failure",
    ):
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ctx["transaction"])
    db.rollback.assert_not_called()


def test_integrity_error_is_preserved_if_duplicate_lookup_fails():
    from sqlalchemy.exc import IntegrityError

    ctx = make_service()
    db = ctx["db"]

    original_error = IntegrityError(
        "INSERT",
        {},
        Exception("simulated constraint violation"),
    )

    ctx["transaction_repository"].create_pending.side_effect = (
        original_error
    )
    ctx["transaction_repository"].get_by_number.side_effect = [
        None,
        RuntimeError("Simulated lookup failure"),
    ]

    with pytest.raises(IntegrityError) as exc_info:
        ctx["service"].create_transaction(
            db,
            make_transaction_data(),
        )

    assert exc_info.value is original_error
    db.rollback.assert_called_once()