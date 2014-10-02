"""make survey question and cm id primary keys

Revision ID: 511547aaec0
Revises: 43efddb87b5
Create Date: 2014-10-02 11:47:07.472937

"""

# revision identifiers, used by Alembic.
revision = '511547aaec0'
down_revision = '43efddb87b5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('cm_response','respondent_id',new_column_name='person_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('cm_response','question_id',new_column_name='survey_question_id', existing_type=sa.Integer(), nullable=False)
    op.create_primary_key('response_pk', 'cm_response', ['survey_question_id','person_id'])


def downgrade():
    op.alter_column('cm_response','person_id',new_column_name='respondent_id', existing_type=sa.Integer(), nullable=None)
    op.alter_column('cm_response','survey_question_id',new_column_name='question_id', existing_type=sa.Integer(), nullable=None)
    op.drop_constraint('response_pk')
