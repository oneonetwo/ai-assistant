"""Add parent_message_id to messages

Revision ID: add_parent_message_field
Revises: initial_migration
Create Date: 2024-03-22
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_parent_message_field'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 添加 parent_message_id 列
    op.add_column('messages',
        sa.Column('parent_message_id', sa.Integer(), nullable=True)
    )
    
    # 添加外键约束
    op.create_foreign_key(
        'fk_message_parent',
        'messages', 'messages',
        ['parent_message_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_message_parent', 'messages', type_='foreignkey')
    # 删除列
    op.drop_column('messages', 'parent_message_id') 