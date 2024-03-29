"""add configurations to base

Revision ID: e61227558d2b
Revises: d08fc7e71618
Create Date: 2024-02-22 09:16:30.772274

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e61227558d2b'
down_revision: Union[str, None] = 'd08fc7e71618'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configurations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('value', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    comment='Global configurations'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('configurations')
    # ### end Alembic commands ###
