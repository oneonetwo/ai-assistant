from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.statistics_schemas import (
    StudyTimeStats, MasteryStats, RevisionStats,
    TagStats, OverallStatistics
)
from app.services.statistics_service import statistics_service
from app.core.logging import app_logger

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/study-time", 
    response_model=StudyTimeStats,
    summary="获取学习时长统计",
    description="获取用户的学习时长统计数据，包括总时长、日均时长、周趋势和高峰时段",
    responses={
        200: {
            "description": "成功获取统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "total_hours": 127.5,
                        "daily_average": 4.25,
                        "weekly_trend": [
                            {"date": "2024-03-01", "hours": 5.5},
                            {"date": "2024-03-02", "hours": 4.2}
                        ],
                        "peak_periods": [
                            {"period": "09:00-11:00", "hours": 45.5},
                            {"period": "14:00-16:00", "hours": 38.2}
                        ]
                    }
                }
            }
        }
    }
)
async def get_study_time_stats(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """获取学习时长统计"""
    try:
        return await statistics_service.get_study_time_stats(db, days)
    except Exception as e:
        app_logger.error(f"获取学习时长统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mastery",
    response_model=MasteryStats,
    summary="获取知识点掌握统计",
    description="获取用户的知识点掌握情况统计，包括总数、已掌握数量、学习中数量等",
    responses={
        200: {
            "description": "成功获取统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "total_points": 150,
                        "mastered": 85,
                        "learning": 45,
                        "struggling": 20,
                        "mastery_rate": 0.567,
                        "category_distribution": {
                            "编程基础": 30,
                            "算法": 45,
                            "框架": 75
                        }
                    }
                }
            }
        }
    }
)
async def get_mastery_stats(db: AsyncSession = Depends(get_db)):
    """获取知识点掌握统计"""
    try:
        return await statistics_service.get_mastery_stats(db)
    except Exception as e:
        app_logger.error(f"获取知识点掌握统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revision",
    response_model=RevisionStats,
    summary="获取复习计划统计",
    description="获取用户的复习计划完成情况统计，包括总计划数、活跃计划数、完成率等",
    responses={
        200: {
            "description": "成功获取统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "total_plans": 25,
                        "active_plans": 12,
                        "completion_rate": 0.78,
                        "overdue_tasks": 5,
                        "upcoming_tasks": 15,
                        "daily_completion_trend": [
                            {"date": "2024-03-01", "completed": 8, "total": 10},
                            {"date": "2024-03-02", "completed": 7, "total": 8}
                        ]
                    }
                }
            }
        }
    }
)
async def get_revision_stats(db: AsyncSession = Depends(get_db)):
    """获取复习计划统计"""
    try:
        return await statistics_service.get_revision_stats(db)
    except Exception as e:
        app_logger.error(f"获取复习计划统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags",
    response_model=TagStats,
    summary="获取标签分布统计",
    description="获取用户的标签使用情况统计，包括总标签数、最常用标签、分类标签等",
    responses={
        200: {
            "description": "成功获取统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "total_tags": 85,
                        "most_used": [
                            {"tag": "Python", "count": 45},
                            {"tag": "FastAPI", "count": 32}
                        ],
                        "category_tags": {
                            "编程语言": ["Python", "JavaScript", "Go"],
                            "框架": ["FastAPI", "Django", "React"]
                        },
                        "recent_tags": [
                            {"tag": "FastAPI", "last_used": "2024-03-03T15:30:00"},
                            {"tag": "Python", "last_used": "2024-03-03T14:20:00"}
                        ]
                    }
                }
            }
        }
    }
)
async def get_tag_stats(db: AsyncSession = Depends(get_db)):
    """获取标签分布统计"""
    try:
        return await statistics_service.get_tag_stats(db)
    except Exception as e:
        app_logger.error(f"获取标签统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overall",
    response_model=OverallStatistics,
    summary="获取整体统计数据",
    description="获取用户的所有统计数据，包括学习时长、知识掌握、复习计划和标签分布等",
    responses={
        200: {
            "description": "成功获取统计数据",
            "content": {
                "application/json": {
                    "example": {
                        "study_time": {
                            "total_hours": 127.5,
                            "daily_average": 4.25,
                            "weekly_trend": [
                                {"date": "2024-03-01", "hours": 5.5}
                            ],
                            "peak_periods": [
                                {"period": "09:00-11:00", "hours": 45.5}
                            ]
                        },
                        "mastery": {
                            "total_points": 150,
                            "mastered": 85,
                            "learning": 45,
                            "struggling": 20,
                            "mastery_rate": 0.567,
                            "category_distribution": {
                                "编程基础": 30
                            }
                        },
                        "revision": {
                            "total_plans": 25,
                            "active_plans": 12,
                            "completion_rate": 0.78,
                            "overdue_tasks": 5,
                            "upcoming_tasks": 15,
                            "daily_completion_trend": [
                                {"date": "2024-03-01", "completed": 8, "total": 10}
                            ]
                        },
                        "tags": {
                            "total_tags": 85,
                            "most_used": [
                                {"tag": "Python", "count": 45}
                            ],
                            "category_tags": {
                                "编程语言": ["Python", "JavaScript"]
                            },
                            "recent_tags": [
                                {"tag": "FastAPI", "last_used": "2024-03-03T15:30:00"}
                            ]
                        },
                        "last_updated": "2024-03-03T16:00:00"
                    }
                }
            }
        }
    }
)
async def get_overall_statistics(db: AsyncSession = Depends(get_db)):
    """获取整体统计数据"""
    try:
        return await statistics_service.get_overall_statistics(db)
    except Exception as e:
        app_logger.error(f"获取整体统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
