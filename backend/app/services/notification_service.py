from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import RevisionSettings, RevisionTask, Note
from datetime import datetime, timedelta
from app.core.logging import app_logger
import asyncio
from fastapi import HTTPException

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
    async def get_settings(db: AsyncSession):
        """获取复习提醒设置"""
        try:
            result = await db.execute(select(RevisionSettings))
            settings = result.scalar_one_or_none()
            
            if not settings:
                # 如果没有设置，创建默认设置
                settings = RevisionSettings(
                    reminder_enabled=True,
                    reminder_time="09:00"
                )
                db.add(settings)
                await db.commit()
                await db.refresh(settings)
                
            return settings
            
        except Exception as e:
            app_logger.error(f"获取复习提醒设置失败: {str(e)}")
            raise
    
    @staticmethod
    async def update_settings(
        db: AsyncSession,
        reminder_enabled: bool = None,
        reminder_time: str = None
    ) -> RevisionSettings:
        """更新提醒设置"""
        try:
            # 获取当前设置
            settings = await NotificationService.get_settings(db)
            
            # 更新设置
            if reminder_enabled is not None:
                settings.reminder_enabled = reminder_enabled
            if reminder_time is not None:
                settings.reminder_time = reminder_time
            
            await db.commit()
            await db.refresh(settings)
            return settings
            
        except Exception as e:
            app_logger.error(f"更新复习提醒设置失败: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"更新复习提醒设置失败: {str(e)}"
            )
    
    @staticmethod
    async def send_notification(message: str):
        """发送通知（示例实现）"""
        app_logger.info(f"Sending notification: {message}")
        # 这里可以集成实际的通知系统
        # 例如: 推送服务、邮件服务等 