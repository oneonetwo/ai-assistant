from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models import Handbook, Category, Note, Tag, NoteTag
from app.models.handbook_schemas import HandbookCreate, HandbookUpdate, CategoryCreate, NoteCreate, NoteUpdate
from app.core.logging import app_logger
from sqlalchemy.orm import joinedload
from datetime import datetime

class HandbookService:
    async def create_category(self, db: AsyncSession, category: CategoryCreate) -> Category:
        """创建分类"""
        db_category = Category(**category.model_dump())
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    async def get_categories(self, db: AsyncSession) -> List[Category]:
        """获取所有分类"""
        result = await db.execute(select(Category))
        return result.scalars().all()

    async def create_handbook(self, db: AsyncSession, handbook: HandbookCreate) -> Handbook:
        """创建手册"""
        db_handbook = Handbook(**handbook.model_dump())
        db.add(db_handbook)
        await db.commit()
        await db.refresh(db_handbook)
        return db_handbook

    async def get_handbooks(self, db: AsyncSession, category_id: Optional[int] = None) -> List[Handbook]:
        """获取手册列表"""
        query = select(Handbook)
        if category_id:
            query = query.where(Handbook.category_id == category_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def update_handbook(
        self, 
        db: AsyncSession, 
        handbook_id: int, 
        handbook_update: HandbookUpdate
    ) -> Optional[Handbook]:
        """更新手册"""
        db_handbook = await self.get_handbook(db, handbook_id)
        if not db_handbook:
            return None
            
        update_data = handbook_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_handbook, key, value)
            
        await db.commit()
        await db.refresh(db_handbook)
        return db_handbook

    async def delete_handbook(self, db: AsyncSession, handbook_id: int) -> bool:
        """删除手册"""
        db_handbook = await self.get_handbook(db, handbook_id)
        if not db_handbook:
            return False
            
        await db.delete(db_handbook)
        await db.commit()
        return True

    async def get_handbook(self, db: AsyncSession, handbook_id: int) -> Optional[Handbook]:
        """获取单个手册"""
        result = await db.execute(
            select(Handbook)
            .where(Handbook.id == handbook_id)
            .options(joinedload(Handbook.notes))
        )
        return result.scalar_one_or_none()

handbook_service = HandbookService() 