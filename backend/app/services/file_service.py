from datetime import datetime
from pathlib import Path
import aiofiles
import magic
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logging import app_logger
from app.db.models import File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

class FileService:
    async def save_file(
        self,
        file: UploadFile,
        file_type: str,
        db: AsyncSession,
        session_id: str
    ) -> File:
        """保存上传的文件并创建数据库记录"""
        try:
            # 验证文件类型
            content_type = magic.from_buffer(await file.read(1024), mime=True)
            await file.seek(0)
            
            allowed_types = (settings.ALLOWED_DOCUMENT_TYPES 
                           if file_type == "document" 
                           else settings.ALLOWED_IMAGE_TYPES)
            
            if content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {content_type}"
                )
            
            # 生成存储路径
            today = datetime.now()
            relative_path = Path(file_type + "s") / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}"
            full_path = settings.UPLOAD_DIR / relative_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{file.filename}"
            file_path = full_path / safe_filename
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(8192):
                    await f.write(chunk)
            
            # 创建数据库记录
            db_file = File(
                file_id=file_id,
                original_name=file.filename,
                file_path=str(relative_path / safe_filename),
                file_type=file_type,
                mime_type=content_type,
                file_size=file_path.stat().st_size,
                user_session_id=session_id
            )
            
            db.add(db_file)
            await db.commit()
            await db.refresh(db_file)
            
            return db_file
            
        except Exception as e:
            app_logger.error(f"文件保存失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"文件保存失败: {str(e)}"
            )

    async def get_file_path(self, file_id: str, db: AsyncSession) -> Path:
        """获取文件的完整路径"""
        query = select(File).where(File.file_id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(
                status_code=404,
                detail=f"文件不存在: {file_id}"
            )
            
        return settings.UPLOAD_DIR / file_record.file_path

    async def get_files_by_batch(
        self,
        db: AsyncSession,
        ids: Optional[List[int]] = None,
        file_ids: Optional[List[str]] = None
    ) -> List[File]:
        """批量查询文件"""
        try:
            if not ids and not file_ids:
                raise ValueError("必须提供ids或file_ids中的至少一个参数")

            query = select(File)
            
            # 构建查询条件
            conditions = []
            if ids:
                conditions.append(File.id.in_(ids))
            if file_ids:
                conditions.append(File.file_id.in_(file_ids))
            
            # 组合条件
            if conditions:
                query = query.where(or_(*conditions))
            
            # 执行查询
            result = await db.execute(query)
            files = result.scalars().all()
            
            return files

        except Exception as e:
            app_logger.error(f"批量查询文件失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"批量查询文件失败: {str(e)}"
            )

# 创建全局文件服务实例
file_service = FileService() 