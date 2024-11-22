from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import Conversation, Message
from app.models.schemas import ConversationCreate, MessageCreate
from app.core.config import settings
from app.services.exceptions import DatabaseError
from app.core.logging import app_logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

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
            content=message.content
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
    limit: int = settings.MAX_CONTEXT_TURNS
) -> List[Message]:
    """获取对话上下文消息"""
    query = select(Message)\
        .where(Message.conversation_id == conversation_id)\
        .order_by(desc(Message.created_at))\
        .limit(limit)
    result = await db.execute(query)
    return list(reversed(result.scalars().all()))

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