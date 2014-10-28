"""Several column name changes

Revision ID: 4119a32d65b
Revises: 2ce3195eb00
Create Date: 2014-10-01 16:47:34.069348

"""

# revision identifiers, used by Alembic.
revision = '4119a32d65b'
down_revision = '2ce3195eb00'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('cm_response','net_formatted_value',new_column_name='converted_net_value', existing_type=sa.Integer())
    op.alter_column('cm_question','question_text',new_column_name='question_title', existing_type=sa.Text())
    op.alter_column('cm_question_category','name',new_column_name='question_category', existing_type=sa.String(20))


def downgrade():
    op.alter_column('cm_response','converted_net_value',new_column_name='net_formatted_value', existing_type=sa.Integer())
    op.alter_column('cm_question','question_title',new_column_name='question_text', existing_type=sa.Text())
    op.alter_column('cm_question_category','question_category',new_column_name='name', existing_type=sa.String(20))
