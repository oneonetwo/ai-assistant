from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, update
from app.db.models import RevisionPlan, RevisionTask, Note, RevisionHistory
from app.models.revision_schemas import (
    RevisionPlanCreate, RevisionTaskUpdate, 
    BatchTaskUpdate, TaskAdjustment, TaskHistoryResponse, RevisionTaskResponse
)
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException, status
from app.core.logging import app_logger
from app.services.history_service import HistoryService  # 确保导入

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
        status: Optional[str] = None,
        date: Optional[date] = None
    ) -> List[RevisionTask]:
        """获取计划的任务列表"""
        try:
            # 构建基础查询
            query = (
                select(RevisionTask)
                .options(joinedload(RevisionTask.note))  # 预加载笔记信息
                .where(RevisionTask.plan_id == plan_id)
            )

            # 分别添加过滤条件
            if status:
                query = query.where(RevisionTask.status == status)
            if date:
                query = query.where(func.date(RevisionTask.scheduled_date) == date)

            # 添加排序
            query = query.order_by(RevisionTask.scheduled_date)

            result = await db.execute(query)
            tasks = result.unique().scalars().all()

            # 设置默认值和补充信息
            for task in tasks:
                if task.status is None:
                    task.status = "pending"
                if task.mastery_level is None:
                    task.mastery_level = "not_mastered"
                if task.revision_mode is None:
                    task.revision_mode = "normal"
                if task.priority is None:
                    task.priority = 0

                # 获取复习次数
                history_count = await db.execute(
                    select(func.count(RevisionHistory.id))
                    .where(RevisionHistory.task_id == task.id)
                )
                task.revision_count = history_count.scalar() or 0

                # 确保笔记信息完整
                if task.note:
                    if task.note.status is None:
                        task.note.status = "active"
                    if task.note.priority is None:
                        task.note.priority = "normal"
                    if task.note.content is None:
                        task.note.content = ""
                    if task.note.title is None:
                        task.note.title = ""

            return tasks

        except Exception as e:
            app_logger.error(f"获取计划任务列表失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取计划任务列表失败: {str(e)}"
            )

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
        date: date,
        status: Optional[str] = None
    ) -> List[RevisionTask]:
        """获取指定日期的复习任务
        
        Args:
            db: 数据库会话
            date: 指定日期
            status: 任务状态筛选
        """
        try:
            # 构建基础查询
            query = select(RevisionTask).filter(
                func.date(RevisionTask.scheduled_date) == date
            )
            
            # 添加状态筛选
            if status:
                query = query.filter(RevisionTask.status == status)
            
            # 预加载笔记关系
            query = query.options(
                selectinload(RevisionTask.note)
            )
            
            # 执行查询
            result = await db.execute(query)
            tasks = result.scalars().all()
            
            return list(tasks)
            
        except Exception as e:
            app_logger.error(f"获取每日任务失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取每日任务失败: {str(e)}"
            )

    @staticmethod
    async def get_next_task(
        db: AsyncSession,
        plan_id: int,
        mode: str = "normal"
    ) -> Optional[RevisionTask]:
        """获取下一个待复习任务"""
        try:
            app_logger.info(f"获取下一个待复习任务: plan_id={plan_id}, mode={mode}")
            
            # 构建基础查询条件
            conditions = [
                RevisionTask.plan_id == plan_id,
                RevisionTask.status == "pending",
                RevisionTask.scheduled_date <= datetime.utcnow()
            ]
            
            # 只有在 normal 模式下才添加 revision_mode 的过滤条件
            if mode == "normal":
                conditions.append(RevisionTask.revision_mode == "normal")
            
            stmt = (
                select(RevisionTask)
                .options(joinedload(RevisionTask.note))
                .where(and_(*conditions))
                .order_by(
                    desc(RevisionTask.priority),
                    RevisionTask.scheduled_date
                )
                .limit(1)
            )
            
            result = await db.execute(stmt)
            task = result.unique().scalar_one_or_none()
            
            if task:
                # 设置默认值
                if task.status is None:
                    task.status = "pending"
                if task.mastery_level is None:
                    task.mastery_level = "not_mastered"
                if task.revision_mode is None:
                    task.revision_mode = "normal"
                if task.priority is None:
                    task.priority = 0
                    
                # 确保笔记信息完整
                if task.note:
                    if task.note.status is None:
                        task.note.status = "active"
                    if task.note.priority is None:
                        task.note.priority = "normal"
                    if task.note.content is None:
                        task.note.content = ""
                    if task.note.title is None:
                        task.note.title = ""
                    
                # 获取复习次数
                history_count = await db.execute(
                    select(func.count(RevisionHistory.id))
                    .where(RevisionHistory.task_id == task.id)
                )
                task.revision_count = history_count.scalar() or 0
                
                app_logger.info(f"找到下一个任务: {task.id}")
            else:
                app_logger.info(f"没有找到待复习的任务 (plan_id: {plan_id}, mode: {mode})")
                
            return task

        except Exception as e:
            app_logger.error(f"获取下一个任务失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"获取下一个任务失败: {str(e)}"
            )
    @staticmethod
    async def batch_update_tasks(
        db: AsyncSession,
        update_data: BatchTaskUpdate
    ) -> List[RevisionTaskResponse]:
        """批量更新任务状态"""
        try:
            app_logger.info(f"开始批量更新任务: {update_data.model_dump()}")
            updated_tasks = []
            
            for task_id in update_data.task_ids:
                app_logger.debug(f"更新任务 {task_id} 的状态")
                # 使用 joinedload 预加载关联的 note
                query = (
                    select(RevisionTask)
                    .options(joinedload(RevisionTask.note))
                    .where(RevisionTask.id == task_id)
                )
                result = await db.execute(query)
                task = result.unique().scalar_one_or_none()
                
                if task:
                    # 更新任务状态
                    if update_data.status:
                        task.status = update_data.status
                    if update_data.mastery_level:
                        task.mastery_level = update_data.mastery_level
                    if update_data.revision_mode:
                        task.revision_mode = update_data.revision_mode
                    if update_data.time_spent is not None:
                        task.time_spent = update_data.time_spent
                    
                    # 记录复习历史
                    if update_data.status == "completed":
                        app_logger.debug(f"为任务 {task_id} 记录复习历史")
                        await HistoryService.record_revision(
                            db=db,
                            task_id=task_id,
                            mastery_level=update_data.mastery_level,
                            revision_mode=update_data.revision_mode or "normal",
                            time_spent=update_data.time_spent or 0,
                            comments=update_data.comments
                        )
                    
                    # 刷新任务对象以获取最新状态
                    await db.refresh(task)
                    
                    # 转换为响应模型，包含所有必需字段
                    task_response = RevisionTaskResponse(
                        id=task.id,
                        note_id=task.note_id,
                        note=task.note,
                        plan_id=task.plan_id,  # 添加计划ID
                        status=task.status,
                        mastery_level=task.mastery_level,
                        revision_mode=task.revision_mode,
                        time_spent=task.time_spent,
                        scheduled_date=task.scheduled_date,  # 添加计划日期
                        created_at=task.created_at,
                        updated_at=task.updated_at
                    )
                    updated_tasks.append(task_response)
            
            await db.commit()
            app_logger.info(f"成功更新 {len(updated_tasks)} 个任务")
            
            return updated_tasks
            
        except Exception as e:
            app_logger.error(f"批量更新任务失败: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            app_logger.info(f"开始调整任务计划: {adjustment.model_dump()}")
            
            # 使用 joinedload 预加载关联的 note
            stmt = (
                select(RevisionTask)
                .options(joinedload(RevisionTask.note))
                .where(RevisionTask.id == adjustment.task_id)
            )
            result = await db.execute(stmt)
            task = result.unique().scalar_one_or_none()
            
            if not task:
                app_logger.error(f"任务不存在: {adjustment.task_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"任务 {adjustment.task_id} 不存在"
                )

            # 更新任务
            task.scheduled_date = adjustment.new_date
            if adjustment.priority is not None:
                task.priority = adjustment.priority
            if adjustment.comments:
                task.comments = adjustment.comments

            await db.commit()
            app_logger.info(f"成功调整任务 {task.id} 的计划")
            return task

        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"调整任务计划失败: {str(e)}")
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

    @staticmethod
    async def check_note_revision_plans(
        db: AsyncSession,
        handbook_id: int
    ) -> Dict[str, Any]:
        """检查手册是否有关联的复习计划"""
        try:
            # 修改查询逻辑,使用 handbook_ids 数组字段
            stmt = (
                select(RevisionPlan)
                .where(
                    # 检查 handbook_ids 数组是否包含指定的 handbook_id
                    RevisionPlan.handbook_ids.contains([handbook_id])
                )
                .options(joinedload(RevisionPlan.tasks))
            )
            result = await db.execute(stmt)
            plans = result.unique().scalars().all()
            
            return {
                "has_plan": bool(plans),
                "plans": [
                    {
                        "id": plan.id,
                        "name": plan.name,
                        "start_date": plan.start_date,
                        "end_date": plan.end_date,
                        "status": plan.status,
                        "created_at": plan.created_at,
                        "updated_at": plan.updated_at,
                        "task_count": len(plan.tasks) if plan.tasks else 0
                    }
                    for plan in plans
                ]
            }
        except Exception as e:
            app_logger.error(f"检查复习计划失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"检查复习计划失败: {str(e)}"
            )

    @staticmethod
    async def add_note_to_multiple_plans(
        db: AsyncSession,
        note_id: int,
        plan_ids: List[int],
        start_date: Optional[datetime] = None,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            # 首先检查笔记是否存在
            note_query = select(Note).where(Note.id == note_id)
            result = await db.execute(note_query)
            note = result.scalar_one_or_none()
            
            if not note:
                raise HTTPException(
                    status_code=404,
                    detail="笔记不存在"
                )
            
            # 查询该笔记在这些计划中已存在的任务
            existing_tasks_query = (
                select(RevisionTask)
                .options(joinedload(RevisionTask.note))  # 预加载笔记信息
                .where(
                    and_(
                        RevisionTask.note_id == note_id,
                        RevisionTask.plan_id.in_(plan_ids)
                    )
                )
            )
            result = await db.execute(existing_tasks_query)
            existing_tasks = result.unique().scalars().all()
            existing_plan_ids = {task.plan_id for task in existing_tasks}

            # 建任务
            created_tasks = []
            failed_plans = []
            
            for plan_id in plan_ids:
                if plan_id in existing_plan_ids:
                    failed_plans.append({
                        "plan_id": plan_id,
                        "reason": "笔记已存在于该计划中"
                    })
                    continue
                    
                # 检查计划是否存在
                plan_query = select(RevisionPlan).where(RevisionPlan.id == plan_id)
                result = await db.execute(plan_query)
                plan = result.scalar_one_or_none()
                
                if not plan:
                    failed_plans.append({
                        "plan_id": plan_id,
                        "reason": "计划不存在"
                    })
                    continue
                    
                task = RevisionTask(
                    plan_id=plan_id,
                    note_id=note_id,
                    scheduled_date=start_date or datetime.utcnow(),
                    status="pending",
                    priority=priority or 1,
                    revision_mode="normal",
                    mastery_level="not_mastered"
                )
                db.add(task)
                created_tasks.append(task)
                
            if created_tasks:
                await db.commit()
                
                # 重新查询创建的任务以获取完整信息
                created_task_ids = [task.id for task in created_tasks]
                tasks_query = (
                    select(RevisionTask)
                    .options(joinedload(RevisionTask.note))
                    .where(RevisionTask.id.in_(created_task_ids))
                )
                result = await db.execute(tasks_query)
                final_tasks = result.unique().scalars().all()
                
                # 设置任务的默认值
                for task in final_tasks:
                    if task.status is None:
                        task.status = "pending"
                    if task.mastery_level is None:
                        task.mastery_level = "not_mastered"
                    if task.revision_mode is None:
                        task.revision_mode = "normal"
                    if task.priority is None:
                        task.priority = 0
                    
                    # 确保笔记信息完整
                    if task.note:
                        if task.note.status is None:
                            task.note.status = "active"
                        if task.note.priority is None:
                            task.note.priority = "normal"
                        if task.note.content is None:
                            task.note.content = ""
                        if task.note.title is None:
                            task.note.title = ""
            
            return {
                "success": bool(created_tasks),
                "tasks": final_tasks if created_tasks else [],
                "failed_plans": failed_plans
            }

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            app_logger.error(f"添加笔记到多个复习计划失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"添加笔记到多个复习计划失败: {str(e)}"
            )