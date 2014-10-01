"""Rename id columns to contain table name

Revision ID: 2ce3195eb00
Revises: 57da90b5598
Create Date: 2014-10-01 16:42:40.295151

"""

# revision identifiers, used by Alembic.
revision = '2ce3195eb00'
down_revision = '57da90b5598'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('cm_question','id',new_column_name='question_id', existing_type=sa.Integer())
    op.alter_column('cm_question_category','id',new_column_name='question_category_id', existing_type=sa.Integer())
    op.alter_column('cm_survey','id',new_column_name='survey_id', existing_type=sa.Integer())

def downgrade():
    op.alter_column('cm_question','question_id',new_column_name='id', existing_type=sa.Integer())
    op.alter_column('cm_question_category','question_category_id',new_column_name='id', existing_type=sa.Integer())
    op.alter_column('cm_survey','survey_id',new_column_name='id', existing_type=sa.Integer())
