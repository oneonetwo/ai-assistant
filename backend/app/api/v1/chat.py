from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, MessageResponse
from app.services import chat as chat_service
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError
from app.services.ai_client import ai_client
from app.services.context import get_conversation, get_context_messages
import json
import asyncio
import uuid
from typing import List

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/{session_id}", response_model=ChatResponse)
async def chat(
    session_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """处理普通聊天请求"""
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

@router.get("/{session_id}/stream")
async def stream_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """处理SSE流式响应"""
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