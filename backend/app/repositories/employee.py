from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeRepository:
    def create(
        self,
        db: Session,
        employee_data: EmployeeCreate,
    ) -> Employee:
        employee = Employee(
            **employee_data.model_dump()
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)

        return employee

    def get_by_id(
        self,
        db: Session,
        employee_id: int,
    ) -> Employee | None:
        statement = select(Employee).where(
            Employee.id == employee_id
        )

        return db.scalar(statement)

    def get_by_email(
        self,
        db: Session,
        retailer_id: int,
        email: str,
    ) -> Employee | None:
        statement = select(Employee).where(
            Employee.retailer_id == retailer_id,
            Employee.email == email,
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Employee]:
        statement = (
            select(Employee)
            .order_by(Employee.id)
            .offset(offset)
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )

    def update(
        self,
        db: Session,
        employee: Employee,
        employee_data: EmployeeUpdate,
    ) -> Employee:
        update_data = employee_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(employee, field, value)

        db.commit()
        db.refresh(employee)

        return employee

    def delete(
        self,
        db: Session,
        employee: Employee,
    ) -> None:
        db.delete(employee)
        db.commit()