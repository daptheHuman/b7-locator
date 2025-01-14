"""Add Response field on audit table

Revision ID: 5573f3e75bd4
Revises: 3be545710e0b
Create Date: 2024-02-29 14:28:13.811076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5573f3e75bd4'
down_revision: Union[str, None] = '20d3924b4747'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('audit', sa.Column('response', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('audit', 'response')
    # ### end Alembic commands ###
