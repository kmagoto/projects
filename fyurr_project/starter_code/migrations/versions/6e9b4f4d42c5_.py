"""empty message

Revision ID: 6e9b4f4d42c5
Revises: bef7a4e9b502
Create Date: 2022-08-21 12:40:25.663265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e9b4f4d42c5'
down_revision = 'bef7a4e9b502'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    op.add_column('Artist', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=500), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.String(length=10), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    op.add_column('Venue', sa.Column('num_past_shows', sa.Integer(), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.String(length=20), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'num_past_shows')
    op.drop_column('Venue', 'num_upcoming_shows')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'past_shows_count')
    op.drop_column('Artist', 'upcoming_shows_count')
    # ### end Alembic commands ###