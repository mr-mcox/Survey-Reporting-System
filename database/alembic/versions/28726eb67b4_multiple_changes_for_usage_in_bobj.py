"""Multiple changes for usage in BOBJ

Revision ID: 28726eb67b4
Revises: 3a5a97f7fe3
Create Date: 2014-09-17 09:53:18.274147

"""

# revision identifiers, used by Alembic.
revision = '28726eb67b4'
down_revision = '3a5a97f7fe3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Text


def upgrade():
	op.rename_table('results','responses')
	op.add_column('responses',Column('net_formatted_value',Integer()))
	op.create_table('question_indicies',
		Column('id',Integer(),primary_key=True),
		Column('name',String(20)))
	op.add_column('questions',Column('question_text',Text()))
	op.create_table('parent_questions',
		Column('id',Integer(),primary_key=True),
		Column('text',Text()))
	op.add_column('questions', Column('index_id',Integer(), sa.ForeignKey('question_indicies.id')))
	op.add_column('questions', Column('parent_question_id',Integer(), sa.ForeignKey('parent_questions.id')))
	op.drop_column('responses','survey_id')



def downgrade():
	op.add_column('responses',Column('survey_id', Integer(), sa.ForeignKey('surveys.id')))
	op.drop_column('questions','parent_question_id')
	op.drop_column('questions','index_id')
	op.drop_table('parent_questions')
	op.drop_column('questions','question_text')
	op.drop_table('question_indicies')
	op.drop_column('responses','net_formatted_value')
	op.rename_table('responses','results')