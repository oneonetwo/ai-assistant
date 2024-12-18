from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import RevisionSettings, RevisionTask, Note
from datetime import datetime, timedelta
from app.core.logging import app_logger
import asyncio
from fastapi import HTTPException
from sqlalchemy.orm import joinedload

class NotificationService:
    @staticmethod
    async def get_daily_summary(db: AsyncSession, date: datetime) -> dict:
        """获取每日复习任务摘要"""
        try:
            # 获取今天的开始和结束时间
            today_start = datetime.combine(date.date(), datetime.min.time())
            today_end = datetime.combine(date.date(), datetime.max.time())
            
            # 查询今天的任务，并预加载笔记信息
            base_query = select(RevisionTask).filter(
                func.date(RevisionTask.scheduled_date) == date.date()
            ).options(
                joinedload(RevisionTask.note)  # 预加载关联的笔记信息
            )
            
            # 获取任务列表
            tasks_result = await db.execute(base_query)
            tasks = tasks_result.unique().scalars().all()
            
            # 统计任务数量
            task_count = len(tasks)
            
            # 构建任务详情列表，包含笔记信息
            task_details = []
            for task in tasks:
                if task.note:
                    # 截取内容的前200个字符
                    content_preview = task.note.content[:200] + "..." if task.note.content and len(task.note.content) > 200 else task.note.content
                    
                    task_detail = {
                        "task_id": task.id,
                        "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None,
                        "priority": task.priority,
                        "status": task.status,
                        "note": {
                            "id": task.note.id,
                            "title": task.note.title or "无标题",
                            "content": content_preview,
                            "status": "待复习",  # 可以根据实际状态设置
                            "priority": task.priority or "medium"
                        }
                    }
                else:
                    task_detail = {
                        "task_id": task.id,
                        "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None,
                        "priority": task.priority,
                        "status": task.status,
                        "note": {
                            "id": None,
                            "title": "未关联笔记",
                            "content": "",
                            "status": "未知",
                            "priority": "low"
                        }
                    }
                
                task_details.append(task_detail)
            
            return {
                "date": date.date().isoformat(),
                "total_tasks": task_count,
                "message": f"今天有 {task_count} 条笔记需要复习",
                "tasks": task_details,
                "has_tasks": task_count > 0
            }
            
        except Exception as e:
            app_logger.error(f"获取每日复习任务摘要失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取每日复习任务摘要失败: {str(e)}"
            )
    
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