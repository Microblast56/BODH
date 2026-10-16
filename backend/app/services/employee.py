from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Employee
from app.repositories import (
    EmployeeRepository,
    RetailerRepository,
    StoreRepository,
)
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository | None = None,
        retailer_repository: RetailerRepository | None = None,
        store_repository: StoreRepository | None = None,
    ) -> None:
        self.repository = repository or EmployeeRepository()
        self.retailer_repository = (
            retailer_repository or RetailerRepository()
        )
        self.store_repository = store_repository or StoreRepository()

    def create_employee(
        self,
        db: Session,
        employee_data: EmployeeCreate,
    ) -> Employee:
        retailer = self.retailer_repository.get_by_id(
            db,
            employee_data.retailer_id,
        )

        if retailer is None:
            raise ResourceNotFoundError("Retailer not found.")

        if employee_data.store_id is not None:
            store = self.store_repository.get_by_id(
                db,
                employee_data.store_id,
            )

            if store is None:
                raise ResourceNotFoundError("Store not found.")

            if store.retailer_id != employee_data.retailer_id:
                raise ResourceConflictError(
                    "The store does not belong to the specified retailer."
                )

        if employee_data.email:
            existing_employee = self.repository.get_by_email(
                db,
                employee_data.retailer_id,
                employee_data.email,
            )

            if existing_employee:
                raise ResourceConflictError(
                    "An employee with this email already exists for this retailer."
                )

        return self.repository.create(db, employee_data)

    def get_employee(
        self,
        db: Session,
        employee_id: int,
    ) -> Employee:
        employee = self.repository.get_by_id(db, employee_id)

        if employee is None:
            raise ResourceNotFoundError("Employee not found.")

        return employee

    def list_employees(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Employee]:
        return self.repository.get_all(
            db,
            offset=offset,
            limit=limit,
        )

    def update_employee(
        self,
        db: Session,
        employee_id: int,
        employee_data: EmployeeUpdate,
    ) -> Employee:
        employee = self.get_employee(db, employee_id)

        if (
            "store_id" in employee_data.model_fields_set
            and employee_data.store_id is not None
        ):
            store = self.store_repository.get_by_id(
                db,
                employee_data.store_id,
            )

            if store is None:
                raise ResourceNotFoundError("Store not found.")

            if store.retailer_id != employee.retailer_id:
                raise ResourceConflictError(
                    "The store does not belong to the specified retailer."
                )

        if (
            "email" in employee_data.model_fields_set
            and employee_data.email is not None
            and employee_data.email != employee.email
        ):
            existing_employee = self.repository.get_by_email(
                db,
                employee.retailer_id,
                employee_data.email,
            )

            if existing_employee:
                raise ResourceConflictError(
                    "An employee with this email already exists for this retailer."
                )

        return self.repository.update(
            db,
            employee,
            employee_data,
        )

    def delete_employee(
        self,
        db: Session,
        employee_id: int,
    ) -> None:
        employee = self.get_employee(db, employee_id)
        self.repository.delete(db, employee)