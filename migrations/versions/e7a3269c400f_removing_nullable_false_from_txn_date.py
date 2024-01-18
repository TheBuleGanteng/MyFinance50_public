"""Removing nullable=False from txn_date

Revision ID: e7a3269c400f
Revises: 302e6fa62034
Create Date: 2024-01-16 22:01:21.020473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7a3269c400f'
down_revision = '302e6fa62034'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('txn_date',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('txn_date',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###