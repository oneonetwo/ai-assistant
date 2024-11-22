from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services import chat as chat_service
from app.core.logging import app_logger
from app.services.exceptions import NotFoundError
from app.services.ai_client import ai_client
import json
import asyncio
import uuid

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
    await chat_service.process_stream_chat(db, session_id, request.message)
    return {"status": "initialized"}

@router.get("/{session_id}/stream")
async def stream_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """处理SSE流式响应"""
    return StreamingResponse(
        ai_client.generate_stream_events(session_id),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    ) 