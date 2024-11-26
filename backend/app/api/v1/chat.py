from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, MessageResponse, ImageChatRequest, ImageChatResponse, FileChatRequest, FileChatResponse
from app.services import chat as chat_service
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError
from app.services.ai_client import ai_client
from app.services.context import get_conversation, get_context_messages
from app.services.file_service import file_service
from app.services.image_service import image_service
from app.services.file_service import UploadFile
from app.services.document_service import document_service
import json
import asyncio
import uuid
from typing import List
import base64
from io import BytesIO
import imghdr

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
        app_logger.error(f"初始化流式聊天失败: {str(e)}")
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
        
        # 直接使用URL分析图片
        result = await image_service.analyze_image_from_url(
            db=db,
            image_url=request.image,
            query=request.message,
            extract_text=request.extract_text,
            system_prompt=request.system_prompt,
            session_id=session_id
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