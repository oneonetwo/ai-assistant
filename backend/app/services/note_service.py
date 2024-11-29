from typing import List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Note, Tag, NoteTag, NoteAttachment, File
from app.models.handbook_schemas import NoteCreate, NoteUpdate, AttachmentCreate
from app.core.logging import app_logger
from sqlalchemy.orm import joinedload
from app.services.file_service import file_service
import uuid
from pathlib import Path
import aiohttp
import aiofiles
from app.core.config import settings

class NoteService:
    async def create_note(self, db: AsyncSession, note: NoteCreate) -> Note:
        """创建笔记"""
        try:
            # 处理标签
            tags = []
            if note.tags:
                for tag_name in note.tags:
                    tag = await self._get_or_create_tag(db, tag_name)
                    tags.append(tag)

            # 处理附件
            attachments = []
            if note.attachments:
                for attachment in note.attachments:
                    file_record = await self._process_attachment(db, attachment)
                    if file_record:
                        attachments.append(file_record)

            # 创建笔记
            note_data = note.model_dump(exclude={'tags', 'attachments'})
            db_note = Note(**note_data)
            db_note.tags = tags
            
            # 添加笔记
            db.add(db_note)
            await db.commit()
            await db.refresh(db_note)

            # 创建笔记附件关联
            if attachments:
                for file in attachments:
                    note_attachment = NoteAttachment(
                        note_id=db_note.id,
                        file_id=file.file_id
                    )
                    db.add(note_attachment)
                
                await db.commit()

            return db_note

        except Exception as e:
            app_logger.error(f"创建笔记失败: {str(e)}")
            raise

    async def _process_attachment(
        self, 
        db: AsyncSession, 
        attachment: AttachmentCreate
    ) -> Optional[File]:
        """处理附件URL并保存到文件系统"""
        try:
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            original_name = attachment.file_name or Path(attachment.url).name
            
            # 下载文件
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status != 200:
                        app_logger.error(f"下载文件失败: {attachment.url}")
                        return None

                    # 确定文件类型
                    content_type = response.headers.get('content-type', 'application/octet-stream')
                    
                    # 构建保存路径
                    file_ext = Path(original_name).suffix or '.bin'
                    relative_path = Path("attachments") / str(uuid.uuid4())[:2] / f"{file_id}{file_ext}"
                    full_path = settings.UPLOAD_DIR / relative_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    # 保存文件
                    async with aiofiles.open(full_path, 'wb') as f:
                        await f.write(await response.read())

                    # 创建文件记录
                    file_record = File(
                        file_id=file_id,
                        original_name=original_name,
                        file_path=str(relative_path),
                        file_type="attachment",
                        mime_type=content_type,
                        file_size=full_path.stat().st_size,
                        user_session_id="system"  # 或其他默认值
                    )
                    
                    db.add(file_record)
                    await db.commit()
                    await db.refresh(file_record)
                    
                    return file_record

        except Exception as e:
            app_logger.error(f"处理附件失败: {str(e)}")
            return None

    async def get_notes(
        self, 
        db: AsyncSession, 
        handbook_id: Optional[int] = None,
        tag: Optional[str] = None
    ) -> List[Note]:
        """获取笔记列表"""
        query = select(Note).options(joinedload(Note.tags))
        
        if handbook_id:
            query = query.where(Note.handbook_id == handbook_id)
            
        if tag:
            query = query.join(Note.tags).where(Tag.name == tag)
            
        result = await db.execute(query)
        return result.scalars().unique().all()

    async def update_note(
        self, 
        db: AsyncSession, 
        note_id: int, 
        note_update: NoteUpdate
    ) -> Optional[Note]:
        """更新笔记"""
        db_note = await self.get_note(db, note_id)
        if not db_note:
            return None

        # 更新标签
        if note_update.tags is not None:
            new_tags = []
            for tag_name in note_update.tags:
                tag = await self._get_or_create_tag(db, tag_name)
                new_tags.append(tag)
            db_note.tags = new_tags

        # 更新其他字段
        update_data = note_update.model_dump(exclude={'tags'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_note, key, value)

        await db.commit()
        await db.refresh(db_note)
        return db_note

    async def delete_note(self, db: AsyncSession, note_id: int) -> bool:
        """删除笔记"""
        db_note = await self.get_note(db, note_id)
        if not db_note:
            return False
            
        await db.delete(db_note)
        await db.commit()
        return True

    async def get_note(self, db: AsyncSession, note_id: int) -> Optional[Note]:
        """获取单个笔记"""
        result = await db.execute(
            select(Note)
            .where(Note.id == note_id)
            .options(joinedload(Note.tags))
        )
        return result.scalar_one_or_none()

    async def _get_or_create_tag(self, db: AsyncSession, tag_name: str) -> Tag:
        """获取或创建标签"""
        result = await db.execute(select(Tag).where(Tag.name == tag_name))
        tag = result.scalar_one_or_none()
        
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
            
        return tag

    async def get_tags(self, db: AsyncSession) -> List[Tag]:
        """获取所有标签"""
        result = await db.execute(select(Tag))
        return result.scalars().all()

note_service = NoteService() 