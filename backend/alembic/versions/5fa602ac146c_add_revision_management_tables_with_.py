"""Add revision management tables with fixed lengths

Revision ID: 5fa602ac146c
Revises: v1_2_0_handbook
Create Date: 2024-xx-xx xx:xx:xx.xxx
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5fa602ac146c'
down_revision: Union[str, None] = 'v1_2_0_handbook'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note_attachments') as batch_op:
        # 删除现有的外键约束
        batch_op.drop_constraint('note_attachments_ibfk_2', type_='foreignkey')
        # 修改 file_id 列
        batch_op.alter_column('file_id',
                            existing_type=sa.String(length=36),
                            type_=sa.String(length=64),
                            existing_nullable=True)
        # 重新添加外键约束
        batch_op.create_foreign_key('note_attachments_ibfk_2',
                                  'files',
                                  ['file_id'],
                                  ['file_id'])
    op.drop_constraint('note_attachments_ibfk_1', 'note_attachments', type_='foreignkey')
    op.create_foreign_key(None, 'note_attachments', 'files', ['file_id'], ['file_id'])
    op.create_foreign_key(None, 'note_attachments', 'notes', ['note_id'], ['id'])
    op.add_column('note_tags', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.drop_constraint('note_tags_ibfk_2', 'note_tags', type_='foreignkey')
    op.drop_constraint('note_tags_ibfk_1', 'note_tags', type_='foreignkey')
    op.create_foreign_key(None, 'note_tags', 'tags', ['tag_id'], ['id'])
    op.create_foreign_key(None, 'note_tags', 'notes', ['note_id'], ['id'])
    op.add_column('notes', sa.Column('total_revisions', sa.Integer(), nullable=True))
    op.add_column('notes', sa.Column('last_revision_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('notes', sa.Column('current_mastery_level', sa.String(length=50), nullable=True))
    op.alter_column('notes', 'priority',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20),
               type_=sa.Integer(),
               existing_nullable=True)
    op.alter_column('notes', 'status',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20),
               type_=sa.String(length=50),
               existing_nullable=True)
    op.drop_constraint('notes_ibfk_1', 'notes', type_='foreignkey')
    op.create_foreign_key(None, 'notes', 'handbooks', ['handbook_id'], ['id'])
    op.drop_column('notes', 'times')
    op.drop_column('notes', 'user_id')
    op.drop_column('notes', 'category')
    op.alter_column('tags', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('tags', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note_attachments') as batch_op:
        # 删除现有的外键约束
        batch_op.drop_constraint('note_attachments_ibfk_2', type_='foreignkey')
        # 恢复 file_id 列的原始长度
        batch_op.alter_column('file_id',
                            existing_type=sa.String(length=64),
                            type_=sa.String(length=36),
                            existing_nullable=True)
        # 重新添加外键约束
        batch_op.create_foreign_key('note_attachments_ibfk_2',
                                  'files',
                                  ['file_id'],
                                  ['file_id'])
    op.alter_column('tags', 'updated_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    op.alter_column('tags', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.add_column('notes', sa.Column('category', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=True))
    op.add_column('notes', sa.Column('user_id', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False))
    op.add_column('notes', sa.Column('times', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'notes', type_='foreignkey')
    op.create_foreign_key('notes_ibfk_1', 'notes', 'handbooks', ['handbook_id'], ['id'], ondelete='CASCADE')
    op.alter_column('notes', 'status',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20),
               existing_nullable=True)
    op.alter_column('notes', 'priority',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20),
               existing_nullable=True)
    op.drop_column('notes', 'current_mastery_level')
    op.drop_column('notes', 'last_revision_date')
    op.drop_column('notes', 'total_revisions')
    op.drop_constraint(None, 'note_tags', type_='foreignkey')
    op.drop_constraint(None, 'note_tags', type_='foreignkey')
    op.create_foreign_key('note_tags_ibfk_1', 'note_tags', 'notes', ['note_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('note_tags_ibfk_2', 'note_tags', 'tags', ['tag_id'], ['id'], ondelete='CASCADE')
    op.drop_column('note_tags', 'created_at')
    # ### end Alembic commands ###
