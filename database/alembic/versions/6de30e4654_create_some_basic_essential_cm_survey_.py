"""Create some basic cm survey indexes

Revision ID: 6de30e4654
Revises: 1db95820760
Create Date: 2014-09-30 14:59:31.046062

"""

# revision identifiers, used by Alembic.
revision = '6de30e4654'
down_revision = '1db95820760'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('ix_cm_questions_question_code', 'cm_questions', ['question_code'])

def downgrade():
    op.drop_index('ix_cm_questions_question_code')
