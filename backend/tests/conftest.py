import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_db
from app.db.base import Base
from app.models import (
    Category,
    Employee,
    Inventory,
    Outlet,
    Product,
    ProductSupplier,
    Restaurant,
    Retailer,
    StockMovement,
    Store,
    Supplier,
)


load_dotenv(".env.test")


TEST_DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{os.getenv('TEST_DATABASE_USER', 'postgres')}:"
    f"{os.getenv('TEST_DATABASE_PASSWORD')}@"
    f"{os.getenv('TEST_DATABASE_HOST', 'localhost')}:"
    f"{os.getenv('TEST_DATABASE_PORT', '5432')}/"
    f"{os.getenv('TEST_DATABASE_NAME', 'bodh_test_db')}"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db() -> Session:
    connection = test_engine.connect()

    transaction = connection.begin()


    session = Session(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )


    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()