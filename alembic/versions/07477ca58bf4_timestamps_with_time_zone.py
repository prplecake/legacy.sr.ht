"""Timestamps with time zone

Revision ID: 07477ca58bf4
Revises: 2c27bce164d
Create Date: 2018-07-08 21:25:39.433804

"""

# revision identifiers, used by Alembic.
revision = '07477ca58bf4'
down_revision = '2c27bce164d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(table_name='upload', column_name='created', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='user', column_name='created', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='user', column_name='approvalDate', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='user', column_name='passwordResetExpiry', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='oauth_clients', column_name='created', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='oauth_tokens', column_name='created', type_=sa.TIMESTAMP(timezone=True))
    op.alter_column(table_name='oauth_tokens', column_name='last_used', type_=sa.TIMESTAMP(timezone=True))



def downgrade():
    op.alter_column(table_name='upload', column_name='created', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='user', column_name='created', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='user', column_name='approvalDate', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='user', column_name='passwordResetExpiry', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='oauth_clients', column_name='created', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='oauth_tokens', column_name='created', type_=sa.TIMESTAMP(timezone=False))
    op.alter_column(table_name='oauth_tokens', column_name='last_used', type_=sa.TIMESTAMP(timezone=False))
