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
    TaskHistoryResponse,
    AddNoteToRevisionPlanRequest,
    RevisionPlanCheckResponse,
    AddNoteToRevisionPlansRequest,
    BatchAddNotesToPlanResponse
)
from app.services.revision_service import RevisionService
from app.core.logging import app_logger
from typing import List, Optional
from datetime import date, datetime
from fastapi.responses import JSONResponse
from app.db.models import Note

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
    status: str = Query(None, description="按状态筛选 (pending/completed/skipped)"),
    date: date = Query(None, description="按日期筛选任务"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取计划任务列表
    
    - **plan_id**: 计划ID
    - **status**: 可选的状态筛选
    - **date**: 可选的日期筛选
    """
    return await RevisionService.get_plan_tasks(
        db=db,
        plan_id=plan_id,
        status=status,
        date=date
    )

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

@router.get(
    "/daily-tasks", 
    response_model=List[RevisionTaskResponse],
    summary="获取每日复习任务列表",
    description="""
    获取指定日期的复习任务列表，支持以下功能：
    - 按日期查询任务（默认为今天）
    - 按状态筛选任务（pending/completed/skipped）
    - 返回包含完整笔记信息的任务列表
    
    示例请求：
    - GET /api/v1/revisions/daily-tasks
    - GET /api/v1/revisions/daily-tasks?date=2024-03-14
    - GET /api/v1/revisions/daily-tasks?status=pending
    - GET /api/v1/revisions/daily-tasks?date=2024-03-14&status=pending
    """,
    response_description="返回指定日期的复习任务列表，每个任务包含关联的笔记详细信息",
    responses={
        200: {
            "description": "成功获取任务列表",
            "content": {
                "application/json": {
                    "example": [{
                        "id": 1,
                        "scheduled_date": "2024-03-14T10:00:00",
                        "status": "pending",
                        "note": {
                            "id": 2,
                            "title": "新概念英语一册内容及应用场景",
                            "content": "标题: 新概念英语一册内容及应用场景...",
                            "status": "待复习",
                            "priority": "low"
                        }
                    }]
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取每日任务失败: 具体错误信息"
                    }
                }
            }
        }
    }
)
async def get_daily_tasks(
    date: date = Query(
        default=None, 
        description="指定日期，默认为今天",
        example="2024-03-14"
    ),
    status: str = Query(
        None, 
        description="按状态筛选 (pending/completed/skipped)",
        example="pending"
    ),
    db: AsyncSession = Depends(get_db)
):
    """获取每日任务列表
    
    Args:
        date: 指定日期，默认为今天
        status: 任务状态筛选 (pending/completed/skipped)
        db: 数据库会话
    """
    try:
        tasks = await RevisionService.get_daily_tasks(
            db, 
            date or datetime.now().date(),
            status=status
        )
        
        # 预加载笔记数据
        for task in tasks:
            if task.note_id:
                note = await db.get(Note, task.note_id)
                if note:
                    task.note = note
        
        return tasks
        
    except Exception as e:
        app_logger.error(f"获取每日任务失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取每日任务失败: {str(e)}"
        )

@router.get("/tasks/next", 
    response_model=Optional[RevisionTaskResponse],
    summary="获取下一个待复习任务",
    description="获取指定计划下一个待复习任务，如果没有任务则返回null"
)
async def get_next_task(
    plan_id: int = Query(..., description="复习计划ID"),
    mode: str = Query("normal", description="复习模式"),
    db: AsyncSession = Depends(get_db)
):
    """获取下一个待复习任务"""
    app_logger.debug(f"请求获取下一个任务: plan_id={plan_id}, mode={mode}")
    
    task = await RevisionService.get_next_task(db, plan_id, mode)
    
    # 如果没有任务，直��返回 None
    if task is None:
        app_logger.debug("没有找到待复习任务，返回null")
        return None
        
    app_logger.debug(f"找到待复习任务: {task.id}")
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
    """获每日任务统计"""
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

@router.get("/plans/check/{handbook_id}", 
    response_model=RevisionPlanCheckResponse,
    summary="检查手册复习计划",
    description="""
    检查指定手册是否有关联的复习计划。
    
    返回:
    - has_plan: 是否存在关联的复习计划
    - plans: 关联的复习计划列表
    """,
    responses={
        200: {
            "description": "成功返回复习计划信息",
            "content": {
                "application/json": {
                    "example": {
                        "has_plan": True,
                        "plans": [
                            {
                                "id": 1,
                                "name": "复习计划1",
                                "start_date": "2024-01-01T00:00:00",
                                "end_date": "2024-12-31T00:00:00",
                                "status": "active",
                                "task_count": 10
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "检查复习计划失败",
            "content": {
                "application/json": {
                    "example": {"detail": "检查复习计划失败: 具体错误信息"}
                }
            }
        }
    }
)
async def check_handbook_revision_plans(
    handbook_id: int = Path(..., description="手册ID"),
    db: AsyncSession = Depends(get_db)
):
    """检查手册是否有复习计划"""
    return await RevisionService.check_note_revision_plans(db, handbook_id)

@router.post("/plans/{plan_id}/notes",
    response_model=RevisionTaskResponse,
    summary="添加笔记到复习计划",
    description="将现有笔记添加到指定的复习计划中")
async def add_note_to_plan(
    plan_id: int,
    request: AddNoteToRevisionPlanRequest,
    db: AsyncSession = Depends(get_db)
):
    """添加笔记到复习计划"""
    return await RevisionService.add_note_to_revision_plan(
        db=db,
        note_id=request.note_id,
        plan_id=plan_id,
        start_date=request.start_date,
        priority=request.priority
    )

@router.post("/plans/notes/batch",
    response_model=BatchAddNotesToPlanResponse,
    summary="批量添加笔记到多个复习计划",
    description="将笔记添加到多个指定的复习计划中")
async def add_note_to_multiple_plans(
    request: AddNoteToRevisionPlansRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量添加笔记到多个复习计划"""
    return await RevisionService.add_note_to_multiple_plans(
        db=db,
        note_id=request.note_id,
        plan_ids=request.plan_ids,
        start_date=request.start_date,
        priority=request.priority
    ) 