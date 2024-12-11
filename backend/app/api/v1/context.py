from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationUpdate
)
from app.services import context as context_service
from app.core.logging import app_logger
from app.services.exceptions import DatabaseError
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.models import Conversation, File
from sqlalchemy import desc, asc
import json

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
        # 获取所有会话及其关联的消息
        stmt = (
            select(Conversation)
            .options(joinedload(Conversation.messages))
            .order_by(desc(Conversation.updated_at))
        )
        result = await db.execute(stmt)
        conversations = result.unique().scalars().all()
        
        # 转换响应格式
        response_conversations = []
        for conv in conversations:
            # 按创建时间升序排序消息
            sorted_messages = sorted(conv.messages, key=lambda msg: msg.created_at)
            
            messages = []
            for msg in sorted_messages:
                # 如果消息有关联文件，获取文件信息
                file_info = None
                if msg.file_id:
                    file_stmt = select(File).where(File.file_id == msg.file_id)
                    file_result = await db.execute(file_stmt)
                    file = file_result.scalar_one_or_none()
                    if file:
                        file_info = {
                            "file_id": file.file_id,
                            "original_name": file.original_name,
                            "file_type": file.file_type,
                            "file_path": file.file_path,
                            "mime_type": file.mime_type,
                            "file_size": file.file_size,
                            "created_at": file.created_at.isoformat() if file.created_at else None
                        }

                # 使用 MessageResponse 的 from_db_model 方法创建消息响应
                message = MessageResponse.from_db_model(msg, file_info)
                messages.append(message)

            # 构建会话响应
            conv_response = ConversationResponse(
                session_id=conv.session_id,
                name=conv.name,
                id=conv.id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                messages=messages
            )
            response_conversations.append(conv_response)
        
        return response_conversations
        
    except Exception as e:
        app_logger.error(f"获取会话列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/conversations/{session_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除指定会话及其所有消息"""
    try:
        success = await context_service.delete_conversation(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
        return {"message": "会话已删除"}
    except DatabaseError as e:
        app_logger.error(f"删除会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/conversations/{session_id}", response_model=ConversationResponse)
async def update_conversation(
    session_id: str,
    update_data: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新会话信息"""
    try:
        conversation = await context_service.update_conversation_name(
            db,
            session_id,
            update_data.name
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在"
            )
            
        # 转换日期时间为ISO格式字符串
            
        # 转换日期时间为ISO格式字符串
        response = ConversationResponse(
            id=conversation.id,
            session_id=conversation.session_id,
            name=conversation.name,
            created_at=conversation.created_at.isoformat() if conversation.created_at else None,
            updated_at=conversation.updated_at.isoformat() if conversation.updated_at else None,
            messages=[
                MessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat() if msg.created_at else None,
                    parent_message_id=msg.parent_message_id,
                    file_id=msg.file_id
                ) for msg in conversation.messages
            ] if conversation.messages else []
        )
        
        return response
        

    except DatabaseError as e:
        app_logger.error(f"更新会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
