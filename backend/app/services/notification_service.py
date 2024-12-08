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
            
            app_logger.info(f"查询日期范围: {today_start} - {today_end}")
            
            # 修改查询条件，使用 date() 函数进行日期比较
            base_query = select(RevisionTask).filter(
                func.date(RevisionTask.scheduled_date) == date.date()
            ).options(
                joinedload(RevisionTask.note)  # 预加载关联的笔记信息
            )
            
            # 先获取任务列表
            tasks_result = await db.execute(base_query)
            tasks = tasks_result.unique().scalars().all()
            
            # 记录查询到的原始任务数据
            app_logger.info(f"查询到的任务数量: {len(tasks)}")
            for task in tasks:
                app_logger.info(f"任务ID: {task.id}, 计划日期: {task.scheduled_date}, 状态: {task.status}")
            
            # 统计任务数量
            task_count = len(tasks)
            
            # 构建任务详情列表
            task_details = []
            for task in tasks:
                note_info = {
                    "task_id": task.id,
                    "scheduled_date": task.scheduled_date,
                    "priority": task.priority,
                    "status": task.status
                }
                
                # 安全地获取笔记信息
                if task.note:
                    note_info.update({
                        "note_id": task.note.id,
                        "note_title": task.note.title or "无标题",
                        "note_content": task.note.content[:100] if task.note.content else ""  # 只取前100个字符
                    })
                else:
                    note_info.update({
                        "note_id": None,
                        "note_title": "未关联笔记",
                        "note_content": ""
                    })
                    
                task_details.append(note_info)
            
            response_data = {
                "date": date.date().isoformat(),
                "total_tasks": task_count,
                "message": f"今天有 {task_count} 条笔记需要复习",
                "tasks": task_details,
                "has_tasks": task_count > 0
            }
            
            # 记录返回的数据结构
            app_logger.info(f"返回的数据: {response_data}")
            
            return response_data
            
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
            # 获取当前设��
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