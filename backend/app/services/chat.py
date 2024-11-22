from typing import List, Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.context import get_conversation, add_message, get_context_messages
from app.models.schemas import MessageCreate
from app.services.ai_client import ai_client
from app.core.config import settings
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError

async def process_chat(
    db: AsyncSession,
    session_id: str,
    user_message: str
) -> Dict[str, str]:
    """处理普通聊天请求"""
    # 获取会话
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在，请先创建会话")

    try:
        # 保存用户消息
        user_msg = MessageCreate(role="user", content=user_message)
        await add_message(db, conversation.id, user_msg)

        # 获取上下文消息
        context_messages = await get_context_messages(
            db,
            conversation.id,
            settings.MAX_CONTEXT_TURNS
        )

        # 转换为AI客户端所需格式
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in context_messages
        ]

        # 生成AI回复
        ai_response = await ai_client.generate_response(messages)

        # 保存AI回复
        ai_msg = MessageCreate(role="assistant", content=ai_response)
        await add_message(db, conversation.id, ai_msg)

        return {
            "session_id": session_id,
            "response": ai_response
        }
    except Exception as e:
        app_logger.error(f"处理聊天请求失败: {str(e)}")
        raise

async def process_stream_chat(
    db: AsyncSession,
    session_id: str,
    user_message: str
) -> None:
    """处理流式聊天请求"""
    # 获取会话
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在，请先创建会话")

    try:
        # 保存用户消息
        user_msg = MessageCreate(role="user", content=user_message)
        await add_message(db, conversation.id, user_msg)

        # 获取上下文消息
        context_messages = await get_context_messages(
            db,
            conversation.id,
            settings.MAX_CONTEXT_TURNS
        )

        # 转换为AI客户端所需格式
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in context_messages
        ]

        # 初始化流式响应
        await ai_client.initialize_stream(session_id, messages)

    except Exception as e:
        app_logger.error(f"处理流式聊天请求失败: {str(e)}")
        raise 