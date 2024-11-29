from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.models.handbook_schemas import (
    NoteCreate, NoteUpdate, NoteResponse,
    TagResponse
)
from app.services.note_service import note_service
from app.core.logging import app_logger

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/tags", response_model=List[TagResponse])
async def get_tags(db: AsyncSession = Depends(get_db)):
    """获取所有标签列表"""
    try:
        tags = await note_service.get_tags(db)
        if not tags:
            return []
        return tags
    except Exception as e:
        app_logger.error(f"获取标签列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("", response_model=List[NoteResponse])
async def get_notes(
    handbook_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取笔记列表"""
    try:
        return await note_service.get_notes(db, handbook_id, skip, limit)
    except Exception as e:
        app_logger.error(f"获取笔记列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=NoteResponse,
    summary="创建笔记",
    description="在指定手册中创建新笔记",
    response_description="返回创建的笔记信息")
async def create_note(
    note: NoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新笔记
    
    - **title**: 笔记标题
    - **content**: 笔记内容
    - **handbook_id**: 所属手册ID
    - **tags**: 可选的标签列表
    - **priority**: 可选的优先级(high/medium/low)
    - **status**: 可选的状态
    - **is_shared**: 是否共享
    """
    try:
        return await note_service.create_note(db, note)
    except Exception as e:
        app_logger.error(f"创建笔记失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{note_id}", response_model=NoteResponse,
    summary="获取笔记详情",
    description="获取指定笔记的详细信息",
    response_description="返回笔记详情")
async def get_note(
    note_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个笔记的详细信息
    
    - **note_id**: 笔记ID
    """
    note = await note_service.get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    return note

@router.patch("/{note_id}", response_model=NoteResponse,
    summary="更新笔记",
    description="更新指定笔记的信息",
    response_description="返回更新后的笔记信息")
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新笔记信息
    
    - **note_id**: 笔记ID
    - **title**: 可选的新标题
    - **content**: 可选的新内容
    - **tags**: 可选的新标签列表
    - **priority**: 可选的新优先级
    - **status**: 可选的新状态
    - **is_shared**: 可选的共享状态
    """
    try:
        note = await note_service.update_note(db, note_id, note_update)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )
        return note
    except Exception as e:
        app_logger.error(f"更新笔记失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除笔记",
    description="删除指定的笔记",
    response_description="成功删除返回204")
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定笔记
    
    - **note_id**: 要删除的笔记ID
    """
    try:
        success = await note_service.delete_note(db, note_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )
    except Exception as e:
        app_logger.error(f"删除笔记失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 