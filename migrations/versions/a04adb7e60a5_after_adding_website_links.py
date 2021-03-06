"""After adding website links

Revision ID: a04adb7e60a5
Revises: e2b55eb5edcd
Create Date: 2020-12-14 11:20:18.235540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a04adb7e60a5'
down_revision = 'e2b55eb5edcd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
