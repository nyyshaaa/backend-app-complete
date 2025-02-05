"""frosties qty column add

Revision ID: 9770d91f040d
Revises: bd8b827e2fd7
Create Date: 2025-02-03 17:38:44.018936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9770d91f040d'
down_revision: Union[str, None] = 'bd8b827e2fd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('frosties', sa.Column('qty', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('frosties', 'qty')
    # ### end Alembic commands ###
