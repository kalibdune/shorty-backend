"""change nullable of fields

Revision ID: 317b59d4e87c
Revises: 8d2e48cb6dd4
Create Date: 2025-03-20 11:38:02.306433

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "317b59d4e87c"
down_revision: Union[str, None] = "8d2e48cb6dd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "url", "expired_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column("url", "user_id", existing_type=sa.UUID(), nullable=True)


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM url WHERE user_id IS NULL OR expired_at IS NULL;"))
    op.alter_column("url", "user_id", existing_type=sa.UUID(), nullable=False)
    op.alter_column(
        "url", "expired_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
