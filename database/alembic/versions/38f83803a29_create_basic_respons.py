"""Create basic responses, question and survey tables

Revision ID: 38f83803a29
Revises: None
Create Date: 2013-11-12 17:11:50.767202

"""

# revision identifiers, used by Alembic.
revision = '38f83803a29'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
	op.create_table('results',
		sa.Column('respondent_id', sa.Integer),
		sa.Column('survey_id', sa.Integer, sa.ForeignKey('surveys.id')),
		sa.Column('question_id', sa.Integer, sa.ForeignKey('questions.id')),
		sa.Column('response', sa.Integer))
	op.create_table('surveys',
		sa.Column('id', sa.Integer, primary_key=True),
		sa.Column('survey_code', sa.String(20)))
	op.create_table('questions',
		sa.Column('id', sa.Integer, primary_key=True),
		sa.Column('survey_id', sa.Integer),
		sa.Column('question_code', sa.String(20)))

	


def downgrade():
    op.drop_table('results')
    op.drop_table('surveys')
    op.drop_table('questions')

