"""Add Description column for Keywords and Keytypes

Revision ID: 36f86e4becbd
Revises: e860cfb5fc69
Create Date: 2023-10-29 13:49:57.731722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36f86e4becbd'
down_revision = 'e860cfb5fc69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("keyword", sa.Column("description", sa.String(length=10000)))
    op.add_column("keytype", sa.Column("description", sa.String(length=10000)))


def downgrade() -> None:
    op.drop_column('keyword', 'description')
    op.drop_column('keytype', 'description')
