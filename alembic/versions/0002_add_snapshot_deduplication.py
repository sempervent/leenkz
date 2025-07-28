"""Add snapshot deduplication via content hash

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add content_hash column to linksnapshot table
    op.add_column('linksnapshot', sa.Column('content_hash', sa.CHAR(64), nullable=True))
    
    # Create unique composite index for deduplication
    op.create_index(
        'ux_linksnapshot_link_id_hash',
        'linksnapshot',
        ['link_id', 'content_hash'],
        unique=True
    )
    
    # Add index on content_hash for performance
    op.create_index(
        'ix_linksnapshot_content_hash',
        'linksnapshot',
        ['content_hash']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_linksnapshot_content_hash', table_name='linksnapshot')
    op.drop_index('ux_linksnapshot_link_id_hash', table_name='linksnapshot')
    
    # Drop content_hash column
    op.drop_column('linksnapshot', 'content_hash') 