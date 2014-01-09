"""Add question_type field

Revision ID: 3a5a97f7fe3
Revises: 59dc0f8cdae
Create Date: 2014-01-09 16:42:46.823019

"""

# revision identifiers, used by Alembic.
revision = '3a5a97f7fe3'
down_revision = '59dc0f8cdae'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('questions', sa.Column('question_type', sa.String(20)))


def downgrade():
    op.drop_column('questions', 'question_type')
