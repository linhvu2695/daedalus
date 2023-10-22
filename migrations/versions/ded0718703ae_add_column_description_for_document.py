"""Add column Description for Document

Revision ID: ded0718703ae
Revises: 64d197acc970
Create Date: 2023-10-21 23:21:43.354261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ded0718703ae'
down_revision = '64d197acc970'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("description", sa.String(length=10000)))


def downgrade() -> None:
    op.drop_column('document', 'description')
