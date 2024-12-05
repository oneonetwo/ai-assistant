"""add_revision_task_fields

Revision ID: 90b71a2a9895
Revises: 39251e0dfc04
Create Date: 2024-12-04 10:36:28.675357

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '90b71a2a9895'
down_revision: Union[str, None] = '39251e0dfc04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 添加新字段到 revision_tasks 表
    op.add_column('revision_tasks', sa.Column('revision_mode', sa.String(length=20), nullable=True))
    op.add_column('revision_tasks', sa.Column('priority', sa.Integer(), nullable=True))
    op.add_column('revision_tasks', sa.Column('updated_at', sa.DateTime(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))

def downgrade() -> None:
    # 删除添加的字段
    op.drop_column('revision_tasks', 'updated_at')
    op.drop_column('revision_tasks', 'priority')
    op.drop_column('revision_tasks', 'revision_mode')
    op.drop_column('revision_histories', 'time_spent')
    op.drop_column('revision_histories', 'revision_mode')
    op.alter_column('notes', 'priority',
               existing_type=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50),
               nullable=False)
    op.alter_column('note_attachments', 'file_id',
               existing_type=sa.String(length=36),
               type_=mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=64),
               existing_nullable=True)
    # ### end Alembic commands ###
