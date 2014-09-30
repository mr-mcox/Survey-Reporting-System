"""Stage Survey Tables included in versioning

Revision ID: 1db95820760
Revises: 2343adb213
Create Date: 2014-09-30 14:47:23.046611

"""

# revision identifiers, used by Alembic.
revision = '1db95820760'
down_revision = '2343adb213'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('numerical_responses',
        sa.Column('cm_pid', sa.Integer),
        sa.Column('survey', sa.String(20)),
        sa.Column('survey_specific_qid', sa.String(40)),
        sa.Column('response', sa.Integer),
        )
    op.create_table('survey_specific_questions',
        sa.Column('survey_specific_qid', sa.String(20)),
        sa.Column('master_qid', sa.String(20)),
        sa.Column('survey', sa.String(20)),
        sa.Column('confidential', sa.Integer),
        sa.Column('question_type', sa.String(20)),
        )


def downgrade():
    op.drop_table('numerical_responses')
    op.drop_table('survey_specific_questions')