from typing import List, Dict, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.context import get_conversation, add_message, get_context_messages
from app.models.schemas import MessageCreate
from app.services.ai_client import ai_client
from app.core.config import settings
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError, APIError
from sqlalchemy import select, and_, desc
from app.db.models import Message
import json

async def process_chat(
    db: AsyncSession,
    session_id: str,
    user_message: str
) -> Dict[str, str]:
    """处理普通聊天请求"""
    # 获取会话
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在")

    try:
        # 保存用户消息
        user_msg = MessageCreate(
            role="user",
            content=user_message
        )
        saved_user_msg = await add_message(db, conversation.id, user_msg)

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
        messages.append({"role": "user", "content": user_message})

        # 生成AI回复
        ai_response = await ai_client.generate_response(messages)

        # 保存AI回复，关联到用户消息
        ai_msg = MessageCreate(
            role="assistant",
            content=ai_response,
            parent_message_id=saved_user_msg.id  # 设置父消息ID，建立问答关系
        )
        await add_message(db, conversation.id, ai_msg)

        return {
            "session_id": session_id,
            "response": ai_response
        }
    except Exception as e:
        app_logger.error(f"处理聊天请求失败: {str(e)}")
        raise

async def initialize_stream_chat(
    db: AsyncSession,
    session_id: str,
    user_message: str
) -> None:
    """初始化流式聊天"""
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在")

    try:
        # 保存用户消息
        user_msg = MessageCreate(role="user", content=user_message)
        saved_user_msg = await add_message(db, conversation.id, user_msg)

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
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        # 初始化流式响应
        await ai_client.initialize_stream(session_id, messages)

    except Exception as e:
        app_logger.error(f"初始化流式聊天失败: {str(e)}")
        raise APIError(detail=f"初始化流式聊天失败: {str(e)}")

async def process_stream_chat(
    db: AsyncSession,
    session_id: str,
) -> AsyncGenerator[str, None]:
    """处理流式聊天响应"""
    conversation = None
    full_response = ""
    
    try:
        conversation = await get_conversation(db, session_id)
        if not conversation:
            raise NotFoundError(detail=f"会话 {session_id} 不存在")

        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'data': {}}, ensure_ascii=False)}\n\n"

        # 使用新的数据库会话来获取最后的用户消息
        last_user_message = await get_last_user_message(db, conversation.id)
        if not last_user_message:
            app_logger.warning(f"未找到用户消息: conversation_id={conversation.id}")
            raise APIError(detail="未找到相关的用户消息")

        async for response_chunk in ai_client.get_stream_response(session_id):
            full_response += response_chunk
            # 发送数据块事件
            chunk_data = {
                'type': 'chunk',
                'data': {
                    'content': response_chunk,
                    'full_text': full_response
                }
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"

        # 发送结束事件
        end_data = {
            'type': 'end',
            'data': {
                'full_text': full_response
            }
        }
        yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"

    except Exception as e:
        app_logger.error(f"处理流式聊天失败: {str(e)}")
        error_data = {
            'type': 'error',
            'data': {
                'message': str(e)
            }
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        return  # 确保在错误情况下提前返回
        
    finally:
        await ai_client.cleanup_stream(session_id)

    # 在生成响应完成后，使用新的事务保存消息
    try:
        if full_response and conversation:
            # 创建并保存AI回复消息
            ai_msg = MessageCreate(
                role="assistant",
                content=full_response,
                parent_message_id=last_user_message.id
            )
            
            # 保存消息并提交事务
            await add_message(db, conversation.id, ai_msg)
            await db.commit()
            
            app_logger.info(
                f"成功保存AI回复消息: conversation_id={conversation.id}, "
                f"parent_message_id={last_user_message.id}, "
                f"content_preview={full_response[:100]}..."
            )
    except Exception as e:
        app_logger.error(f"保存AI回复消息失败: {str(e)}")
        await db.rollback()
        # 这里我们不抛出异常，因为消息已经发送给了用户

async def get_last_user_message(
    db: AsyncSession,
    conversation_id: int
) -> Optional[Message]:
    """获取最后一条用户消息"""
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