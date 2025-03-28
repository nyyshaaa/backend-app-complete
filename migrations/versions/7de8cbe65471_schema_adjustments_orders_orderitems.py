"""schema adjustments orders orderitems

Revision ID: 7de8cbe65471
Revises: 9770d91f040d
Create Date: 2025-02-03 23:30:43.194966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7de8cbe65471'
down_revision: Union[str, None] = '9770d91f040d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_user_title', 'frosties', ['user_id', 'title'])
    op.add_column('orderitems', sa.Column('seller_id', sa.BigInteger(), nullable=True))
    op.create_unique_constraint('unique_order_item', 'orderitems', ['order_id', 'frost_id'])
    op.create_foreign_key(None, 'orderitems', 'users', ['seller_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('orders_seller_id_fkey', 'orders', type_='foreignkey')
    op.drop_column('orders', 'seller_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('seller_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('orders_seller_id_fkey', 'orders', 'users', ['seller_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'orderitems', type_='foreignkey')
    op.drop_constraint('unique_order_item', 'orderitems', type_='unique')
    op.drop_column('orderitems', 'seller_id')
    op.drop_constraint('unique_user_title', 'frosties', type_='unique')
    # ### end Alembic commands ###
