from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)
from app.services import context as context_service
from app.core.logging import app_logger
from app.services.exceptions import DatabaseError
from typing import List

router = APIRouter(prefix="/context", tags=["context"])

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新会话"""
    try:
        app_logger.debug(f"收到创建会话请求: {conversation.model_dump()}")
        db_conversation = await context_service.create_conversation(db, conversation)
        return db_conversation
    except DatabaseError as e:
        app_logger.error(f"创建会话失败: {str(e)}")
        if "已存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/conversations/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取指定会话信息"""
    conversation = await context_service.get_conversation(db, session_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return conversation

@router.post("/conversations/{session_id}/messages", response_model=MessageResponse)
async def add_message(
    session_id: str,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加消息到会话"""
    conversation = await context_service.get_conversation(db, session_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    try:
        return await context_service.add_message(db, conversation.id, message)
    except DatabaseError as e:
        app_logger.error(f"添加消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/conversations/{session_id}/context")
async def clear_context(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """清除指定会话的上下文"""
    try:
        success = await context_service.clear_context(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        return {"message": "上下文已清除"}
    except DatabaseError as e:
        app_logger.error(f"清除上下文失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_all_conversations(
    db: AsyncSession = Depends(get_db)
):
    """获取所有会话列表"""
    try:
        conversations = await context_service.get_all_conversations(db)
        return conversations
    except DatabaseError as e:
        app_logger.error(f"获取会话列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
