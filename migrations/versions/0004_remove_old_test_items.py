"""Remove old test items with invalid values.

This migration deletes rows and cannot be reversed: the deleted test rows are not
stored anywhere, so downgrade() is a no-op. It only removes rows that still match
the exact leftover test data, and fails if anything else references them.

Revision ID: 0004
Revises: 0003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    test_items = {
        999991: ("Jumbo Summer Sprinkles IJsjes 6 Stuks", "ITM-000001", 0, 1),
        1896087415: ("Range Validation Test", "ITM-1896087415", 0, None),
        1233446673: ("Range Validation Test", "ITM-1233446673", None, -1),
    }

    referencing_tables = [
        "inventory",
        "order_item",
        "shipment_item",
        "transfer_item",
    ]

    for item_id, (description, code, case_size, order_multiple) in test_items.items():
        item = connection.execute(
            sa.text(
                """
                SELECT description, code, case_size, order_multiple
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

        if item.case_size != case_size or item.order_multiple != order_multiple:
            raise RuntimeError(
                f"Cannot remove item ID {item_id}: "
                "it does not have the expected invalid values."
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

        result = connection.execute(
            sa.text(
                """
                DELETE FROM item
                WHERE id = :item_id
                AND description = :description
                AND code = :code
                AND case_size IS NOT DISTINCT FROM :case_size
                AND order_multiple IS NOT DISTINCT FROM :order_multiple
                """
            ),
            {
                "item_id": item_id,
                "description": description,
                "code": code,
                "case_size": case_size,
                "order_multiple": order_multiple,
            },
        )

        if result.rowcount != 1:
            raise RuntimeError(
                f"Cannot remove item ID {item_id}: "
                "its values changed before deletion."
            )


def downgrade() -> None:
    pass
