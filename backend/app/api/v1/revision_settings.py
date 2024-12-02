from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.revision_notification_schemas import (
    RevisionSettingsUpdate,
    RevisionSettingsResponse,
    RevisionHistoryEntry,
    RevisionStatistics
)
from app.services.notification_service import NotificationService
from app.services.history_service import HistoryService
from datetime import datetime
from typing import List

router = APIRouter(prefix="/revision-settings", tags=["revision-settings"])

@router.get("/notifications/summary",
    summary="获取任务摘要",
    description="获取今日复习任务的摘要信息",
    response_description="返回任务摘要信息"
)
async def get_daily_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    获取今日任务摘要
    
    返回：
    - 今日待复习任务数量
    - 任务完成进度
    """
    return await NotificationService.get_daily_summary(db, datetime.now())

@router.get("/settings", response_model=RevisionSettingsResponse,
    summary="获取提醒设置",
    description="获取用户的复习提醒设置"
)
async def get_notification_settings(
    db: AsyncSession = Depends(get_db)
):
    """
    获取提醒设置
    
    返回：
    - 是否启用提醒
    - 提醒时间
    """
    return await NotificationService.get_settings()

@router.patch("/settings", response_model=RevisionSettingsResponse,
    summary="更新提醒设置",
    description="更新用户的复习提醒设置"
)
async def update_notification_settings(
    settings: RevisionSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新提醒设置
    
    - **settings**: 设置更新参数
        - reminder_enabled: 是否启用提醒
        - reminder_time: 提醒时间 (HH:MM)
    """
    return await NotificationService.update_settings(
        db,
        reminder_enabled=settings.reminder_enabled,
        reminder_time=settings.reminder_time
    )

@router.get("/history/note/{note_id}", response_model=List[RevisionHistoryEntry],
    summary="获取笔记复习历史",
    description="获取特定笔记的复习历史记录"
)
async def get_note_history(
    note_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取笔记复习历史
    
    - **note_id**: 笔记ID
    
    返回：
    - 复习历史记录列表
    - 每次复习的掌握状态
    - 复习时间
    """
    return await HistoryService.get_note_history(db, note_id)

@router.get("/statistics/note/{note_id}", response_model=RevisionStatistics,
    summary="获取笔记统计信息",
    description="获取特定笔记的复习统计数据"
)
async def get_note_statistics(
    note_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取笔记统计信息
    
    - **note_id**: 笔记ID
    
    返回：
    - 复习统计数据
    """
    return await HistoryService.get_note_statistics(db, note_id) 