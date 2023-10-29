"""Add Binned column for Keywords and Keytypes

Revision ID: d386af6a6cdb
Revises: 36f86e4becbd
Create Date: 2023-10-29 15:03:18.105116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd386af6a6cdb'
down_revision = '36f86e4becbd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("keyword", sa.Column("binned", sa.Boolean(), nullable=False, server_default=sa.literal(False)))
    op.add_column("keytype", sa.Column("binned", sa.Boolean(), nullable=False, server_default=sa.literal(False)))


def downgrade() -> None:
    op.drop_column('keyword', 'binned')
    op.drop_column('keytype', 'binned')
