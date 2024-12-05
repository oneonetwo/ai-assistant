from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.revision_schemas import (
    RevisionPlanCreate,
    RevisionPlanResponse,
    RevisionTaskUpdate,
    RevisionTaskResponse,
    BatchTaskUpdate,
    TaskAdjustment,
    TaskHistoryResponse
)
from app.services.revision_service import RevisionService
from typing import List, Optional
from datetime import date, datetime
from fastapi.responses import JSONResponse

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

@router.patch("/tasks/{task_id}", response_model=RevisionTaskResponse,
    summary="更新复习任务",
    description="更新复习任务的掌握程度等状态")
async def update_task(
    task_id: int,
    update_data: RevisionTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新复习任务状态
    
    - **task_id**: 任务ID
    - **mastery_level**: 掌握程度 (not_mastered/partially_mastered/mastered)
    """
    try:
        updated_task = await RevisionService.update_task(db, task_id, update_data)
        return updated_task
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新任务失败: {str(e)}"
        )

@router.get("/daily-tasks", response_model=List[RevisionTaskResponse])
async def get_daily_tasks(
    date: date = Query(default=None, description="指定日期，默认为今天"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务清单"""
    return await RevisionService.get_daily_tasks(db, date or datetime.now().date())

@router.get("/tasks/next",
    response_model=RevisionTaskResponse,
    summary="获取下一个待复习任务",
    description="""
    获取下一个待复习的任务，支持以下功能：
    - 可选择指定计划ID
    - 支持普通模式和快速复习模式
    - 按优先级和计划时间排序
    """)
async def get_next_task(
    plan_id: Optional[int] = Query(None, description="计划ID"),
    mode: str = Query("normal", description="复习模式: normal/quick"),
    db: AsyncSession = Depends(get_db)
):
    """获取下一个待复习任务"""
    task = await RevisionService.get_next_task(db, plan_id, mode)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="没有待复习的任务"
        )
    return task

@router.post("/tasks/batch",
    response_model=List[RevisionTaskResponse],
    summary="批量更新任务状态",
    description="""
    批量更新任务状态，支持：
    - 更新多个任务的状态
    - 记录掌握程度
    - 记录复习模式和时间
    """)
async def batch_update_tasks(
    updates: BatchTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """批量更新任务状态"""
    return await RevisionService.batch_update_tasks(db, updates)

@router.get("/tasks/{task_id}/history",
    response_model=List[TaskHistoryResponse],
    summary="获取任务复习历史",
    description="获取指定任务的所有复习历史记录")
async def get_task_history(
    task_id: int = Path(..., description="任务ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取任务复习历史"""
    return await RevisionService.get_task_history(db, task_id)

@router.post("/tasks/adjust",
    response_model=RevisionTaskResponse,
    summary="调整任务计划",
    description="""
    调整任务复习计划，支持：
    - 修改计划日期
    - 调整优先级
    - 添加调整说明
    """)
async def adjust_task_schedule(
    adjustment: TaskAdjustment,
    db: AsyncSession = Depends(get_db)
):
    """调整任务计划"""
    return await RevisionService.adjust_task_schedule(db, adjustment)

@router.get("/tasks/daily/summary",
    summary="获取每日任务统计",
    description="获取指定日期的任务统计信息")
async def get_daily_summary(
    date: Optional[date] = Query(None, description="指定日期，默认为今天"),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务统计"""
    target_date = date or datetime.now().date()
    tasks = await RevisionService.get_daily_tasks(db, target_date)
    
    # 统计信息
    summary = {
        "date": target_date.isoformat(),
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t.status == "completed"),
        "pending": sum(1 for t in tasks if t.status == "pending"),
        "skipped": sum(1 for t in tasks if t.status == "skipped"),
        "mastery_levels": {
            "mastered": sum(1 for t in tasks if t.mastery_level == "mastered"),
            "partially_mastered": sum(1 for t in tasks if t.mastery_level == "partially_mastered"),
            "not_mastered": sum(1 for t in tasks if t.mastery_level == "not_mastered")
        }
    }
    
    return JSONResponse(content=summary) 