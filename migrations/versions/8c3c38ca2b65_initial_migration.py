"""Initial migration

Revision ID: 8c3c38ca2b65
Revises: 
Create Date: 2024-08-05 13:01:21.479938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c3c38ca2b65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contact_message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_name', sa.String(length=100), nullable=False))
        batch_op.drop_column('name')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('name')

    with op.batch_alter_table('contact_message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=100), nullable=False))
        batch_op.drop_column('contact_name')

    # ### end Alembic commands ###