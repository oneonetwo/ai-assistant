from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

class StudyTimeStats(BaseModel):
    """学习时长统计"""
    total_hours: float = Field(..., description="总学习时长(小时)")
    daily_average: float = Field(..., description="日均学习时长(小时)")
    weekly_trend: List[Dict[str, Any]] = Field(..., description="每周学习趋势")
    peak_periods: List[Dict[str, Any]] = Field(..., description="学习高峰时段")

    class Config:
        json_schema_extra = {
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

class MasteryStats(BaseModel):
    """知识点掌握情况统计"""
    total_points: int
    mastered: int
    learning: int
    struggling: int
    mastery_rate: float
    category_distribution: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "total_points": 150,
                "mastered": 85,
                "learning": 45,
                "struggling": 20,
                "mastery_rate": 0.567,
                "category_distribution": {
                    "编程基础": 30,
                    "算法": 45,
                    "系统设计": 35
                }
            }
        }

class RevisionStats(BaseModel):
    """复习计划统计"""
    total_plans: int = Field(..., description="总计划数")
    active_plans: int = Field(..., description="活跃计划数")
    completion_rate: float = Field(..., description="完成率")
    overdue_tasks: int = Field(..., description="逾期任务数")
    upcoming_tasks: int = Field(..., description="待完成任务数")
    daily_completion_trend: List[Dict[str, Any]] = Field(..., description="每日完成趋势")

    class Config:
        json_schema_extra = {
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

class TagStats(BaseModel):
    """标签分布统计"""
    total_tags: int
    most_used: List[Dict[str, Any]]
    category_tags: Dict[str, List[str]]
    recent_tags: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
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

class OverallStatistics(BaseModel):
    """整体统计数据"""
    study_time: StudyTimeStats
    mastery: MasteryStats
    revision: RevisionStats
    tags: TagStats
    last_updated: datetime = Field(..., description="最后更新时间") 