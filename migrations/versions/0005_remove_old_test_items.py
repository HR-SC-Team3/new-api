"""Remove leftover test items.

Revision ID: 0005
Revises: 0004
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    test_items = {
        555555: ("Test Item", "ITM-555555"),
        555556: ("Location Test Item", "ITM-555556"),
        555557: ("Retrievable Item", "ITM-555557"),
        888888: ("Temporary Test Item", "ITM-888888"),
    }

    referencing_tables = [
        "inventory",
        "order_item",
        "shipment_item",
        "transfer_item",
    ]

    for item_id, (description, code) in test_items.items():
        item = connection.execute(
            sa.text(
                """
                SELECT description, code
                FROM item
                WHERE id = :item_id
                """
            ),
            {"item_id": item_id},
        ).fetchone()

        if item is None:
            continue

        if item.description != description or item.code != code:
            raise RuntimeError(
                f"Cannot remove item ID {item_id}: "
                "it does not match the expected test item."
            )

        for table in referencing_tables:
            references = connection.execute(
                sa.text(
                    f"SELECT count(*) FROM {table} WHERE item_id = :item_id"
                ),
                {"item_id": item_id},
            ).scalar_one()

            if references:
                raise RuntimeError(
                    f"Cannot remove item ID {item_id}: "
                    f"{table} still references it."
                )

        connection.execute(
            sa.text("DELETE FROM item WHERE id = :item_id"),
            {"item_id": item_id},
        )


def downgrade() -> None:
    pass
