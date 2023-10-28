"""Create Keytypes table

Revision ID: 3b0af3eac947
Revises: 585df3206275
Create Date: 2023-10-22 22:46:59.036890

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '3b0af3eac947'
down_revision = '585df3206275'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'keytype',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('create_date', sa.DateTime(timezone=True), default=datetime.now()),
    )


def downgrade() -> None:
    op.drop_table('keytype')
