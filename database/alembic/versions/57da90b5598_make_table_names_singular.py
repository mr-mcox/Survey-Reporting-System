"""Make table names singular

Revision ID: 57da90b5598
Revises: 2f9a751d0c9
Create Date: 2014-10-01 16:37:25.206223

"""

# revision identifiers, used by Alembic.
revision = '57da90b5598'
down_revision = '2f9a751d0c9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('cm_questions','cm_question')
    op.rename_table('cm_responses','cm_response')
    op.rename_table('cm_surveys','cm_survey')


def downgrade():
    op.rename_table('cm_question','cm_questions')
    op.rename_table('cm_response','cm_responses')
    op.rename_table('cm_survey','cm_surveys')
