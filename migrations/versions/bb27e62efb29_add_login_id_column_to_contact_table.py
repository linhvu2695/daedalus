"""Add Login_Id column to Contact table

Revision ID: bb27e62efb29
Revises: 715bba9406c4
Create Date: 2023-11-15 21:11:02.651364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb27e62efb29'
down_revision = '715bba9406c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contact", sa.Column("login_id", sa.String(200)))


def downgrade() -> None:
    op.drop_column('contact', 'login_id')
