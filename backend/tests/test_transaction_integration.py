
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Inventory,
    Product,
    Retailer,
    StockMovement,
    Store,
    Transaction,
    TransactionItem,
)
from app.schemas import TransactionCreate
from app.services.transaction import TransactionService
from conftest import test_engine


def create_sale_setup(db):
    suffix = uuid4().hex[:8]

    retailer = Retailer(
        name=f"Sale Test Retailer {suffix}",
        email=f"sale-{suffix}@example.com",
        phone=f"98{uuid4().int % 10**8:08d}",
    )
    db.add(retailer)
    db.flush()

    store = Store(
        retailer_id=retailer.id,
        name=f"Sale Test Store {suffix}",
        code=f"SALE-{suffix}",
        city="Lucknow",
        state="Uttar Pradesh",
        country="India",
    )
    db.add(store)
    db.flush()

    product = Product(
        retailer_id=retailer.id,
        name=f"Sale Test Product {suffix}",
        sku=f"SALE-{suffix}",
        cost_price=Decimal("5.00"),
        selling_price=Decimal("10.00"),
        tax_rate=Decimal("10.00"),
        unit="piece",
    )
    db.add(product)
    db.flush()

    inventory = Inventory(
        store_id=store.id,
        product_id=product.id,
        quantity_on_hand=10,
        reorder_level=2,
        reorder_quantity=5,
    )
    db.add(inventory)
    db.commit()

    return retailer, store, product, inventory


def make_sale(retailer, store, product, number):
    return TransactionCreate(
        retailer_id=retailer.id,
        store_id=store.id,
        transaction_number=number,
        payment_method="cash",
        items=[
            {
                "product_id": product.id,
                "quantity": 2,
            }
        ],
    )


def cleanup_sale_data(db, retailer_id, store_id, product_id):
    transaction_ids = select(Transaction.id).where(
        Transaction.retailer_id == retailer_id
    )

    db.query(TransactionItem).filter(
        TransactionItem.transaction_id.in_(transaction_ids)
    ).delete(synchronize_session=False)

    db.query(StockMovement).filter(
        StockMovement.inventory_id.in_(
            select(Inventory.id).where(
                Inventory.store_id == store_id
            )
        )
    ).delete(synchronize_session=False)

    db.query(Transaction).filter(
        Transaction.retailer_id == retailer_id
    ).delete(synchronize_session=False)

    db.query(Inventory).filter(
        Inventory.store_id == store_id
    ).delete(synchronize_session=False)

    db.query(Product).filter(
        Product.id == product_id
    ).delete(synchronize_session=False)

    db.query(Store).filter(
        Store.id == store_id
    ).delete(synchronize_session=False)

    db.query(Retailer).filter(
        Retailer.id == retailer_id
    ).delete(synchronize_session=False)

    db.commit()


def test_sale_persists_transaction_items_stock_and_movement():
    with Session(test_engine, expire_on_commit=False) as db:
        retailer, store, product, inventory = create_sale_setup(db)

        try:
            result = TransactionService().create_transaction(
                db,
                make_sale(
                    retailer,
                    store,
                    product,
                    f"TX-{uuid4().hex[:12]}",
                ),
            )

            saved_transaction = db.get(Transaction, result.id)
            saved_inventory = db.get(Inventory, inventory.id)

            assert saved_transaction is not None
            assert saved_transaction.total_amount == Decimal("22.00")
            assert saved_inventory.quantity_on_hand == 8

            items = db.scalars(
                select(TransactionItem).where(
                    TransactionItem.transaction_id == result.id
                )
            ).all()

            assert len(items) == 1
            assert items[0].quantity == 2
            assert items[0].line_total == Decimal("22.00")

            movements = db.scalars(
                select(StockMovement).where(
                    StockMovement.reference_type == "transaction",
                    StockMovement.reference_id == result.id,
                )
            ).all()

            assert len(movements) == 1
            assert movements[0].quantity_change == -2
        finally:
            cleanup_sale_data(
                db, retailer.id, store.id, product.id
            )


def test_sale_rolls_back_every_write_when_stock_movement_fails():
    with Session(test_engine, expire_on_commit=False) as db:
        retailer, store, product, inventory = create_sale_setup(db)
        service = TransactionService()

        def fail_to_create_movement(db_arg, movement_data):
            raise RuntimeError("Simulated stock movement failure")

        service.stock_movement_repository.create_pending = (
            fail_to_create_movement
        )

        transaction_number = f"TX-{uuid4().hex[:12]}"

        try:
            with pytest.raises(
                RuntimeError,
                match="Simulated stock movement failure",
            ):
                service.create_transaction(
                    db,
                    make_sale(
                        retailer,
                        store,
                        product,
                        transaction_number,
                    ),
                )

            saved_inventory = db.get(Inventory, inventory.id)
            assert saved_inventory.quantity_on_hand == 10

            transaction_count = db.scalar(
                select(func.count()).select_from(Transaction).where(
                    Transaction.retailer_id == retailer.id,
                    Transaction.transaction_number == transaction_number,
                )
            )
            assert transaction_count == 0

            item_count = db.scalar(
                select(func.count()).select_from(TransactionItem).where(
                    TransactionItem.transaction_id.in_(
                        select(Transaction.id).where(
                            Transaction.retailer_id == retailer.id,
                            Transaction.transaction_number == transaction_number,
                        )
                    )
                )
            )
            assert item_count == 0

            movement_count = db.scalar(
                select(func.count()).select_from(StockMovement).where(
                    StockMovement.inventory_id == inventory.id,
                    StockMovement.reference_type == "transaction",
                )
            )
            assert movement_count == 0
        finally:
            cleanup_sale_data(
                db, retailer.id, store.id, product.id
            )
