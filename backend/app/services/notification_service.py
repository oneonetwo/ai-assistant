from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import RevisionSettings, RevisionTask, Note
from datetime import datetime, timedelta
from app.core.logging import app_logger
import asyncio

class NotificationService:
    @staticmethod
    async def get_daily_summary(db: AsyncSession, date: datetime) -> dict:
        """获取每日复习任务摘要"""
        query = select(func.count(RevisionTask.id)).filter(
            func.date(RevisionTask.scheduled_date) == date.date(),
            RevisionTask.status == "pending"
        )
        result = await db.execute(query)
        task_count = result.scalar_one()
        
        return {
            "date": date.date().isoformat(),
            "total_tasks": task_count,
            "message": f"今天有{task_count}条笔记需要复习"
        }
    
    @staticmethod
    async def get_settings() -> RevisionSettings:
        """获取提醒设置"""
        async with AsyncSession() as db:
            result = await db.execute(select(RevisionSettings))
            settings = result.scalar_one_or_none()
            if not settings:
                settings = RevisionSettings()
                db.add(settings)
                await db.commit()
            return settings
    
    @staticmethod
    async def update_settings(
        db: AsyncSession,
        reminder_enabled: bool = None,
        reminder_time: str = None
    ) -> RevisionSettings:
        """更新提醒设置"""
        settings = await NotificationService.get_settings()
        
        if reminder_enabled is not None:
            settings.reminder_enabled = reminder_enabled
        if reminder_time is not None:
            settings.reminder_time = reminder_time
            
        await db.commit()
        return settings
    
    @staticmethod
    async def send_notification(message: str):
        """发送通知（示例实现）"""
        app_logger.info(f"Sending notification: {message}")
        # 这里可以集成实际的通知系统
        # 例如: 推送服务、邮件服务等 