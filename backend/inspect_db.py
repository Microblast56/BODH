from sqlalchemy import inspect
from app.db.database import engine

inspector = inspect(engine)

for table in inspector.get_table_names():
    print(f"\n===== {table} =====")

    print("Columns:")
    for column in inspector.get_columns(table):
        print(f"  - {column['name']} ({column['type']})")

    print("Foreign Keys:")
    for fk in inspector.get_foreign_keys(table):
        print(
            f"  - {fk['constrained_columns']} "
            f"-> {fk['referred_table']}.{fk['referred_columns']}"
        )
