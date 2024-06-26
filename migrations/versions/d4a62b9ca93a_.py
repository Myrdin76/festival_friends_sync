"""empty message

Revision ID: d4a62b9ca93a
Revises: e6599a100993
Create Date: 2023-07-30 17:19:55.377788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4a62b9ca93a'
down_revision = 'e6599a100993'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('day', sa.String(length=30), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.drop_column('day')

    # ### end Alembic commands ###
