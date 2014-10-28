"""Rename question_indicies table to question_category

Revision ID: 2f9a751d0c9
Revises: 265cf2450cf
Create Date: 2014-10-01 11:18:47.053324

"""

# revision identifiers, used by Alembic.
revision = '2f9a751d0c9'
down_revision = '265cf2450cf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('cm_question_indicies','cm_question_category')
    op.alter_column('cm_questions','index_id',new_column_name='question_category_id', existing_type=sa.Integer())

def downgrade():
    op.rename_table('cm_question_category', 'cm_question_indicies')
    op.alter_column('cm_questions','question_category_id',new_column_name='index_id', existing_type=sa.Integer())