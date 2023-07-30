"""empty message

Revision ID: 5c6587f306b4
Revises: 1b95a49b3f1c
Create Date: 2023-07-30 19:39:52.287473

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5c6587f306b4'
down_revision = '1b95a49b3f1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.alter_column('starttime',
               existing_type=postgresql.TIME(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.alter_column('endtime',
               existing_type=postgresql.TIME(),
               type_=sa.String(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.alter_column('endtime',
               existing_type=sa.String(),
               type_=postgresql.TIME(),
               existing_nullable=False)
        batch_op.alter_column('starttime',
               existing_type=sa.String(),
               type_=postgresql.TIME(),
               existing_nullable=False)

    # ### end Alembic commands ###
