"""Add column Lineage_path for Document

Revision ID: 64d197acc970
Revises: 2d58e53b5e40
Create Date: 2023-09-21 22:15:13.143845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64d197acc970'
down_revision = '2d58e53b5e40'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("lineage_path", sa.String(length=10000)))


def downgrade() -> None:
    op.drop_column('document', 'lineage_path')
