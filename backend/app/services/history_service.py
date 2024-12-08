from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import RevisionHistory, Note, RevisionTask
from datetime import datetime, timedelta
from typing import List, Dict
import json
from app.models.revision_notification_schemas import RevisionHistoryEntry
from app.core.logging import app_logger
from fastapi import HTTPException, status

class HistoryService:
    @staticmethod
    async def record_revision(
        db: AsyncSession,
        task_id: int,
        mastery_level: str,
        comments: str = None
    ) -> RevisionHistory:
        """记录一次复习历史"""
        # 获取任务信息
        task = await db.get(RevisionTask, task_id)
        if not task:
            raise ValueError("Task not found")
            
        # 创建历史记录
        history = RevisionHistory(
            note_id=task.note_id,
            task_id=task_id,
            mastery_level=mastery_level,
            comments=comments
        )
        
        # 更新笔记状态
        note = await db.get(Note, task.note_id)
        note.total_revisions += 1
        note.last_revision_date = datetime.utcnow()
        note.current_mastery_level = mastery_level
        
        db.add(history)
        await db.commit()
        return history
    
    @staticmethod
    async def get_note_statistics(
        db: AsyncSession,
        note_id: int
    ) -> Dict:
        """获取笔记的复习统计信息"""
        # 获取复习历史
        query = select(RevisionHistory).filter(
            RevisionHistory.note_id == note_id
        ).order_by(RevisionHistory.revision_date)
        
        result = await db.execute(query)
        history = result.scalars().all()
        
        # 统计掌握程度分布
        mastery_levels = {}
        revision_dates = []
        
        for entry in history:
            mastery_levels[entry.mastery_level] = mastery_levels.get(entry.mastery_level, 0) + 1
            revision_dates.append(entry.revision_date)
            
        return {
            "total_revisions": len(history),
            "mastery_levels": mastery_levels,
            "revision_dates": revision_dates,
            "last_revision": revision_dates[-1] if revision_dates else None
        } 
    
    @staticmethod
    async def get_note_history(db: AsyncSession, note_id: int) -> List[RevisionHistoryEntry]:
        """获取笔记的复习历史记录"""
        try:
            # 查询笔记的复习历史
            query = (
                select(RevisionHistory)
                .where(RevisionHistory.note_id == note_id)
                .order_by(RevisionHistory.revision_date.desc())
            )
            result = await db.execute(query)
            history = result.scalars().all()
            
            # 转换为响应模型
            return [
                RevisionHistoryEntry(
                    id=entry.id,
                    note_id=entry.note_id,
                    revision_date=entry.revision_date,
                    mastery_level=entry.mastery_level,
                    comments=entry.comments
                )
                for entry in history
            ]
            
        except Exception as e:
            app_logger.error(f"获取笔记复习历史失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取笔记复习历史失败: {str(e)}"
            )