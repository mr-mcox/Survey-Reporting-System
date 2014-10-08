"""Add survey_specific_question to survey_specific_question

Revision ID: 3018942e76f
Revises: 1a4cbc92a6f
Create Date: 2014-10-07 18:58:40.740160

"""

# revision identifiers, used by Alembic.
revision = '3018942e76f'
down_revision = '1a4cbc92a6f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('survey_specific_questions', sa.Column('survey_specific_question', sa.String(2000)))
    
def downgrade():
    op.drop_column('survey_specific_questions', 'survey_specific_question')
