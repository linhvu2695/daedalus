"""Add Binned column for Dockey

Revision ID: 715bba9406c4
Revises: d386af6a6cdb
Create Date: 2023-11-12 21:21:04.391497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '715bba9406c4'
down_revision = 'd386af6a6cdb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dockey", sa.Column("binned", sa.Boolean(), nullable=False, server_default=sa.literal(False)))


def downgrade() -> None:
    op.drop_column('dockey', 'binned')
