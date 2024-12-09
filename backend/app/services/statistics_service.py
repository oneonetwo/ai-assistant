from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, select, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RevisionHistory, RevisionTask, Note, Tag, NoteTag
from app.models.statistics_schemas import (
    StudyTimeStats, MasteryStats, RevisionStats,
    TagStats, OverallStatistics
)
from app.core.logging import app_logger

class StatisticsService:
    @staticmethod
    async def get_study_time_stats(db: AsyncSession, days: int = 30) -> StudyTimeStats:
        """获取学习时长统计"""
        try:
            # 计算总学习时长（将秒转换为小时）
            total_query = select(func.sum(RevisionHistory.time_spent))
            total_seconds = await db.scalar(total_query) or 0
            total_hours = total_seconds / 3600  # 转换为小时
            
            # 计算日均学习时长
            daily_avg = total_hours / days if days > 0 else 0
            
            # 获取每周趋势
            weekly_trend_query = select(
                func.date(RevisionHistory.revision_date).label('date'),
                func.sum(RevisionHistory.time_spent).label('seconds')
            ).group_by(
                func.date(RevisionHistory.revision_date)
            ).order_by(
                func.date(RevisionHistory.revision_date).desc()
            ).limit(7)
            
            result = await db.execute(weekly_trend_query)
            weekly_trend = [
                {
                    "date": row.date.strftime("%Y-%m-%d"),
                    "hours": row.seconds / 3600
                }
                for row in result
            ]
            
            # 获取高峰时段
            peak_query = select(
                func.extract('hour', RevisionHistory.revision_date).label('hour'),
                func.sum(RevisionHistory.time_spent).label('seconds')
            ).group_by(
                func.extract('hour', RevisionHistory.revision_date)
            ).order_by(
                func.sum(RevisionHistory.time_spent).desc()
            ).limit(3)
            
            result = await db.execute(peak_query)
            peak_periods = [
                {
                    "period": f"{int(row.hour):02d}:00-{int(row.hour)+1:02d}:00",
                    "hours": row.seconds / 3600
                }
                for row in result
            ]
            
            return StudyTimeStats(
                total_hours=round(total_hours, 2),
                daily_average=round(daily_avg, 2),
                weekly_trend=weekly_trend,
                peak_periods=peak_periods
            )
            
        except Exception as e:
            app_logger.error(f"获取学习时长统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_mastery_stats(db: AsyncSession) -> MasteryStats:
        """获取知识点掌握统计"""
        try:
            # 获取知识点总数
            total_query = select(func.count(Note.id))
            total_points = await db.scalar(total_query) or 0
            
            # 使用 status 字段替代 mastery_level
            mastery_query = select(
                Note.status,
                func.count(Note.id)
            ).group_by(Note.status)
            
            result = await db.execute(mastery_query)
            status_counts = dict(result.fetchall())
            
            # 映射 status 到掌握程度
            mastered = status_counts.get('completed', 0)
            learning = status_counts.get('in_progress', 0)
            struggling = status_counts.get('pending', 0)
            
            mastery_rate = mastered / total_points if total_points > 0 else 0
            
            # 获取分类分布并转��键为字符串
            category_query = select(
                Note.handbook_id,
                func.count(Note.id)
            ).group_by(Note.handbook_id)
            
            result = await db.execute(category_query)
            category_distribution = {
                f"handbook_{str(handbook_id)}": count
                for handbook_id, count in result.fetchall() if handbook_id
            }
            
            return MasteryStats(
                total_points=total_points,
                mastered=mastered,
                learning=learning,
                struggling=struggling,
                mastery_rate=round(mastery_rate, 3),
                category_distribution=category_distribution
            )
            
        except Exception as e:
            app_logger.error(f"获取知识点掌握统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_revision_stats(db: AsyncSession) -> RevisionStats:
        """获取复习计划统计"""
        try:
            now = datetime.utcnow()
            
            # 获取任务总数和活跃任务数
            tasks_query = select(
                func.count(RevisionTask.id).label('total'),
                func.sum(case(
                    (RevisionTask.status == 'active', 1),
                    else_=0
                )).label('active')
            )
            result = await db.execute(tasks_query)
            task_stats = result.fetchone()
            total_plans = task_stats.total or 0
            active_plans = task_stats.active or 0
            
            # 获取任务完成率
            completed_query = select(
                func.count(RevisionTask.id)
            ).where(RevisionTask.status == 'completed')
            completed_tasks = await db.scalar(completed_query) or 0
            completion_rate = completed_tasks / total_plans if total_plans > 0 else 0
            
            # 获取逾期和待完成任务数 (使用 created_at 替代 due_date)
            overdue_query = select(func.count(RevisionTask.id)).where(
                and_(
                    RevisionTask.created_at < now - timedelta(days=7),  # 假设7天未完成视为逾期
                    RevisionTask.status != 'completed'
                )
            )
            upcoming_query = select(func.count(RevisionTask.id)).where(
                and_(
                    RevisionTask.created_at >= now - timedelta(days=7),
                    RevisionTask.status != 'completed'
                )
            )
            
            overdue_tasks = await db.scalar(overdue_query) or 0
            upcoming_tasks = await db.scalar(upcoming_query) or 0
            
            # 获取每日完成趋势
            trend_query = select(
                func.date(RevisionHistory.revision_date).label('date'),
                func.count(RevisionHistory.id).label('completed'),
                func.count(RevisionHistory.id).label('total')
            ).where(
                RevisionHistory.revision_date >= (now - timedelta(days=7))
            ).group_by(
                func.date(RevisionHistory.revision_date)
            ).order_by(
                desc('date')
            )
            
            result = await db.execute(trend_query)
            daily_completion_trend = [
                {
                    "date": row.date.strftime("%Y-%m-%d"),
                    "completed": row.completed,
                    "total": row.total
                }
                for row in result
            ]
            
            return RevisionStats(
                total_plans=total_plans,
                active_plans=active_plans,
                completion_rate=round(completion_rate, 3),
                overdue_tasks=overdue_tasks,
                upcoming_tasks=upcoming_tasks,
                daily_completion_trend=daily_completion_trend
            )
            
        except Exception as e:
            app_logger.error(f"获取复习计划统计失���: {str(e)}")
            raise

    @staticmethod
    async def get_tag_stats(db: AsyncSession) -> TagStats:
        """获取标签统计"""
        try:
            # 获取标签总数
            total_query = select(func.count(Tag.id))
            total_tags = await db.scalar(total_query) or 0
            
            # 获取使用最多的标签
            most_used_query = select(
                Tag.name,
                func.count(NoteTag.note_id).label('count')
            ).select_from(Tag).join(
                NoteTag, Tag.id == NoteTag.tag_id
            ).group_by(Tag.id, Tag.name).order_by(
                desc('count')
            ).limit(10)
            
            result = await db.execute(most_used_query)
            most_used = [
                {"tag": row.name, "count": row.count}
                for row in result
            ]
            
            # 使用 GROUP_CONCAT 替代 array_agg
            category_query = select(
                Note.handbook_id,
                func.group_concat(Tag.name).label('tags')
            ).select_from(Note).join(
                NoteTag, Note.id == NoteTag.note_id
            ).join(
                Tag, NoteTag.tag_id == Tag.id
            ).group_by(Note.handbook_id)
            
            result = await db.execute(category_query)
            category_tags = {
                f"handbook_{str(row.handbook_id)}": row.tags.split(',') if row.tags else []
                for row in result if row.handbook_id
            }
            
            # 获取最近使用的标签
            recent_query = select(
                Tag.name,
                func.max(NoteTag.created_at).label('last_used')
            ).select_from(Tag).join(
                NoteTag, Tag.id == NoteTag.tag_id
            ).group_by(Tag.id, Tag.name).order_by(
                desc('last_used')
            ).limit(5)
            
            result = await db.execute(recent_query)
            recent_tags = [
                {
                    "tag": row.name,
                    "last_used": row.last_used.isoformat() if row.last_used else None
                }
                for row in result
            ]
            
            return TagStats(
                total_tags=total_tags,
                most_used=most_used,
                category_tags=category_tags,
                recent_tags=recent_tags
            )
            
        except Exception as e:
            app_logger.error(f"获取标签统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_overall_statistics(db: AsyncSession) -> OverallStatistics:
        """获取整体统计数据"""
        try:
            study_time = await StatisticsService.get_study_time_stats(db)
            mastery = await StatisticsService.get_mastery_stats(db)
            revision = await StatisticsService.get_revision_stats(db)
            tags = await StatisticsService.get_tag_stats(db)
            
            return OverallStatistics(
                study_time=study_time,
                mastery=mastery,
                revision=revision,
                tags=tags,
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            app_logger.error(f"获取整体统计数据失败: {str(e)}")
            raise

# 创建服务实例
statistics_service = StatisticsService()