"""Alter data column to MEDIUMBLOB

Revision ID: 919b6158493a
Revises: e5185dac6905
Create Date: 2024-10-14 21:08:19.482019

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '919b6158493a'
down_revision = 'e5185dac6905'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=sa.BLOB(),
               type_=mysql.LONGBLOB(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.alter_column('data',
               existing_type=mysql.LONGBLOB(),
               type_=sa.BLOB(),
               existing_nullable=False)

    # ### end Alembic commands ###
