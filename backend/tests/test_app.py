from sqlalchemy import inspect

from app.main import app


def test_app_imports():
    assert app is not None


def test_database_tables_exist(db):
    inspector = inspect(db.bind)

    tables = inspector.get_table_names()

    assert "retailers" in tables
    assert "categories" in tables
    assert "products" in tables