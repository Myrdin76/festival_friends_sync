"""empty message

Revision ID: 885336b9e4eb
Revises: 58ff72df9d82
Create Date: 2023-08-02 18:03:36.446842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '885336b9e4eb'
down_revision = '58ff72df9d82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_invite',
    sa.Column('invite_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('to_group_id', sa.Integer(), nullable=False),
    sa.Column('from_user_id', sa.Integer(), nullable=False),
    sa.Column('to_user_id', sa.Integer(), nullable=False),
    sa.Column('accepted', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('invite_id')
    )
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('private', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.drop_column('private')

    op.drop_table('group_invite')
    # ### end Alembic commands ###
