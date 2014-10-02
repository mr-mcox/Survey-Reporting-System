"""Change question override type from text to varchar

Revision ID: 1a4cbc92a6f
Revises: 2b57c816b22
Create Date: 2014-10-02 12:13:11.562095

"""

# revision identifiers, used by Alembic.
revision = '1a4cbc92a6f'
down_revision = '2b57c816b22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('cm_survey_question','question_title_override',type_=sa.String(2000))


def downgrade():
    op.alter_column('cm_survey_question','question_title_override',type_=sa.Text())
