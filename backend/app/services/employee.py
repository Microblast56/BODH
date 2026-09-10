from sqlalchemy.orm import Session

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Employee
from app.repositories import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository | None = None,
    ) -> None:
        self.repository = repository or EmployeeRepository()

    def create_employee(
        self,
        db: Session,
        employee_data: EmployeeCreate,
    ) -> Employee:
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

        return self.repository.create(
            db,
            employee_data,
        )

    def get_employee(
        self,
        db: Session,
        employee_id: int,
    ) -> Employee:
        employee = self.repository.get_by_id(
            db,
            employee_id,
        )

        if employee is None:
            raise ResourceNotFoundError(
                "Employee not found."
            )

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
        employee = self.get_employee(
            db,
            employee_id,
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
        employee = self.get_employee(
            db,
            employee_id,
        )

        self.repository.delete(
            db,
            employee,
        )