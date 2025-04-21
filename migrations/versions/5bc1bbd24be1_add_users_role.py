"""add users role

Revision ID: 5bc1bbd24be1
Revises: c831acd85f09
Create Date: 2025-04-21 15:34:46.968691

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum


# revision identifiers, used by Alembic.
revision: str = "5bc1bbd24be1"
down_revision: Union[str, None] = "c831acd85f09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create UserRole enum type
    userrole = Enum('ADMIN', 'USER', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)

    # Add role column with default value
    op.add_column(
        "users",
        sa.Column("role", userrole, nullable=False, server_default="USER"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the role column
    op.drop_column("users", "role")
    
    # Drop the enum type
    userrole = Enum('ADMIN', 'USER', name='userrole')
    userrole.drop(op.get_bind(), checkfirst=True)
