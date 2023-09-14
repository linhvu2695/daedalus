"""Create Document table

Revision ID: 4baadef5513b
Revises: 29843ad23296
Create Date: 2023-09-14 22:01:15.305509

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '4baadef5513b'
down_revision = '29843ad23296'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'document',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(1000), nullable=False),
        sa.Column('storage_path', sa.String(10000)),
        sa.Column('create_date', sa.DateTime(timezone=True), default=datetime.now()),
        sa.Column('doctype', sa.String(150)),
        sa.Column('subtype', sa.String(150)),
        sa.Column('mother', sa.Integer),
        sa.Column('binned', sa.Boolean),
    )


def downgrade() -> None:
    op.drop_table('document')
