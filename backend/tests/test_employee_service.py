from unittest.mock import Mock

import pytest

from app.core.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services import EmployeeService


def make_employee(
    employee_id: int = 1,
    retailer_id: int = 1,
    name: str = "John Doe",
    email: str | None = "john@example.com",
) -> Employee:
    employee = Employee(
        id=employee_id,
        retailer_id=retailer_id,
        name=name,
        email=email,
        phone="9876543210",
        role="Manager",
        is_active=True,
    )

    return employee


def make_service():
    repository = Mock()
    retailer_repository = Mock()

    service = EmployeeService(
        repository=repository,
        retailer_repository=retailer_repository,
    )

    return service, repository, retailer_repository


def test_create_employee():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_email.return_value = None

    employee = make_employee()

    repository.create.return_value = employee

    employee_data = EmployeeCreate(
        retailer_id=1,
        name="John Doe",
        email="john@example.com",
        phone="9876543210",
        role="Manager",
    )

    result = service.create_employee(
        Mock(),
        employee_data,
    )

    assert result == employee
    repository.create.assert_called_once()


def test_create_employee_without_email():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    employee = make_employee(email=None)

    repository.create.return_value = employee

    employee_data = EmployeeCreate(
        retailer_id=1,
        name="John Doe",
        role="Manager",
    )

    result = service.create_employee(
        Mock(),
        employee_data,
    )

    assert result == employee
    repository.get_by_email.assert_not_called()
    repository.create.assert_called_once()


def test_create_employee_raises_when_retailer_not_found():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = None

    employee_data = EmployeeCreate(
        retailer_id=999,
        name="John Doe",
        email="john@example.com",
        role="Manager",
    )

    with pytest.raises(
        ResourceNotFoundError,
        match="Retailer not found.",
    ):
        service.create_employee(
            Mock(),
            employee_data,
        )

    repository.create.assert_not_called()


def test_create_employee_rejects_duplicate_email():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=1,
        is_active=True,
    )

    repository.get_by_email.return_value = make_employee()

    employee_data = EmployeeCreate(
        retailer_id=1,
        name="Another Employee",
        email="john@example.com",
        role="Staff",
    )

    with pytest.raises(
        ResourceConflictError,
        match="An employee with this email already exists for this retailer.",
    ):
        service.create_employee(
            Mock(),
            employee_data,
        )

    repository.create.assert_not_called()


def test_create_employee_allows_same_email_for_different_retailers():
    service, repository, retailer_repository = make_service()

    retailer_repository.get_by_id.return_value = Mock(
        id=2,
        is_active=True,
    )

    repository.get_by_email.return_value = None

    employee = make_employee(
        retailer_id=2,
    )

    repository.create.return_value = employee

    employee_data = EmployeeCreate(
        retailer_id=2,
        name="John Doe",
        email="john@example.com",
        role="Manager",
    )

    result = service.create_employee(
        Mock(),
        employee_data,
    )

    assert result == employee
    repository.create.assert_called_once()


def test_get_employee():
    service, repository, _ = make_service()

    employee = make_employee()

    repository.get_by_id.return_value = employee

    result = service.get_employee(
        Mock(),
        1,
    )

    assert result == employee
    repository.get_by_id.assert_called_once()


def test_get_employee_raises_when_not_found():
    service, repository, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.get_employee(
            Mock(),
            999,
        )


def test_list_employees():
    service, repository, _ = make_service()

    employees = [
        make_employee(employee_id=1),
        make_employee(
            employee_id=2,
            name="Jane Doe",
            email="jane@example.com",
        ),
    ]

    repository.get_all.return_value = employees

    result = service.list_employees(
        Mock(),
        offset=10,
        limit=20,
    )

    assert result == employees
    repository.get_all.assert_called_once_with(
        repository.get_all.call_args.args[0],
        offset=10,
        limit=20,
    )


def test_update_employee():
    service, repository, _ = make_service()

    employee = make_employee()

    repository.get_by_id.return_value = employee
    repository.update.return_value = employee

    update_data = EmployeeUpdate(
        name="Updated Name",
        role="Senior Manager",
    )

    result = service.update_employee(
        Mock(),
        1,
        update_data,
    )

    assert result == employee
    repository.update.assert_called_once_with(
        repository.update.call_args.args[0],
        employee,
        update_data,
    )


def test_update_employee_rejects_duplicate_email():
    service, repository, _ = make_service()

    employee = make_employee(
        employee_id=1,
        email="john@example.com",
    )

    duplicate_employee = make_employee(
        employee_id=2,
        email="jane@example.com",
    )

    repository.get_by_id.return_value = employee
    repository.get_by_email.return_value = duplicate_employee

    update_data = EmployeeUpdate(
        email="jane@example.com",
    )

    with pytest.raises(
        ResourceConflictError,
        match="An employee with this email already exists for this retailer.",
    ):
        service.update_employee(
            Mock(),
            1,
            update_data,
        )

    repository.update.assert_not_called()


def test_update_employee_allows_same_email():
    service, repository, _ = make_service()

    employee = make_employee(
        employee_id=1,
        email="john@example.com",
    )

    repository.get_by_id.return_value = employee
    repository.update.return_value = employee

    update_data = EmployeeUpdate(
        email="john@example.com",
        name="Updated Name",
    )

    result = service.update_employee(
        Mock(),
        1,
        update_data,
    )

    assert result == employee
    repository.update.assert_called_once()


def test_update_employee_without_email_does_not_check_duplicate():
    service, repository, _ = make_service()

    employee = make_employee()

    repository.get_by_id.return_value = employee
    repository.update.return_value = employee

    update_data = EmployeeUpdate(
        name="Updated Name",
    )

    result = service.update_employee(
        Mock(),
        1,
        update_data,
    )

    assert result == employee
    repository.get_by_email.assert_not_called()
    repository.update.assert_called_once()


def test_delete_employee():
    service, repository, _ = make_service()

    employee = make_employee()

    repository.get_by_id.return_value = employee

    service.delete_employee(
        Mock(),
        1,
    )

    repository.delete.assert_called_once()


def test_delete_employee_raises_when_not_found():
    service, repository, _ = make_service()

    repository.get_by_id.return_value = None

    with pytest.raises(
        ResourceNotFoundError,
        match="Employee not found.",
    ):
        service.delete_employee(
            Mock(),
            999,
        )

    repository.delete.assert_not_called()
