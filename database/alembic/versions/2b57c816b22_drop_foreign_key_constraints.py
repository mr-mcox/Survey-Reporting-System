"""Drop foreign key constraints

Revision ID: 2b57c816b22
Revises: 511547aaec0
Create Date: 2014-10-02 12:00:01.890156

"""

# revision identifiers, used by Alembic.
revision = '2b57c816b22'
down_revision = '511547aaec0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('cm_survey_question','question_category_id',mssql_drop_foreign_key=True)
    op.add_column('cm_survey_question',sa.Column('question_category_id',sa.Integer()))
    op.drop_constraint('response_pk','cm_response')
    op.drop_column('cm_response','survey_question_id',mssql_drop_foreign_key=True)
    op.add_column('cm_response',sa.Column('survey_question_id',sa.Integer(), nullable=False))
    op.create_primary_key('response_pk', 'cm_response', ['survey_question_id','person_id'])


def downgrade():
    op.drop_column('cm_survey_question','question_category_id',mssql_drop_foreign_key=True)
    op.add_column('cm_survey_question',sa.Column('question_category_id',sa.Integer(), sa.ForeignKey('question_category.question_category_id')))
    op.drop_constraint('response_pk','cm_response')
    op.drop_column('cm_response','survey_question_id',mssql_drop_foreign_key=True)
    op.add_column('cm_response',sa.Column('survey_question_id',sa.Integer(), sa.ForeignKey('survey_question.survey_question_id'), nullable=False))
    op.create_primary_key('response_pk', 'cm_response', ['survey_question_id','person_id'])