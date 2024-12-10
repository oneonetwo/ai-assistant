from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import Tag, Note, NoteTag, Message, File, NoteAttachment
from app.models.handbook_schemas import TagResponse, NoteCreate, NoteUpdate, AttachmentCreate
from app.core.logging import app_logger
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from app.models.schemas import MessageResponse
import uuid
from datetime import datetime

class NoteService:
    async def get_tags(self, db: AsyncSession) -> List[TagResponse]:
        """获取所有标签列表"""
        try:
            # 只选择必要的字段
            stmt = select(Tag.id, Tag.name, Tag.created_at).order_by(Tag.name)
            result = await db.execute(stmt)
            tags = result.all()
            
            if not tags:
                return []
                
            # 将查询结果转换为响应模型
            return [
                TagResponse(
                    id=tag.id,
                    name=tag.name,
                    created_at=tag.created_at,
                    updated_at=tag.created_at  # 如果没有 updated_at，使用 created_at
                ) for tag in tags
            ]
            
        except Exception as e:
            app_logger.error(f"获取标签列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取标签列表失败: {str(e)}"
            )

    async def create_note(self, db: AsyncSession, note_data: NoteCreate) -> Note:
        """创建笔记并处理附件"""
        try:
            # 创建笔记基本信息
            note = Note(
                title=note_data.title,
                content=note_data.content,
                handbook_id=note_data.handbook_id,
                priority=note_data.priority,
                status=note_data.status,
                is_shared=note_data.is_shared,
                message_ids=note_data.message_ids or []
            )
            
            db.add(note)
            await db.flush()  # 获取note.id
            
            # 处理附件
            if note_data.attachments:
                for attachment in note_data.attachments:
                    # 创建文件记录
                    file = File(
                        file_id=str(uuid.uuid4()),
                        original_name=attachment.original_name,
                        file_path=attachment.file_path,
                        file_type=attachment.file_type or "unknown",
                        mime_type=attachment.file_type or "application/octet-stream",
                        file_size=attachment.file_size,
                        created_at=datetime.utcnow()
                    )
                    db.add(file)
                    await db.flush()  # 获取file.file_id
                    
                    # 创建笔记-附件关联
                    note_attachment = NoteAttachment(
                        note_id=note.id,
                        file_id=file.file_id
                    )
                    db.add(note_attachment)
            
            # 处理标签
            if note_data.tags:
                for tag_name in note_data.tags:
                    tag = await self._get_or_create_tag(db, tag_name)
                    note.tags.append(tag)
            
            await db.commit()
            await db.refresh(note)
            
            return note
            
        except Exception as e:
            await db.rollback()
            app_logger.error(f"创建笔记失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建笔记失败: {str(e)}"
            )

    async def update_note(
        self, 
        db: AsyncSession, 
        note_id: int, 
        note_update: NoteUpdate
    ) -> Optional[Note]:
        """新笔记"""
        try:
            # 查询现有笔记
            stmt = select(Note).where(Note.id == note_id)
            result = await db.execute(stmt)
            note = result.scalar_one_or_none()
            
            if not note:
                return None
                
            # 更新笔记字段
            for key, value in note_update.model_dump(exclude_unset=True).items():
                setattr(note, key, value)
                
            await db.commit()
            await db.refresh(note)
            
            return note
            
        except Exception as e:
            await db.rollback()
            app_logger.error(f"更新笔记失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新笔记失败: {str(e)}"
            )

    async def delete_note(self, db: AsyncSession, note_id: int) -> bool:
        """删除笔记"""
        try:
            # 查询笔记
            stmt = select(Note).where(Note.id == note_id)
            result = await db.execute(stmt)
            note = result.scalar_one_or_none()
            
            if not note:
                return False
                
            await db.delete(note)
            await db.commit()
            
            return True
            
        except Exception as e:
            await db.rollback()
            app_logger.error(f"删除笔记失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除笔记失败: {str(e)}"
            )

    async def get_notes(
        self,
        db: AsyncSession,
        handbook_id: Optional[int] = None,
        tag_id: Optional[int] = None
    ) -> List[Note]:
        try:
            # 构建基础查询
            query = select(Note).options(
                joinedload(Note.tags),
                joinedload(Note.attachments)
            )

            # 添加过滤条件
            if handbook_id:
                query = query.filter(Note.handbook_id == handbook_id)
            if tag_id:
                query = query.join(NoteTag).filter(NoteTag.tag_id == tag_id)
            
            # 添加按时间倒序排序
            query = query.order_by(desc(Note.updated_at))

            # 执行查询
            result = await db.execute(query)
            notes = result.unique().scalars().all()
            return notes

        except Exception as e:
            app_logger.error(f"获取笔记列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_tag(self, db: AsyncSession, tag_name: str) -> Tag:
        """创建新标签"""
        try:
            # 检查标签是否已存在
            stmt = select(Tag).where(Tag.name == tag_name)
            result = await db.execute(stmt)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"标签 '{tag_name}' 已存在"
                )
                
            # 创建新标签
            new_tag = Tag(name=tag_name)
            db.add(new_tag)
            await db.commit()
            await db.refresh(new_tag)
            
            return new_tag
            
        except Exception as e:
            await db.rollback()
            app_logger.error(f"创建标签失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建标签失败: {str(e)}"
            )

    async def get_note(self, db: AsyncSession, note_id: int) -> Optional[Note]:
        """获取笔记详情"""
        try:
            # 查询笔记
            query = (
                select(Note)
                .options(
                    joinedload(Note.tags),
                    joinedload(Note.attachments)
                )
                .where(Note.id == note_id)
            )
            result = await db.execute(query)
            note = result.unique().scalar_one_or_none()
            
            if not note:
                return None
                
            # 如果有message_ids,查询对应的消息
            if note.message_ids:
                messages_query = (
                    select(Message)
                    .where(Message.id.in_(note.message_ids))
                )
                messages_result = await db.execute(messages_query)
                messages = messages_result.scalars().all()
                
                # 转换为MessageResponse对象
                note.messages = []
                for message in messages:
                    # 获取文件信息（如果存在）
                    file_info = None
                    if message.file:
                        file_info = {
                            'file_id': message.file.file_id,
                            'original_name': message.file.original_name,
                            'file_type': message.file.file_type,
                            'file_path': message.file.file_path,
                            'mime_type': message.file.mime_type,
                            'file_size': message.file.file_size
                        }
                    
                    # 创建消息响应对象
                    message_response = MessageResponse.from_db_model(
                        message,
                        file_info=file_info
                    )
                    note.messages.append(message_response)
            else:
                note.messages = []
                
            return note
            
        except Exception as e:
            app_logger.error(f"获取笔记详情失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取笔记详情失败: {str(e)}"
            )

# 创建服务实例
note_service = NoteService()