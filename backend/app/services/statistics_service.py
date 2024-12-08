from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, and_, select
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
            # 计算总学习时长
            total_query = select(func.sum(RevisionHistory.duration))
            total_hours = await db.scalar(total_query) or 0
            
            # 计算日均学习时长
            daily_avg = total_hours / days
            
            # 获取每周趋势
            weekly_trend = []
            # 实现周趋势统计逻辑
            
            # 获取高峰时段
            peak_periods = []
            # 实现高峰时段统计逻辑
            
            return StudyTimeStats(
                total_hours=total_hours,
                daily_average=daily_avg,
                weekly_trend=weekly_trend,
                peak_periods=peak_periods
            )
        except Exception as e:
            app_logger.error(f"获取学习时长统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_mastery_stats(db: AsyncSession) -> MasteryStats:
        """获取知识点掌握情况统计"""
        try:
            # 实现知识点掌握统计逻辑
            return MasteryStats(...)
        except Exception as e:
            app_logger.error(f"获取知识点掌握统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_revision_stats(db: AsyncSession) -> RevisionStats:
        """获取复习计划统计"""
        try:
            # 获取总计划数
            total_plans = await db.scalar(
                select(func.count(RevisionPlan.id))
            )
            
            # 获取活跃计划数
            active_plans = await db.scalar(
                select(func.count(RevisionPlan.id)).where(
                    RevisionPlan.status == "active"
                )
            )
            
            # 计算完成率等其他统计
            # ...
            
            return RevisionStats(...)
        except Exception as e:
            app_logger.error(f"获取复习计划统计失败: {str(e)}")
            raise

    @staticmethod
    async def get_tag_stats(db: AsyncSession) -> TagStats:
        """获取标签分布统计"""
        try:
            # 实现标签统计逻辑
            return TagStats(...)
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