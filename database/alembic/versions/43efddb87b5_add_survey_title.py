"""Add survey title

Revision ID: 43efddb87b5
Revises: 501540883d7
Create Date: 2014-10-02 11:42:56.402644

"""

# revision identifiers, used by Alembic.
revision = '43efddb87b5'
down_revision = '501540883d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('cm_survey', sa.Column('survey_title', sa.String(2000)))


def downgrade():
    op.drop_column('cm_survey', 'survey_title')
