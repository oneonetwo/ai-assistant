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
        revision_mode: str = "normal",
        time_spent: int = 0,
        comments: str = None
    ) -> RevisionHistory:
        """记录一次复习历史"""
        try:
            app_logger.info(f"开始记录复习历史 - 任务ID: {task_id}")
            
            # 获取任务信息
            task = await db.get(RevisionTask, task_id)
            app_logger.debug(f"获取到任务信息: {task}")
            
            if not task:
                app_logger.error(f"未找到任务: {task_id}")
                raise ValueError("Task not found")
            
            # 创建历史记录
            history = RevisionHistory(
                note_id=task.note_id,
                task_id=task_id,
                mastery_level=mastery_level,
                revision_mode=revision_mode,
                time_spent=time_spent,
                comments=comments,
                revision_date=datetime.utcnow()
            )
            
            # 更新笔记状态
            note = await db.get(Note, task.note_id)
            if note:
                app_logger.debug(f"更新笔记状态 - 笔记ID: {note.id}")
                note.total_revisions += 1
                note.last_revision_date = datetime.utcnow()
                note.current_mastery_level = mastery_level
            
            db.add(history)
            await db.commit()
            await db.refresh(history)
            
            app_logger.info(f"成功记录复习历史 - 历史ID: {history.id}")
            return history
            
        except Exception as e:
            app_logger.error(f"记录复习历史失败: {str(e)}", exc_info=True)
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"记录复习历史失败: {str(e)}"
            )
    
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
                    task_id=entry.task_id,
                    revision_date=entry.revision_date,
                    mastery_level=entry.mastery_level,
                    revision_mode=entry.revision_mode,
                    time_spent=entry.time_spent,
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