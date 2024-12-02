from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.revision_schemas import (
    RevisionPlanCreate,
    RevisionPlanResponse,
    RevisionTaskUpdate,
    RevisionTaskResponse
)
from app.services.revision_service import RevisionService
from typing import List
from datetime import date, datetime

router = APIRouter(prefix="/revisions", tags=["revisions"])

@router.post("/plans", response_model=RevisionPlanResponse,
    summary="创建复习计划",
    description="""
    创建新的复习计划，支持以下功能：
    - 选择复习范围（手册、分类、标签）
    - 设置计划周期
    - 自动生成基于艾宾浩斯遗忘曲线的任务
    """,
    response_description="返回创建的复习计划详情"
)
async def create_revision_plan(
    plan: RevisionPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建复习计划
    
    - **plan**: 复习计划创建参数
        - name: 计划名称
        - start_date: 开始日期
        - end_date: 结束日期
        - handbook_ids: 手册ID列表
        - category_ids: 分类ID列表
        - tag_ids: 标签ID列表
        - note_statuses: 笔记状态列表
    """
    return await RevisionService.create_plan(db, plan)

@router.get("/plans", response_model=List[RevisionPlanResponse],
    summary="获取复习计划列表",
    description="获取所有复习计划，支持按状态筛选"
)
async def get_revision_plans(
    status: str = Query(None, description="计划状态筛选 (active/completed/cancelled)"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取复习计划列表
    
    - **status**: 可选的状态筛选
    """
    return await RevisionService.get_plans(db, status)

@router.get("/plans/{plan_id}", response_model=RevisionPlanResponse)
async def get_revision_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取特定复习计划详情"""
    plan = await RevisionService.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="复习计划不存在")
    return plan

@router.get("/plans/{plan_id}/tasks", response_model=List[RevisionTaskResponse],
    summary="获取计划任务列表",
    description="获取特定复习计划的任务列表，支持按日期和状态筛选"
)
async def get_plan_tasks(
    plan_id: int,
    date: date = Query(None, description="按日期筛选任务"),
    status: str = Query(None, description="按状态筛选 (pending/completed/skipped)"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取计划任务列表
    
    - **plan_id**: 计划ID
    - **date**: 可选的日期筛选
    - **status**: 可选的状态筛选
    """
    return await RevisionService.get_plan_tasks(db, plan_id, date, status)

@router.patch("/tasks/{task_id}", response_model=RevisionTaskResponse)
async def update_task_status(
    task_id: int,
    update: RevisionTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务状态和掌握程度"""
    task = await RevisionService.update_task(db, task_id, update)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@router.get("/daily-tasks", response_model=List[RevisionTaskResponse])
async def get_daily_tasks(
    date: date = Query(default=None, description="指定日期，默认为今天"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务清单"""
    return await RevisionService.get_daily_tasks(db, date or datetime.now().date()) 