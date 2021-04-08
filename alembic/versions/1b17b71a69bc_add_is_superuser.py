"""add is_superuser

Revision ID: 1b17b71a69bc
Revises: de61e3c0cead
Create Date: 2021-04-08 15:42:46.604731

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "1b17b71a69bc"
down_revision = "de61e3c0cead"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("is_superuser", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "is_superuser")
    # ### end Alembic commands ###
