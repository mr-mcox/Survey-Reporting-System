"""Separate survey question and question tables

Revision ID: 501540883d7
Revises: 4119a32d65b
Create Date: 2014-10-02 11:08:37.532938

"""

# revision identifiers, used by Alembic.
revision = '501540883d7'
down_revision = '4119a32d65b'

from alembic import op
import sqlalchemy as sa

#This does not include data migration and question codes will be lost. I'm assuming that a re-import is required anyways.

def upgrade():
    op.drop_index('ix_cm_questions_question_code', 'cm_question')
    op.drop_column('cm_question','question_code')
    op.rename_table('cm_question','cm_survey_question')
    op.alter_column('cm_survey_question','question_id',new_column_name='survey_question_id', existing_type=sa.Integer())
    op.alter_column('cm_survey_question','question_title',new_column_name='question_title_override', existing_type=sa.Text())
    op.create_table('cm_question',
        sa.Column('question_id', sa.Integer, primary_key=True),
        sa.Column('question_title', sa.Unicode(2000)),
        sa.Column('question_code', sa.String(20)))
    op.add_column('cm_survey_question', sa.Column('question_id',sa.Integer()))

def downgrade():
    op.drop_column('cm_survey_question','question_id', mssql_drop_foreign_key=True)
    op.drop_table('cm_question')
    op.alter_column('cm_survey_question','survey_question_id',new_column_name='question_id', existing_type=sa.Integer())
    op.alter_column('cm_survey_question','question_title_override',new_column_name='question_title', existing_type=sa.Text())
    op.rename_table('cm_question','cm_survey_question')
    op.add_column('cm_question',sa.Column('question_code', sa.String(20)))
    op.create_index('ix_cm_questions_question_code', 'cm_question', ['question_code'])
