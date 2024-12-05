from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, update
from app.db.models import RevisionPlan, RevisionTask, Note, RevisionHistory
from app.models.revision_schemas import (
    RevisionPlanCreate, RevisionTaskUpdate, 
    BatchTaskUpdate, TaskAdjustment, TaskHistoryResponse
)
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

class RevisionService:
    @staticmethod
    async def create_plan(
        db: AsyncSession,
        plan_data: RevisionPlanCreate
    ) -> RevisionPlan:
        # 创建复习计划
        plan = RevisionPlan(
            name=plan_data.name,
            start_date=plan_data.start_date,
            end_date=plan_data.end_date,
            handbook_ids=plan_data.handbook_ids,
            category_ids=plan_data.category_ids,
            tag_ids=plan_data.tag_ids,
            note_statuses=plan_data.note_statuses
        )
        
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        
        # 生成复习任务
        await RevisionService._generate_tasks(db, plan)
        return plan

    @staticmethod
    async def _generate_tasks(db: AsyncSession, plan: RevisionPlan):
        # 查询符合条件的笔记
        query = select(Note)
        
        if plan.handbook_ids:
            query = query.filter(Note.handbook_id.in_(plan.handbook_ids))
            
        # ... 其他筛选条件
        
        result = await db.execute(query)
        notes = result.scalars().all()
        
        # 生成复习时间点
        revision_points = [1, 2, 4, 7, 15, 30]  # 艾宾浩斯遗忘曲线
        
        for note in notes:
            for days in revision_points:
                scheduled_date = plan.start_date + timedelta(days=days)
                if scheduled_date <= plan.end_date:
                    task = RevisionTask(
                        plan_id=plan.id,
                        note_id=note.id,
                        scheduled_date=scheduled_date
                    )
                    db.add(task)
        
        await db.commit() 

    @staticmethod
    async def get_plans(
        db: AsyncSession,
        status: Optional[str] = None
    ) -> List[RevisionPlan]:
        """获取复习计划列表"""
        query = select(RevisionPlan)
        if status:
            query = query.filter(RevisionPlan.status == status)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_plan(
        db: AsyncSession,
        plan_id: int
    ) -> Optional[RevisionPlan]:
        """获取特定复习计划"""
        result = await db.execute(
            select(RevisionPlan).filter(RevisionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_plan_tasks(
        db: AsyncSession,
        plan_id: int,
        date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[RevisionTask]:
        """获取计划的任务列表"""
        query = (
            select(RevisionTask)
            .options(joinedload(RevisionTask.note))
            .filter(RevisionTask.plan_id == plan_id)
        )
        
        if date:
            query = query.filter(func.date(RevisionTask.scheduled_date) == date)
        if status:
            query = query.filter(RevisionTask.status == status)
            
        result = await db.execute(query)
        return result.unique().scalars().all()

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        update_data: RevisionTaskUpdate
    ) -> RevisionTask:
        """更新习任务状态"""
        try:
            # 查询任务,同时加载关联的note
            stmt = (
                select(RevisionTask)
                .options(joinedload(RevisionTask.note))
                .where(RevisionTask.id == task_id)
            )
            result = await db.execute(stmt)
            task = result.unique().scalar_one_or_none()
            
            if not task:
                raise HTTPException(
                    status_code=404,
                    detail="复习任务不存在"
                )
            
            # 更新任务状态
            if update_data.mastery_level is not None:
                task.mastery_level = update_data.mastery_level
                task.completed_at = datetime.utcnow()
                
                # 创建历史记录
                history = RevisionHistory(
                    note_id=task.note_id,
                    task_id=task.id,
                    mastery_level=update_data.mastery_level,
                    revision_date=datetime.utcnow()
                )
                db.add(history)
            
            await db.commit()
            await db.refresh(task)
            return task
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"更新任务失败: {str(e)}"
            )

    @staticmethod
    async def _create_additional_task(
        db: AsyncSession,
        task: RevisionTask
    ):
        """为未掌握的内容创建额外的复习任务"""
        next_date = datetime.utcnow() + timedelta(days=2)  # 两天后复习
        new_task = RevisionTask(
            plan_id=task.plan_id,
            note_id=task.note_id,
            scheduled_date=next_date
        )
        db.add(new_task)
        await db.commit()

    @staticmethod
    async def get_daily_tasks(
        db: AsyncSession,
        date: date
    ) -> List[RevisionTask]:
        """获取指定日期的所有任务"""
        query = (
            select(RevisionTask)
            .filter(func.date(RevisionTask.scheduled_date) == date)
            .order_by(RevisionTask.scheduled_date)
        )
        result = await db.execute(query)
        return result.scalars().all()
    @staticmethod
    async def get_next_task(
        db: AsyncSession,
        plan_id: Optional[int] = None,
        mode: str = "normal"
    ) -> Optional[RevisionTask]:
        try:
            print(f"\n[DEBUG] Starting get_next_task with mode={mode}, plan_id={plan_id}")
            
            # 首先检查是否有匹配的任务
            check_query = (
                select(func.count())
                .select_from(RevisionTask)
                .filter(
                    and_(
                        RevisionTask.status == "pending",
                        RevisionTask.revision_mode == mode
                    )
                )
            )
            if plan_id:
                check_query = check_query.filter(RevisionTask.plan_id == plan_id)
            
            try:
                result = await db.execute(check_query)
                count = result.scalar()
                print(f"[DEBUG] Found {count} tasks with mode '{mode}'")
            except Exception as e:
                print(f"[ERROR] Failed to check existing tasks: {str(e)}")
                raise

            # 如果没有匹配的任务，将部分pending任务更新为请求的模式
            if count == 0:
                print(f"[DEBUG] Attempting to update tasks to mode '{mode}'")
                try:
                    # 先查找可更新的任务
                    pending_query = (
                        select(RevisionTask)
                        .filter(
                            and_(
                                RevisionTask.status == "pending",
                                or_(
                                    RevisionTask.revision_mode.is_(None),
                                    RevisionTask.revision_mode == "normal"
                                )
                            )
                        )
                    )
                    if plan_id:
                        pending_query = pending_query.filter(RevisionTask.plan_id == plan_id)
                    
                    pending_result = await db.execute(pending_query)
                    pending_tasks = pending_result.scalars().all()
                    print(f"[DEBUG] Found {len(pending_tasks)} pending tasks to update")

                    # 更新这些任务
                    if pending_tasks:
                        update_stmt = (
                            update(RevisionTask)
                            .where(RevisionTask.id.in_([t.id for t in pending_tasks]))
                            .values(revision_mode=mode)
                        )
                        await db.execute(update_stmt)
                        await db.commit()
                        print(f"[DEBUG] Successfully updated tasks to mode '{mode}'")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to update tasks: {str(e)}")
                    await db.rollback()
                    raise

            # 查询任务
            try:
                query = (
                    select(RevisionTask)
                    .options(joinedload(RevisionTask.note))
                    .filter(
                        and_(
                            RevisionTask.status == "pending",
                            RevisionTask.revision_mode == mode
                        )
                    )
                    .order_by(
                        RevisionTask.priority.desc(),
                        RevisionTask.scheduled_date
                    )
                )
                
                if plan_id:
                    query = query.filter(RevisionTask.plan_id == plan_id)

                print(f"[DEBUG] Executing final query")
                result = await db.execute(query)
                task = result.scalars().first()
                
                print(f"[DEBUG] Query completed. Task found: {task is not None}")
                if task:
                    print(f"[DEBUG] Task details:")
                    print(f"  - id: {task.id}")
                    print(f"  - scheduled_date: {task.scheduled_date}")
                    print(f"  - status: {task.status}")
                    print(f"  - revision_mode: {task.revision_mode}")
                
                if not task:
                    raise HTTPException(
                        status_code=404,
                        detail=f"没有待复习的任务 (mode: {mode})"
                    )
                    
                return task
                
            except Exception as e:
                print(f"[ERROR] Failed to query task: {str(e)}")
                raise
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected error in get_next_task: {str(e)}")
            print(f"[ERROR] Error type: {type(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"获取下一个任务失败: {str(e)}"
            )
    @staticmethod
    async def batch_update_tasks(
        db: AsyncSession,
        updates: BatchTaskUpdate
    ) -> List[RevisionTask]:
        """批量更新任务状态"""
        try:
            tasks = []
            for task_id in updates.task_ids:
                task = await db.get(RevisionTask, task_id)
                if not task:
                    continue
                
                # 更新任务状态
                task.status = updates.status
                if updates.mastery_level:
                    task.mastery_level = updates.mastery_level
                task.completed_at = datetime.utcnow()
                
                # 创建历史记录
                history = RevisionHistory(
                    note_id=task.note_id,
                    task_id=task.id,
                    mastery_level=updates.mastery_level or task.mastery_level,
                    revision_mode=updates.revision_mode,
                    time_spent=updates.time_spent,
                    comments=updates.comments
                )
                db.add(history)
                
                # 如果未完全掌握，创建后续任务
                if updates.mastery_level in ["not_mastered", "partially_mastered"]:
                    await RevisionService._create_followup_task(db, task)
                
                tasks.append(task)
            
            await db.commit()
            return tasks
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"批量更新任务失败: {str(e)}"
            )

    @staticmethod
    async def get_task_history(
        db: AsyncSession,
        note_id: Optional[int] = None,
        task_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TaskHistoryResponse]:
        """获取任务复习历史"""
        try:
            query = select(RevisionHistory)
            
            if note_id:
                query = query.filter(RevisionHistory.note_id == note_id)
            if task_id:
                query = query.filter(RevisionHistory.task_id == task_id)
            if start_date:
                query = query.filter(RevisionHistory.revision_date >= start_date)
            if end_date:
                query = query.filter(RevisionHistory.revision_date <= end_date)
                
            query = query.order_by(desc(RevisionHistory.revision_date))
            
            result = await db.execute(query)
            histories = result.scalars().all()
            
            return [TaskHistoryResponse.from_orm(h) for h in histories]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"获取任务历史失败: {str(e)}"
            )

    @staticmethod
    async def adjust_task_schedule(
        db: AsyncSession,
        adjustment: TaskAdjustment
    ) -> RevisionTask:
        """调整任务计划"""
        try:
            task = await db.get(RevisionTask, adjustment.task_id)
            if not task:
                raise HTTPException(
                    status_code=404,
                    detail="任务不存在"
                )
            
            task.scheduled_date = adjustment.new_date
            if adjustment.priority is not None:
                task.priority = adjustment.priority
                
            # 记录调整历史
            history = RevisionHistory(
                note_id=task.note_id,
                task_id=task.id,
                mastery_level=task.mastery_level,
                revision_mode="adjustment",
                comments=adjustment.comments
            )
            db.add(history)
            
            await db.commit()
            await db.refresh(task)
            return task
            
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"调整任务计划失败: {str(e)}"
            )

    @staticmethod
    async def _create_followup_task(
        db: AsyncSession,
        task: RevisionTask
    ) -> RevisionTask:
        """创建后续复习任务"""
        # 根据掌握程度调整下次复习时间
        if task.mastery_level == "not_mastered":
            next_date = datetime.utcnow() + timedelta(days=1)  # 第二天复习
            priority = 2
        else:  # partially_mastered
            next_date = datetime.utcnow() + timedelta(days=3)  # 三天后复习
            priority = 1
            
        new_task = RevisionTask(
            plan_id=task.plan_id,
            note_id=task.note_id,
            scheduled_date=next_date,
            priority=priority,
            revision_mode=task.revision_mode
        )
        db.add(new_task)
        return new_task