from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.context import get_conversation, add_message, get_context_messages
from app.models.schemas import MessageCreate
from app.services.ai_client import ai_client
from app.core.config import settings
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError, APIError
from sqlalchemy import select, and_, desc
from app.db.models import Message, File
import json
from pathlib import Path
import aiofiles
import aiohttp
import uuid

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
            content=user_message,
            file_id=None
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
        raise NotFoundError(detail=f"话 {session_id} 不存在")

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

        # 初始化流响应
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

        # 使用新的据库会话来获取最后的用户消息
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

async def init_image_stream_chat(
    db: AsyncSession,
    session_id: str,
    message: str,
    image_url: str,
    file_id: str
) -> None:
    """初始化流式图片聊天"""
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在")

    try:
        # 保存用户消息到数据库
        user_msg = MessageCreate(
            role="user",
            content=message,     # 只存储纯文本消息
            file_id=file_id      # 文件ID存储在专门的字段中
        )
        saved_user_msg = await add_message(db, conversation.id, user_msg)

        # 获取上下文消息
        context_messages = await get_context_messages(
            db,
            conversation.id,
            settings.MAX_CONTEXT_TURNS
        )

        # 转换为AI客户端所需格式
        messages = []
        for msg in context_messages[:-1]:  # 排除最后条消息
            message_data = {"role": msg.role, "content": msg.content}
            if msg.file_id:  # 如果消息关联文件，添加文件信息
                # 获取文件信息
                file_query = select(File).where(File.file_id == msg.file_id)
                result = await db.execute(file_query)
                file_record = result.scalar_one_or_none()
                if file_record and file_record.file_type == "image":
                    message_data["content"] = [
                        {"type": "text", "text": msg.content},
                        {"type": "image_url", "image_url": {"url": file_record.file_path}}
                    ]
            messages.append(message_data)

        # 添加当前用户消息，使用正确的Vision API格式
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        })

        # 初始化流式响应
        await ai_client.initialize_stream(
            session_id=session_id,
            messages=messages,
            model=ai_client.vision_model
        )

    except Exception as e:
        app_logger.error(f"始化流式图片聊天失败: {str(e)}")
        raise APIError(detail=f"初始化流式图片聊天失败: {str(e)}")

async def init_file_stream_chat(
    db: AsyncSession,
    session_id: str,
    message: str,
    file_id: str,
    file_type: str,
    file_text: str
) -> None:
    """初始化流式文件聊天"""
    conversation = await get_conversation(db, session_id)
    if not conversation:
        raise NotFoundError(detail=f"会话 {session_id} 不存在")

    try:
        # 保存用户消息到数据库
        user_msg = MessageCreate(
            role="user",
            content=message,
            file_id=file_id
        )
        saved_user_msg = await add_message(db, conversation.id, user_msg)

        # 获取上下文消息
        context_messages = await get_context_messages(
            db,
            conversation.id,
            settings.MAX_CONTEXT_TURNS
        )

        # 转换为AI客户端所需格式
        messages = []
        for msg in context_messages[:-1]:  # 排除最后一条消息
            message_data = {"role": msg.role, "content": msg.content}
            messages.append(message_data)

        # 添加当前用户消息，包含文件内容
        if file_type == "image":
            file_query = select(File).where(File.file_id == file_id)
            result = await db.execute(file_query)
            file_record = result.scalar_one_or_none()
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {"type": "image_url", "image_url": {"url": file_record.file_path}}
                ]
            })
        else:
            # 对于文档类型，将文件内容添加到消息中
            messages.append({
                "role": "user",
                "content": f"{message}\n\n文档内容：\n{file_text}"
            })

        # 初始化流式响应
        model = ai_client.vision_model if file_type == "image" else ai_client.model
        await ai_client.initialize_stream(
            session_id=session_id,
            messages=messages,
            model=model
        )

    except Exception as e:
        app_logger.error(f"初始化流式文件聊天失败: {str(e)}")
        raise APIError(detail=f"初始化流式文件聊天失败: {str(e)}")

@staticmethod
async def extract_text(file_path: str) -> str:
    """从文件中提取文本"""
    try:
        # 如果是URL，尝试下载文件内容
        if file_path.startswith(('http://', 'https://')):
            async with aiohttp.ClientSession() as session:
                async with session.get(file_path) as response:
                    if response.status == 200:
                        file_content = await response.read()
                        if file_path.endswith('.docx'):
                            from docx import Document
                            import io
                            doc = Document(io.BytesIO(file_content))
                            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                        return await response.text()
                    else:
                        return f"无法访问文件: {response.status}"

        # 获取文件后缀
        suffix = Path(file_path).suffix.lower()
        
        # Word文档处理
        if suffix in ['.doc', '.docx']:
            try:
                from docx import Document
                import asyncio
                
                # 使用线程池执行同步操作
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: '\n'.join(
                    [paragraph.text for paragraph in Document(file_path).paragraphs]
                ))
            except Exception as e:
                app_logger.error(f"Word文档处理失败: {str(e)}")
                return f"Word文档处理失败: {str(e)}"
                
        # 文本文件处理
        elif suffix in ['.txt', '.md']:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
                
        # PDF文件处理
        elif suffix == '.pdf':
            try:
                from pypdf import PdfReader
                import asyncio
                
                # 使用线程池执行同步操作
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: '\n'.join(
                    [page.extract_text() for page in PdfReader(file_path).pages]
                ))
            except Exception as e:
                app_logger.error(f"PDF文件处理失败: {str(e)}")
                return f"PDF文件处理失败: {str(e)}"
        
        else:
            return f"不支持的文件类型: {suffix}"

    except Exception as e:
        app_logger.error(f"文本提取失败: {str(e)}")
        return f"文本提取失败: {str(e)}"

async def initialize_message_analysis_stream(
    messages: List[Dict[str, Any]],
    system_prompt: Optional[str] = None
) -> str:
    """初始化消息分析流
    
    Args:
        messages: 消息列表，每个消息包含 role 和 content
        system_prompt: 可选的系统提示
    
    Returns:
        str: 分析会话ID
    """
    try:
        print("process_message_analysis_stream***********************")
        # 构建分析提示
        message_texts = []
        for msg in messages:
            # 使用字典访问语法获取role和content
            formatted_msg = f"{msg['role']}: {msg['content']}"
            message_texts.append(formatted_msg)
            
        combined_message = "\n".join(message_texts)
        analysis_prompt = f"""请分析以下对话内容:
{combined_message}

请提供:
1. 一个不超过30个字的精简标题
2. 提取有效的关键字
3. 提取考点，要点, 简短
4. 请分析内容，结构清晰，内容完整

输出格式:
标题: <标题>

关键字: <关键字>

要点: <要点>

 <分析内容>"""

        # 构建消息列表
        prompt_messages = []
        if system_prompt:
            prompt_messages.append({"role": "system", "content": system_prompt})
        prompt_messages.append({"role": "user", "content": analysis_prompt})
        # 初始化分析流并返回会话ID
        session_id = await ai_client.initialize_analysis_stream(
            messages=prompt_messages,
            temperature=0.7
        )
        app_logger.info(f"成功初始化消息分析流，会话ID: {session_id}")
        return session_id
    except Exception as e:
        app_logger.error(f"初始化消息分析流失败: {str(e)}")
        raise APIError(f"初始化消息分析流失败: {str(e)}")

async def get_message_analysis_stream(session_id: str) -> AsyncGenerator[str, None]:
    """获取消息分析的流式响应"""
    try:
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'data': {}}, ensure_ascii=False)}\n\n"
        
        # 检查会话是否存在
        is_active = await ai_client.is_session_active(session_id)
        if not is_active:
            error_data = {
                'type': 'error',
                'data': {
                    'message': '会话未初始化或已过期'
                }
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            return

        full_response = ""
        async for chunk in ai_client.get_analysis_stream(session_id):
            # 确保chunk是UTF-8编码
            if isinstance(chunk, bytes):
                chunk = chunk.decode('utf-8')
            
            full_response += chunk
            # 构建数据块事件并确保使用UTF-8编码
            chunk_data = {
                'type': 'chunk',
                'data': {
                    'content': chunk,
                    'section': 'analysis',
                    'full_text': full_response
                }
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n".encode('utf-8').decode('utf-8')

        # 发送结束事件
        end_data = {
            'type': 'end',
            'data': {
                'full_text': full_response
            }
        }
        yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n".encode('utf-8').decode('utf-8')

    except Exception as e:
        app_logger.error(f"获取消息分析流失败: {str(e)}")
        error_data = {
            'type': 'error',
            'data': {
                'message': str(e)
            }
        }
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"