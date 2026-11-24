
"""Remove duplicate item with ID 0.

Revision ID: 0003
Revises: 0002
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    duplicate = connection.execute(
        sa.text("SELECT * FROM item WHERE id = 0")
    ).mappings().fetchone()

    if duplicate is None:
        return

    original = connection.execute(
        sa.text("SELECT * FROM item WHERE id = 1")
    ).mappings().fetchone()

    if original is None:
        raise RuntimeError(
            "Cannot remove item ID 0: item ID 1 does not exist."
        )

    excluded_fields = {"id", "created_at", "updated_at"}

    if any(
        duplicate[field] != original[field]
        for field in duplicate.keys()
        if field not in excluded_fields
    ):
        raise RuntimeError(
            "Cannot remove item ID 0: it does not match item ID 1."
        )

    referencing_tables = [
        "inventory",
        "order_item",
        "shipment_item",
        "transfer_item",
    ]

    for table in referencing_tables:
        references = connection.execute(
            sa.text(f"SELECT count(*) FROM {table} WHERE item_id = 0")
        ).scalar_one()

        if references:
            raise RuntimeError(
                f"Cannot remove item ID 0: {table} still references it."
            )

    connection.execute(
        sa.text("DELETE FROM item WHERE id = 0")
    )


def downgrade() -> None:
    pass
