"""Initial

Revision ID: 869e60dd2057
Revises: 
Create Date: 2023-04-23 21:39:38.312589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '869e60dd2057'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('grouprows', 'id',
               existing_type=sa.INTEGER(),
               server_default=sa.Identity(always=False, start=1, increment=1),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('grouprows', 'idgroup',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'grouprows', 'groups', ['idgroup'], ['id'])
    op.alter_column('groups', 'id',
               existing_type=sa.INTEGER(),
               server_default=sa.Identity(always=False, start=1, increment=1),
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('logevents', 'datetimestamp',
               existing_type=sa.DATETIME(),
               nullable=True)
    op.alter_column('reports', 'id',
               existing_type=sa.INTEGER(),
               server_default=sa.Identity(always=False, start=1, increment=1),
               existing_nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('reports', 'id',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('logevents', 'datetimestamp',
               existing_type=sa.DATETIME(),
               nullable=False)
    op.alter_column('groups', 'id',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
    op.drop_constraint(None, 'grouprows', type_='foreignkey')
    op.alter_column('grouprows', 'idgroup',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('grouprows', 'id',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###