"""Add column OriginalFilename for Document

Revision ID: 854e8fa07f59
Revises: 4baadef5513b
Create Date: 2023-09-16 12:35:59.568619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '854e8fa07f59'
down_revision = '4baadef5513b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("original_filename", sa.String(length=1000)))


def downgrade() -> None:
    op.drop_column('document', 'original_filename')
