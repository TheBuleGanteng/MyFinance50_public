"""Adding cash_initial

Revision ID: ed5c83a9a1ca
Revises: 2e379e41bb75
Create Date: 2024-02-02 19:51:28.635693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed5c83a9a1ca'
down_revision = '2e379e41bb75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cash_initial', sa.Float(precision=2), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('cash_initial')

    # ### end Alembic commands ###
