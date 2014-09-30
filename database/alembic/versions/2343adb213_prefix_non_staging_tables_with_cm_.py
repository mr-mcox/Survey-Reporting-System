"""Prefix non-staging tables with cm_

Revision ID: 2343adb213
Revises: 28726eb67b4
Create Date: 2014-09-30 11:22:36.977873

"""

# revision identifiers, used by Alembic.
revision = '2343adb213'
down_revision = '28726eb67b4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('parent_questions','cm_parent_questions')
    op.rename_table('question_indicies','cm_question_indicies')
    op.rename_table('questions','cm_questions')
    op.rename_table('responses','cm_responses')
    op.rename_table('surveys','cm_surveys')


def downgrade():
    op.rename_table('cm_parent_questions','parent_questions')
    op.rename_table('cm_question_indicies','question_indicies')
    op.rename_table('cm_questions','questions')
    op.rename_table('cm_responses','responses')
    op.rename_table('cm_surveys','surveys')
