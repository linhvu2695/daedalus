"""Create DocumentKeys table

Revision ID: e860cfb5fc69
Revises: 3b0af3eac947
Create Date: 2023-10-22 22:49:43.021500

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'e860cfb5fc69'
down_revision = '3b0af3eac947'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'dockey',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('create_date', sa.DateTime(timezone=True), default=datetime.now()),
        sa.Column('doc_id', sa.Integer, nullable=False),
        sa.Column('keyword_id', sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('dockey')
