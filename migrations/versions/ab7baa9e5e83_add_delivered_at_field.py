"""add delivered at field

Revision ID: ab7baa9e5e83
Revises: cfbb0a56d960
Create Date: 2025-03-20 19:57:19.478270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab7baa9e5e83'
down_revision: Union[str, None] = 'cfbb0a56d960'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('delivered_at', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'delivered_at')
    # ### end Alembic commands ###
