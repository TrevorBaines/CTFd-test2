"""Rename Keys.key_type to Keys.type

Revision ID: 2539d8b5082e
Revises: e62fd69bd417
Create Date: 2017-11-23 17:30:43.759245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2539d8b5082e'
down_revision = 'e62fd69bd417'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('keys', new_column_name='type', column_name="key_type", type_=sa.String(80))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('keys', new_column_name='key_type', column_name="key_type", type_=sa.String(80))
    # ### end Alembic commands ###
