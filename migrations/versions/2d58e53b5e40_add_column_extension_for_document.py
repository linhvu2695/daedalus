"""Add column Extension for Document

Revision ID: 2d58e53b5e40
Revises: 854e8fa07f59
Create Date: 2023-09-17 17:45:49.025746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d58e53b5e40'
down_revision = '854e8fa07f59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("extension", sa.String(length=20)))


def downgrade() -> None:
    op.drop_column('document', 'extension')
