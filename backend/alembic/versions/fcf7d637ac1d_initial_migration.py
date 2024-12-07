"""initial_migration

Revision ID: fcf7d637ac1d
Revises: 
Create Date: 2024-11-27 18:24:48.014100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcf7d637ac1d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=True)
    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.String(length=64), nullable=True),
    sa.Column('original_name', sa.String(length=255), nullable=True),
    sa.Column('file_path', sa.String(length=512), nullable=True),
    sa.Column('file_type', sa.String(length=50), nullable=True),
    sa.Column('mime_type', sa.String(length=100), nullable=True),
    sa.Column('file_size', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_session_id', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_file_id'), 'files', ['file_id'], unique=True)
    op.create_index(op.f('ix_files_user_session_id'), 'files', ['user_session_id'], unique=False)
    op.create_table('analysis_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.String(length=64), nullable=True),
    sa.Column('analysis_type', sa.String(length=50), nullable=True),
    sa.Column('result', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['files.file_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('conversation_id', sa.Integer(), nullable=True),
    sa.Column('parent_message_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['file_id'], ['files.file_id'], ),
    sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_table('analysis_records')
    op.drop_index(op.f('ix_files_user_session_id'), table_name='files')
    op.drop_index(op.f('ix_files_file_id'), table_name='files')
    op.drop_table('files')
    op.drop_index(op.f('ix_conversations_session_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_id'), table_name='conversations')
    op.drop_table('conversations')
    # ### end Alembic commands ###
