"""unique index on user.api_key

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_user_api_key', 'user', ['api_key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_api_key', table_name='user')
