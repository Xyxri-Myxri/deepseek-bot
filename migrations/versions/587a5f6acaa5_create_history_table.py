"""Create history table

Revision ID: 587a5f6acaa5
Revises:
Create Date: 2025-03-09 16:55:18.392766

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "587a5f6acaa5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger, nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("response", sa.Text, nullable=False),
        sa.Column(
            "timestamp", sa.TIMESTAMP, server_default=sa.func.now(), nullable=False
        ),
    )


def downgrade():
    op.drop_table("history")
