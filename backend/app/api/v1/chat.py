from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.schemas import (
    ChatRequest, 
    ChatResponse, 
    MessageResponse, 
    ImageChatRequest, 
    ImageChatResponse, 
    FileChatRequest, 
    FileChatResponse, 
    MessageCreate
)
from app.db.models import File
from app.services import chat as chat_service
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError, APIError
from app.services.ai_client import ai_client
from app.services.context import get_conversation, get_context_messages, add_message, get_last_user_message
from app.services.file_service import file_service, UploadFile
from app.services.image_service import image_service
from app.services.document_service import document_service
from app.core.config import settings
import json
import asyncio
import uuid
from typing import List, Dict, Any, Optional
import base64
from io import BytesIO
import imghdr
import aiohttp
import io
from docx import Document
from pathlib import Path
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/{session_id}", response_model=ChatResponse, 
    summary="发送聊天消息",
    description="发送一条消息并获取AI回复")
async def chat(
    session_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理普通聊天请求
    
    - **session_id**: 会话ID
    - **message**: 用户消息
    - **system_prompt**: 可选的系统提示
    """
    try:
        # 添加请求日志
        app_logger.debug(f"收到聊天请求: session_id={session_id}, request={request.model_dump()}")
        
        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式，请使用有效的UUID"
            )

        # 处理聊天请求
        response = await chat_service.process_chat(
            db,
            session_id,
            request.message
        )
        return ChatResponse(**response)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        app_logger.error(f"聊天处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="聊天处理失败"
        )

@router.post("/{session_id}/stream")
async def init_stream_chat(
    session_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """初始化流式聊天"""
    try:
        # 初始化会话（如果需要）
        if not ai_client.is_session_initialized(session_id):
            await ai_client.init_session(session_id)
            
        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式，请使用有效的UUID"
            )

        # 如果已经初始化，先清理旧的流
        if ai_client.is_session_initialized(session_id):
            await ai_client.cleanup_stream(session_id)

        # 初始化新的流式聊天
        await chat_service.initialize_stream_chat(db, session_id, request.message)
        return {"status": "initialized"}
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        app_logger.error(f"初始化流式聊失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="初始化流式聊天失败"
        )

@router.get("/{session_id}/stream",
    summary="获取流式响应",
    description="获流式聊天的SSE响应")
async def stream_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    处理SSE流式响应
    
    - **session_id**: 会话ID
    """
    try:
        # 验证会话是否已初始化
        if not ai_client.is_session_initialized(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话未初始化，请先调用初始化接口"
            )

        return StreamingResponse(
            chat_service.process_stream_chat(db, session_id),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream',
                # 添加CORS相关头
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    except Exception as e:
        app_logger.error(f"处理流式响应失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理流式响应失败"
        )

@router.get("/{session_id}/history", response_model=List[MessageResponse])
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取完整的对话历史"""
    try:
        conversation = await get_conversation(db, session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
            
        messages = await get_context_messages(
            db,
            conversation.id,
            limit=100  # 可以根据需求调整限制
        )
        
        return messages
    except Exception as e:
        app_logger.error(f"获取对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话历史失败"
        )

@router.post("/{session_id}/image", response_model=ImageChatResponse)
async def image_chat(
    session_id: str,
    request: ImageChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理图片聊天请求
    
    - **session_id**: 会话ID
    - **message**: 用户消息
    - **image**: 图片URL
    - **system_prompt**: 可选的系统提示
    - **extract_text**: 是否提取图片文字
    """
    try:
        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式"
            )
            
        # 创建文件记录
        file_id = str(uuid.uuid4())
        file_record = File(
            file_id=file_id,
            original_name=Path(request.image).name,  # 从URL提取文件名
            file_path=request.image,  # 存储图片URL
            file_type="image",
            mime_type="image/*",  # 简化MIME类型
            file_size=0,  # 远程文件不需要记录大小
            user_session_id=session_id
        )
        db.add(file_record)
        await db.commit()
        
        # 分析图片
        result = await image_service.analyze_image_from_url(
            db=db,
            image_url=request.image,
            query=request.message,
            extract_text=request.extract_text,
            system_prompt=request.system_prompt,
            session_id=session_id,
            file_id=file_id  # 添加file_id参数
        )
        
        return ImageChatResponse(**result)
        
    except Exception as e:
        app_logger.error(f"图片聊天处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{session_id}/file", response_model=FileChatResponse,
    summary="发送带文件的聊天消息",
    description="发送带文件（如文档、图片等）的消息并获取AI回复")
async def file_chat(
    session_id: str,
    request: FileChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    处理带文件的聊天请求
    
    - **session_id**: 会话ID
    - **message**: 用户消息
    - **file**: base64编码的文件
    - **file_name**: 文件名
    - **file_type**: 文件类型 (image/document)
    - **system_prompt**: 可选的系统提示
    """
    try:
        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式"
            )

        # 解码base64文件内容
        file_content = base64.b64decode(request.file)
        file_obj = UploadFile(
            filename=request.file_name,
            file=BytesIO(file_content)
        )
        
        # 保存文件
        saved_file = await file_service.save_file(
            file=file_obj,
            file_type=request.file_type,
            db=db,
            session_id=session_id
        )

        # 根据文件类型选择处理方法
        if request.file_type == "image":
            result = await analyze_image(
                db=db,
                file_id=saved_file.file_id,
                query=request.message,
                system_prompt=request.system_prompt
            )
            response = result["analysis"]
        else:
            # 处理文档类型文件
            result = await document_service.analyze_document(
                db=db,
                file_id=saved_file.file_id,
                query=request.message,
                system_prompt=request.system_prompt
            )
            response = result["analysis"]

        return FileChatResponse(
            session_id=session_id,
            response=response,
            file_id=saved_file.file_id
        )

    except Exception as e:
        app_logger.error(f"处理带文件的聊天请求失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 

@router.post("/{session_id}/image/stream")
async def init_image_stream_chat(
    session_id: str,
    request: ImageChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """初始化图片流式聊天"""
    try:
        # 创建文件记录
        file_id = str(uuid.uuid4())
        file_record = File(
            file_id=file_id,
            original_name=Path(request.image).name,
            file_path=request.image,
            file_type="image",
            mime_type="image/*",
            file_size=0,
            user_session_id=session_id
        )
        db.add(file_record)
        await db.commit()

        # 初始化流式聊天
        await chat_service.init_image_stream_chat(
            db=db,
            session_id=session_id,
            message=request.message,
            image_url=request.image,
            file_id=file_id
        )

        return {
            "status": "initialized",
            "file_id": file_id
        }

    except Exception as e:
        app_logger.error(f"初始化流式图片聊天失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{session_id}/image/stream",
    summary="获取图片分析流式响应",
    description="获取图片分析的SSE流式响应")
async def stream_image_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    async def generate_stream():
        try:
            conversation = await get_conversation(db, session_id)
            if not conversation:
                raise NotFoundError("会话不存在")

            # 获取最后一条用户消息
            last_message = await get_last_user_message(db, conversation.id)
            if not last_message:
                raise NotFoundError("未找到用户消息")
            
            # 获取文件信息
            file_query = select(File).where(File.file_id == last_message.file_id)
            result = await db.execute(file_query)
            file_record = result.scalar_one_or_none()
            
            if not file_record:
                raise NotFoundError("图片文件不存在")

            # 生成AI响应流
            full_response = ""
            async for chunk in ai_client.get_stream_response(session_id):
                full_response += chunk
                chunk_data = {
                    'type': 'chunk',
                    'data': {
                        'content': chunk,
                        'full_text': full_response
                    }
                }
                yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"

            # 保存AI响应
            ai_msg = MessageCreate(
                role="assistant",
                content=full_response,
                parent_message_id=last_message.id
            )
            await add_message(db, conversation.id, ai_msg)

            # 发送结束事件
            end_data = {
                'type': 'end',
                'data': {
                    'full_text': full_response
                }
            }
            yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            app_logger.error(f"处理图片分析流失败: {str(e)}")
            error_data = {
                'type': 'error',
                'data': {
                    'message': str(e)
                }
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )

@router.post("/{session_id}/file/stream")
async def handle_file_stream_chat(
    session_id: str,
    request: FileChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 初始化会话（如果需要）
        if not ai_client.is_session_initialized(session_id):
            await ai_client.init_session(session_id)

        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式"
            )

        # 获取会话
        conversation = await get_conversation(db, session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        # 从文件URL提取文本
        file_text = await chat_service.extract_text(request.file)

        # 简化文件类型
        simplified_file_type = "document"  # 默认为文档类型
        if request.file_type.startswith('image/'):
            simplified_file_type = "image"
        elif request.file_type.startswith('video/'):
            simplified_file_type = "video"
        elif request.file_type.startswith('audio/'):
            simplified_file_type = "audio"

        # 创建文件记录
        file_id = str(uuid.uuid4())
        file_record = File(
            file_id=file_id,
            original_name=request.file_name,
            file_path=request.file,
            file_type=simplified_file_type,
            mime_type=request.file_type,
            file_size=0,
            user_session_id=session_id
        )
        db.add(file_record)
        await db.commit()

        # 初始化流式聊天
        await chat_service.init_file_stream_chat(
            db=db,
            session_id=session_id,
            message=request.message,
            file_id=file_id,
            file_type=simplified_file_type,
            file_text=file_text
        )

        return {
            "status": "initialized",
            "file_id": file_id
        }

    except Exception as e:
        app_logger.error(f"处理文件流式聊天失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{session_id}/file/stream",
    summary="获取文件分析流式响应",
    description="获取文件分析的SSE流式响应")
async def stream_file_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 验证会话是否已初始化
        if not ai_client.is_session_initialized(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="会话未初始化，请先调用初始化接口"
            )

        return StreamingResponse(
            chat_service.process_stream_chat(db, session_id),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    except Exception as e:
        app_logger.error(f"处理文件分析流失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{session_id}/file/stream",
    summary="处理文件流式聊天",
    description="处理文件流式聊天请求并返回流式响应")
async def handle_file_stream_chat(
    session_id: str,
    request: FileChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 验证session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会话ID格式"
            )

        # 获取会话
        conversation = await get_conversation(db, session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )

        # 创建文件记录
        file_id = str(uuid.uuid4())
        file_record = File(
            file_id=file_id,
            original_name=request.file_name,
            file_path=request.file,
            file_type=request.file_type,
            mime_type=request.file_type,
            file_size=0,
            user_session_id=session_id
        )
        db.add(file_record)
        await db.commit()

        # 初始化流式聊天
        await chat_service.init_file_stream_chat(
            db=db,
            session_id=session_id,
            message=request.message,
            file_id=file_id,
            file_type=request.file_type
        )

        # 返回流式响应
        return StreamingResponse(
            chat_service.process_stream_chat(db, session_id),
            media_type="text/event-stream"
        )

    except Exception as e:
        app_logger.error(f"处理文件流式聊天失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 

class MessageAnalysisRequest(BaseModel):
    messages: List[str]
    system_prompt: Optional[str] = None

@router.post("/analyze/stream/init",
    summary="初始化消息分析流",
    description="初始化一个或多个消息的分析流")
async def init_message_analysis_stream(
    request: MessageAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    初始化消息分析流
    
    - **messages**: 消息内容列表
    - **system_prompt**: 可选的系统提示
    """
    try:
        await chat_service.initialize_message_analysis_stream(
            request.messages,
            request.system_prompt
        )
        return {"status": "initialized"}
    except Exception as e:
        app_logger.error(f"初始化消息分析流失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="初始化消息分析流失败"
        )

@router.get("/analyze/stream",
    summary="获取消息分析流式响应",
    description="获取消息分析的SSE流式响应")
async def get_message_analysis_stream():
    """获取消息分析的流式响应"""
    try:
        return StreamingResponse(
            chat_service.get_message_analysis_stream(),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    except Exception as e:
        app_logger.error(f"获取消息分析流失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取消息分析流失败"
        ) 