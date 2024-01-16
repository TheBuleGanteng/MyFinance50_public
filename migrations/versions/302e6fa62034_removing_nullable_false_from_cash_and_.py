"""Removing nullable=False from 'cash' and 'created' since they have defaults

Revision ID: 302e6fa62034
Revises: 2516f40ba48b
Create Date: 2024-01-16 20:28:54.080812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '302e6fa62034'
down_revision = '2516f40ba48b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('created',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.alter_column('cash',
               existing_type=sa.FLOAT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.alter_column('created',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###
