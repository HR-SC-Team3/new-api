"""unique index on user.api_key

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Stop with a clear message if duplicates exist. No policy says which user to
    # keep, so this migration never deletes or merges users. Fix the data by hand,
    # then run the migration again. The key values stay out of the message (secrets).
    duplicates = op.get_bind().execute(sa.text(
        'SELECT count(*) FROM (SELECT 1 FROM "user" '
        'GROUP BY api_key HAVING count(*) > 1) AS d'
    )).scalar_one()
    if duplicates:
        raise RuntimeError(
            f'Cannot add a unique index: {duplicates} api_key value(s) in "user" '
            'are used by more than one user. Resolve them by hand, then retry.'
        )
    op.create_index('ix_user_api_key', 'user', ['api_key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_api_key', table_name='user')
