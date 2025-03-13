"""add auth table

Revision ID: 8d2e48cb6dd4
Revises: 76a656ea64d9
Create Date: 2025-03-13 18:11:25.994282

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8d2e48cb6dd4"
down_revision: Union[str, None] = "76a656ea64d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth",
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column(
            "revoked", sa.Boolean(), nullable=False, server_default=sa.text("False")
        ),
        sa.Column("expired_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["usr.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key("fk_url_usr", "url", "usr", ["user_id"], ["id"])
    op.drop_index("ix_user_email", table_name="usr")
    op.create_index(op.f("ix_usr_email"), "usr", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_usr_email"), table_name="usr")
    op.create_index("ix_user_email", "usr", ["email"], unique=True)
    op.drop_constraint("fk_url_usr", "url", type_="foreignkey")
    op.drop_table("auth")
