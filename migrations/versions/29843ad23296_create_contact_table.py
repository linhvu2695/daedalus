"""Create Contact table

Revision ID: 29843ad23296
Revises: 
Create Date: 2023-09-14 21:52:58.026063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29843ad23296'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'contact',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(150), nullable=False, unique=True),
        sa.Column('password', sa.String(200)),
        sa.Column('first_name', sa.String(200)),
        sa.Column('last_name', sa.String(200)),
    )


def downgrade() -> None:
    op.drop_table('contact')
