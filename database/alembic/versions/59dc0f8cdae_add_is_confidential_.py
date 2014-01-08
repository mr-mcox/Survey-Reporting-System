"""Add is_confidential field to questions

Revision ID: 59dc0f8cdae
Revises: 38f83803a29
Create Date: 2014-01-08 10:20:28.537054

"""

# revision identifiers, used by Alembic.
revision = '59dc0f8cdae'
down_revision = '38f83803a29'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('questions', sa.Column('is_confidential', sa.Integer))


def downgrade():
    op.drop_column('questions', 'is_confidential')
