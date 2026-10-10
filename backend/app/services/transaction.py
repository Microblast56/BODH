
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Inventory, Product, Transaction
from app.repositories import (
    EmployeeRepository,
    InventoryRepository,
    ProductRepository,
    RetailerRepository,
    StockMovementRepository,
    StoreRepository,
    TransactionItemRepository,
    TransactionRepository,
)
from app.schemas import StockMovementCreate, TransactionCreate


ZERO = Decimal("0.00")
CENT = Decimal("0.01")


class TransactionService:
    """Coordinates a complete sale within one database transaction."""

    def __init__(
        self,
        transaction_repository: TransactionRepository | None = None,
        transaction_item_repository: TransactionItemRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
        store_repository: StoreRepository | None = None,
        employee_repository: EmployeeRepository | None = None,
        product_repository: ProductRepository | None = None,
        inventory_repository: InventoryRepository | None = None,
        stock_movement_repository: StockMovementRepository | None = None,
    ) -> None:
        self.transaction_repository = (
            transaction_repository or TransactionRepository()
        )
        self.transaction_item_repository = (
            transaction_item_repository or TransactionItemRepository()
        )
        self.retailer_repository = retailer_repository or RetailerRepository()
        self.store_repository = store_repository or StoreRepository()
        self.employee_repository = employee_repository or EmployeeRepository()
        self.product_repository = product_repository or ProductRepository()
        self.inventory_repository = inventory_repository or InventoryRepository()
        self.stock_movement_repository = (
            stock_movement_repository or StockMovementRepository()
        )

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(CENT, rounding=ROUND_HALF_UP)

    def _allocate_transaction_discount(
        self,
        line_bases: list[Decimal],
        discount: Decimal,
    ) -> list[Decimal]:
        """Allocate an order-level discount proportionally across lines."""
        allocations = [ZERO for _ in line_bases]

        if discount == ZERO:
            return allocations

        eligible = [
            index
            for index, base in enumerate(line_bases)
            if base > ZERO
        ]

        if not eligible:
            raise ResourceConflictError(
                "A transaction discount cannot be applied when no "
                "discountable amount remains."
            )

        total_base = sum(line_bases, ZERO)
        remaining = discount

        for index in eligible[:-1]:
            allocation = self._money(
                discount * line_bases[index] / total_base
            )
            allocation = min(allocation, remaining)
            allocations[index] = allocation
            remaining = self._money(remaining - allocation)

        allocations[eligible[-1]] = remaining
        return allocations

    def create_transaction(
        self,
        db: Session,
        transaction_data: TransactionCreate,
    ) -> Transaction:
        """Create a sale, deduct inventory, and record stock movements atomically."""
        committed = False

        try:
            # ----------------------------------------------------------
            # 1. Validate retailer, store, and employee
            # ----------------------------------------------------------
            retailer = self.retailer_repository.get_by_id(
                db, transaction_data.retailer_id
            )
            if retailer is None:
                raise ResourceNotFoundError("Retailer not found.")
            if not retailer.is_active:
                raise ResourceConflictError("Retailer is inactive.")

            store = self.store_repository.get_by_id(
                db, transaction_data.store_id
            )
            if store is None:
                raise ResourceNotFoundError("Store not found.")
            if not store.is_active:
                raise ResourceConflictError("Store is inactive.")
            if store.retailer_id != retailer.id:
                raise ResourceConflictError(
                    "The store does not belong to the specified retailer."
                )

            employee = None
            if transaction_data.employee_id is not None:
                employee = self.employee_repository.get_by_id(
                    db, transaction_data.employee_id
                )
                if employee is None:
                    raise ResourceNotFoundError("Employee not found.")
                if not employee.is_active:
                    raise ResourceConflictError("Employee is inactive.")
                if employee.retailer_id != retailer.id:
                    raise ResourceConflictError(
                        "The employee does not belong to the specified retailer."
                    )
                if (
                    employee.store_id is not None
                    and employee.store_id != store.id
                ):
                    raise ResourceConflictError(
                        "The employee is assigned to a different store."
                    )

            # ----------------------------------------------------------
            # 2. Reject duplicate transaction numbers
            # ----------------------------------------------------------
            existing = self.transaction_repository.get_by_number(
                db,
                transaction_data.retailer_id,
                transaction_data.transaction_number,
            )
            if existing is not None:
                raise ResourceConflictError(
                    "This transaction number already exists for the retailer."
                )

            # ----------------------------------------------------------
            # 3. Validate products and calculate gross line amounts
            # ----------------------------------------------------------
            prepared_lines: list[dict] = []
            required_quantities: dict[int, int] = {}
            gross_subtotal = ZERO
            line_discount_total = ZERO

            for requested_item in transaction_data.items:
                product = self.product_repository.get_by_id(
                    db, requested_item.product_id
                )
                if product is None:
                    raise ResourceNotFoundError(
                        f"Product {requested_item.product_id} not found."
                    )
                if not product.is_active:
                    raise ResourceConflictError(
                        f"Product {product.id} is inactive."
                    )
                if product.retailer_id != retailer.id:
                    raise ResourceConflictError(
                        f"Product {product.id} does not belong to this retailer."
                    )

                unit_price = self._money(
                    Decimal(str(product.selling_price))
                )
                quantity = requested_item.quantity
                gross_line = self._money(unit_price * quantity)
                line_discount = self._money(
                    Decimal(str(requested_item.discount_amount))
                )

                if line_discount > gross_line:
                    raise ResourceConflictError(
                        f"Discount exceeds the gross amount for product {product.id}."
                    )

                remaining_line = self._money(gross_line - line_discount)

                prepared_lines.append(
                    {
                        "product": product,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "gross_line": gross_line,
                        "line_discount": line_discount,
                        "remaining_line": remaining_line,
                    }
                )

                required_quantities[product.id] = (
                    required_quantities.get(product.id, 0) + quantity
                )
                gross_subtotal += gross_line
                line_discount_total += line_discount

            gross_subtotal = self._money(gross_subtotal)
            line_discount_total = self._money(line_discount_total)

            order_discount = self._money(
                Decimal(str(transaction_data.discount_amount))
            )
            available_for_order_discount = self._money(
                gross_subtotal - line_discount_total
            )

            if order_discount > available_for_order_discount:
                raise ResourceConflictError(
                    "The transaction discount exceeds the amount remaining "
                    "after line discounts."
                )

            # ----------------------------------------------------------
            # 4. Lock inventory rows in deterministic product-ID order
            # ----------------------------------------------------------
            locked_inventory: dict[int, Inventory] = {}

            for product_id in sorted(required_quantities):
                inventory = (
                    self.inventory_repository.get_by_store_and_product_for_update(
                        db,
                        store.id,
                        product_id,
                    )
                )

                if inventory is None:
                    raise ResourceNotFoundError(
                        f"Inventory for product {product_id} was not found "
                        f"in store {store.id}."
                    )

                required = required_quantities[product_id]
                if inventory.quantity_on_hand < required:
                    raise ResourceConflictError(
                        f"Insufficient stock for product {product_id}. "
                        f"Available: {inventory.quantity_on_hand}; "
                        f"required: {required}."
                    )

                locked_inventory[product_id] = inventory

            # ----------------------------------------------------------
            # 5. Allocate the order discount and calculate tax
            # ----------------------------------------------------------
            order_discount_allocations = self._allocate_transaction_discount(
                [line["remaining_line"] for line in prepared_lines],
                order_discount,
            )

            subtotal = gross_subtotal
            total_discount = self._money(
                line_discount_total + order_discount
            )
            total_tax = ZERO
            total_amount = ZERO

            for index, line in enumerate(prepared_lines):
                allocated_discount = order_discount_allocations[index]
                combined_line_discount = self._money(
                    line["line_discount"] + allocated_discount
                )
                taxable_amount = self._money(
                    line["gross_line"] - combined_line_discount
                )

                tax_rate = Decimal(
                    str(line["product"].tax_rate or 0)
                )
                line_tax = self._money(
                    taxable_amount * tax_rate / Decimal("100")
                )
                line_total = self._money(taxable_amount + line_tax)

                line["discount_amount"] = combined_line_discount
                line["tax_amount"] = line_tax
                line["line_total"] = line_total

                total_tax += line_tax
                total_amount += line_total

            total_tax = self._money(total_tax)
            total_amount = self._money(total_amount)

            # ----------------------------------------------------------
            # 6. Create the transaction and its line items
            # ----------------------------------------------------------
            transaction = self.transaction_repository.create_pending(
                db,
                {
                    "retailer_id": retailer.id,
                    "store_id": store.id,
                    "employee_id": employee.id if employee else None,
                    "transaction_number": transaction_data.transaction_number,
                    "status": "completed",
                    "payment_method": transaction_data.payment_method,
                    "subtotal": subtotal,
                    "tax_amount": total_tax,
                    "discount_amount": total_discount,
                    "total_amount": total_amount,
                    "notes": transaction_data.notes,
                },
            )

            for line in prepared_lines:
                self.transaction_item_repository.create_pending(
                    db,
                    {
                        "transaction_id": transaction.id,
                        "product_id": line["product"].id,
                        "quantity": line["quantity"],
                        "unit_price": line["unit_price"],
                        "discount_amount": line["discount_amount"],
                        "tax_amount": line["tax_amount"],
                        "line_total": line["line_total"],
                    },
                )

            # ----------------------------------------------------------
            # 7. Deduct inventory and record stock movements
            # ----------------------------------------------------------
            for product_id in sorted(required_quantities):
                quantity = required_quantities[product_id]
                inventory = locked_inventory[product_id]

                self.inventory_repository.adjust_quantity(
                    db,
                    inventory,
                    -quantity,
                )

                movement_data = StockMovementCreate(
                    inventory_id=inventory.id,
                    employee_id=employee.id if employee else None,
                    movement_type="stock_out",
                    quantity_change=-quantity,
                    reference_type="transaction",
                    reference_id=transaction.id,
                    notes=(
                        f"Sale transaction {transaction.transaction_number}"
                    ),
                )

                self.stock_movement_repository.create_pending(
                    db,
                    movement_data,
                )

            # ----------------------------------------------------------
            # 8. Commit exactly once for the entire sale
            # ----------------------------------------------------------
            db.commit()
            committed = True

            db.refresh(transaction)
            return transaction

        except IntegrityError:
            if committed:
                raise

            db.rollback()

            # A concurrent request may have inserted the same number
            # after our initial duplicate check.
            try:
                existing = self.transaction_repository.get_by_number(
                    db,
                    transaction_data.retailer_id,
                    transaction_data.transaction_number,
                )
            except Exception:
                # A failed diagnostic lookup must not mask the original
                # database integrity error.
                existing = None

            if existing is not None:
                raise ResourceConflictError(
                    "This transaction number already exists for the retailer."
                )

            raise

        except Exception:
            if not committed:
                db.rollback()
            raise

    def get_transaction(
        self,
        db: Session,
        transaction_id: int,
    ) -> Transaction:
        transaction = self.transaction_repository.get_by_id(
            db,
            transaction_id,
        )

        if transaction is None:
            raise ResourceNotFoundError(
                "Transaction not found."
            )

        return transaction

    def list_transactions(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Transaction]:
        return self.transaction_repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )
