"""v1.2.0_add_handbook_tables

Revision ID: v1_2_0_handbook
Revises: fcf7d637ac1d
Create Date: 2024-03-28 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'v1_2_0_handbook'
down_revision: Union[str, None] = 'fcf7d637ac1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 检查表是否已存在，如果存在则跳过
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 创建分类表（如果不存在）
    if 'categories' not in existing_tables:
        op.create_table('categories',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # 创建手册表（如果不存在）
    if 'handbooks' not in existing_tables:
        op.create_table('handbooks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # 创建标签表（如果不存在）
    if 'tags' not in existing_tables:
        op.create_table('tags',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    # 创建笔记表（如果不存在）
    if 'notes' not in existing_tables:
        op.create_table('notes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('message_ids', sa.JSON(), nullable=True),
            sa.Column('priority', sa.String(length=10), nullable=True),
            sa.Column('times', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('is_shared', sa.Boolean(), nullable=True),
            sa.Column('handbook_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['handbook_id'], ['handbooks.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # 创建笔记标签关联表（如果不存在）
    if 'note_tags' not in existing_tables:
        op.create_table('note_tags',
            sa.Column('note_id', sa.Integer(), nullable=False),
            sa.Column('tag_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
            sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
            sa.PrimaryKeyConstraint('note_id', 'tag_id')
        )

    # 创建笔记附件表（如果不存在）
    if 'note_attachments' not in existing_tables:
        op.create_table('note_attachments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('note_id', sa.Integer(), nullable=True),
            sa.Column('file_id', sa.String(length=36), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['file_id'], ['files.file_id'], ),
            sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade() -> None:
    # 仅删除知识手册相关的表，不影响AI助手的表
    op.drop_table('note_attachments')
    op.drop_table('note_tags')
    op.drop_table('notes')
    op.drop_table('tags')
    op.drop_table('handbooks')
    op.drop_table('categories')