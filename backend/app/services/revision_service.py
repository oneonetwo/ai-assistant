from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models import RevisionPlan, RevisionTask, Note, RevisionHistory
from app.models.revision_schemas import RevisionPlanCreate, RevisionTaskUpdate
from datetime import datetime, timedelta, date
from typing import List, Optional
import json
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
        """更新复习任务状态"""
        try:
            # 查询任务
            stmt = select(RevisionTask).where(RevisionTask.id == task_id)
            result = await db.execute(stmt)
            task = result.scalar_one_or_none()
            
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