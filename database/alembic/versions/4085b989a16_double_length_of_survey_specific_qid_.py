"""Double length of survey_specific_qid field

Revision ID: 4085b989a16
Revises: 3018942e76f
Create Date: 2014-10-08 01:35:45.030934

"""

# revision identifiers, used by Alembic.
revision = '4085b989a16'
down_revision = '3018942e76f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('survey_specific_questions','survey_specific_qid',type_=sa.String(40))


def downgrade():
    op.alter_column('survey_specific_questions','survey_specific_qid',type_=sa.String(20))
