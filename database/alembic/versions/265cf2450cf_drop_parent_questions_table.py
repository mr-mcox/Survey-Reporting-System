"""Drop parent_questions table

Revision ID: 265cf2450cf
Revises: 11141a543f5
Create Date: 2014-10-01 11:07:38.194125

"""

# revision identifiers, used by Alembic.
revision = '265cf2450cf'
down_revision = '11141a543f5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Text


def upgrade():
    op.drop_column('cm_questions','parent_question_id', mssql_drop_foreign_key=True)
    op.drop_table('cm_parent_questions')


def downgrade():
    op.create_table('cm_parent_questions',
        Column('id',Integer(),primary_key=True),
        Column('text',Text()))
    op.add_column('cm_questions', Column('parent_question_id',Integer(), sa.ForeignKey('cm_parent_questions.id')))
