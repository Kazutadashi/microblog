"""Add new fields in user model

Revision ID: dc0b5dc6fc39
Revises: a54434813f53
Create Date: 2025-01-23 17:34:15.079395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc0b5dc6fc39'
down_revision = 'a54434813f53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_me', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('about_me')

    # ### end Alembic commands ###
