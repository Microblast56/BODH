"""allow category name reuse after deactivation"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aba5e35ecec6"
down_revision: Union[str, Sequence[str], None] = "bca2bb0a0d41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow category names to be reused after deactivation."""
    op.drop_constraint(
        "uq_categories_retailer_name",
        "categories",
        type_="unique",
    )

    op.create_index(
        "uq_categories_retailer_name",
        "categories",
        ["retailer_id", "name"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )


def downgrade() -> None:
    """Restore unconditional category name uniqueness."""
    connection = op.get_bind()

    duplicates = connection.execute(
        sa.text(
            """
            SELECT retailer_id, name
            FROM categories
            GROUP BY retailer_id, name
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()

    if duplicates:
        raise RuntimeError(
            "Cannot downgrade category name reuse migration: "
            "duplicate category names exist for the same retailer. "
            "Resolve those duplicates before retrying."
        )

    op.drop_index(
        "uq_categories_retailer_name",
        table_name="categories",
    )

    op.create_unique_constraint(
        "uq_categories_retailer_name",
        "categories",
        ["retailer_id", "name"],
    )
