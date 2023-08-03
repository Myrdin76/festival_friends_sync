"""empty message

Revision ID: 97ed909a2523
Revises: 885336b9e4eb
Create Date: 2023-08-03 11:35:17.005827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '97ed909a2523'
down_revision = '885336b9e4eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_invite', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['to_group_id', 'to_user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group_invite', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###