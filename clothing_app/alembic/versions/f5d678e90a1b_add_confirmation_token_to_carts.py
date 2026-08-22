"""Add confirmation_token to carts table."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f5d678e90a1b"
down_revision: Union[str, Sequence[str], None] = "e4c2a1b7d9f4"
branch_labels = None
depends_on = None
SCHEMA = "clothing_store"


def upgrade() -> None:
    op.add_column("carts", sa.Column("confirmation_token", sa.Uuid(), nullable=True), schema=SCHEMA)


def downgrade() -> None:
    op.drop_column("carts", "confirmation_token", schema=SCHEMA)
