"""empty message

Revision ID: 117eed1bf216
Revises: 4c3a0537b7aa
Create Date: 2020-07-11 10:14:56.018679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '117eed1bf216'
down_revision = '4c3a0537b7aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
