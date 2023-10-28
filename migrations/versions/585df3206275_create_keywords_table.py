"""Create Keywords table

Revision ID: 585df3206275
Revises: ded0718703ae
Create Date: 2023-10-22 22:32:59.177696

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '585df3206275'
down_revision = 'ded0718703ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'keyword',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('create_date', sa.DateTime(timezone=True), default=datetime.now()),
        sa.Column('keytype', sa.Integer),
    )


def downgrade() -> None:
    op.drop_table('keyword')
