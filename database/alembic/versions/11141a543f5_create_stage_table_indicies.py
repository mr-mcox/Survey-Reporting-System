"""Create stage table indicies

Revision ID: 11141a543f5
Revises: 6de30e4654
Create Date: 2014-09-30 15:09:29.049806

"""

# revision identifiers, used by Alembic.
revision = '11141a543f5'
down_revision = '6de30e4654'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('ix_survey_specific_questions_survey', 'survey_specific_questions', ['survey'])
    op.create_index('ix_numerical_responses_survey', 'numerical_responses', ['survey'])



def downgrade():
    op.drop_index('ix_survey_specific_questions_survey')
    op.drop_index('ix_numerical_responses_survey')
