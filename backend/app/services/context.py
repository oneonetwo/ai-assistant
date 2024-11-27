from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import Conversation, Message, File
from app.models.schemas import ConversationCreate, MessageCreate, MessageResponse
from app.core.config import settings
from app.services.exceptions import DatabaseError
from app.core.logging import app_logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
import json

async def create_conversation(
    db: AsyncSession,
    conversation: ConversationCreate
) -> Conversation:
    """创建新的对话会话"""
    try:
        # 先检查session_id是否已存在
        existing = await get_conversation(db, conversation.session_id)
        if existing:
            raise DatabaseError(detail=f"会话ID '{conversation.session_id}' 已存在")
            
        db_conversation = Conversation(session_id=conversation.session_id)
        db.add(db_conversation)
        await db.commit()
        await db.refresh(db_conversation)
        return db_conversation
    except IntegrityError as e:
        app_logger.error(f"创建对话失败: {str(e)}")
        raise DatabaseError(detail=f"会话ID '{conversation.session_id}' 已存在")
    except Exception as e:
        app_logger.error(f"创建对话失败: {str(e)}")
        raise DatabaseError(detail="创建对话失败")

async def get_conversation(
    db: AsyncSession,
    session_id: str
) -> Optional[Conversation]:
    """获取指定会话ID的对话及其消息"""
    query = (
        select(Conversation)
        .where(Conversation.session_id == session_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def add_message(
    db: AsyncSession,
    conversation_id: int,
    message: MessageCreate
) -> Message:
    """添加消息到对话"""
    try:
        db_message = Message(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            parent_message_id=message.parent_message_id,
            file_id=message.file_id
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message
    except Exception as e:
        app_logger.error(f"添加消息失败: {str(e)}")
        raise DatabaseError(detail="添加消息失败")

async def get_context_messages(
    db: AsyncSession,
    conversation_id: int,
    limit: int = None
) -> List[MessageResponse]:
    # 构建查询
    query = (
        select(Message, File)
        .outerjoin(File, File.file_id == Message.file_id)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
    )
    
    if limit:
        query = query.limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    messages = []
    for row in rows:
        message = row[0]
        file = row[1]
        
        file_info = None
        if file:
            file_info = {
                "file_id": file.file_id,
                "original_name": file.original_name,
                "file_type": file.file_type,
                "file_path": file.file_path
            }
        
        messages.append(MessageResponse.from_db_model(message, file_info))
    
    return list(reversed(messages))

async def clear_context(
    db: AsyncSession,
    session_id: str
) -> bool:
    """清除指定会话的上下文"""
    try:
        conversation = await get_conversation(db, session_id)
        if not conversation:
            return False
        
        # 删除所有相关消息
        await db.execute(
            select(Message).where(Message.conversation_id == conversation.id).delete()
        )
        await db.commit()
        return True
    except Exception as e:
        app_logger.error(f"清除上下文失败: {str(e)}")
        raise DatabaseError(detail="清除上下文失败")

async def get_all_conversations(db: AsyncSession) -> List[Conversation]:
    """获取所有会话"""
    try:
        query = select(Conversation).order_by(desc(Conversation.updated_at))
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        app_logger.error(f"获取所有会话失败: {str(e)}")
        raise DatabaseError(detail="获取会话列表失败")

async def delete_conversation(
    db: AsyncSession,
    session_id: str
) -> bool:
    """删除指定会话及其所有消息"""
    try:
        # 查找会话
        conversation = await get_conversation(db, session_id)
        if not conversation:
            return False
        
        # 由于设置了 CASCADE，删除会话时会自动删除相关消息
        await db.delete(conversation)
        await db.commit()
        
        return True
    except Exception as e:
        app_logger.error(f"删除会话失败: {str(e)}")
        raise DatabaseError(detail="删除会话失败")

async def update_conversation_name(
    db: AsyncSession,
    session_id: str,
    name: str
) -> Optional[Conversation]:
    """更新会话名称"""
    try:
        conversation = await get_conversation(db, session_id)
        if not conversation:
            return None
            
        conversation.name = name
        await db.commit()
        await db.refresh(conversation)
        return conversation
    except Exception as e:
        app_logger.error(f"更新会话名称失败: {str(e)}")
        raise DatabaseError(detail="更新会话名称失败")

async def get_last_user_message(
    db: AsyncSession,
    conversation_id: int
) -> Optional[Message]:
    """获取会话中最后一条用户消息"""
    query = (
        select(Message)
        .where(
            and_(
                Message.conversation_id == conversation_id,
                Message.role == "user"
            )
        )
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
  