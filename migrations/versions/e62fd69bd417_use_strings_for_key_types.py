"""Use strings for key types

Revision ID: e62fd69bd417
Revises: 7e9efd084c5a
Create Date: 2017-10-14 14:56:14.215349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e62fd69bd417'
down_revision = '7e9efd084c5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith('mysql'):
        op.alter_column('keys', 'key_type',
                   existing_type=sa.INTEGER(),
                   type_=sa.String(length=80),
                   existing_nullable=True)
        op.execute("UPDATE `keys` set key_type='static' WHERE key_type='0'")
        op.execute("UPDATE `keys` set key_type='regex' WHERE key_type='1'")
    elif url.startswith('postgres'):
        op.alter_column('keys', 'key_type',
                   existing_type=sa.INTEGER(),
                   type_=sa.String(length=80),
                   existing_nullable=True,
                   postgresql_using="CASE WHEN key_type=0 THEN 'static' WHEN key_type=1 THEN 'regex' ELSE NULL END")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith('mysql'):
        op.execute("UPDATE `keys` set key_type=0 WHERE key_type='static'")
        op.execute("UPDATE `keys` set key_type=1 WHERE key_type='regex'")
        op.alter_column('keys', 'key_type',
                   existing_type=sa.String(length=80),
                   type_=sa.INTEGER(),
                   existing_nullable=True)
    elif url.startswith('postgres'):
        op.alter_column('keys', 'key_type',
                    existing_type=sa.String(length=80),
                    type_=sa.INTEGER(),
                    existing_nullable=True,
                    postgresql_using="CASE WHEN key_type='static' THEN 0 WHEN key_type='regex' THEN 1 ELSE NULL END")
    # ### end Alembic commands ###
