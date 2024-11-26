from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from pathlib import Path
import shutil
import uuid
import os

router = APIRouter(prefix="/upload", tags=["upload"])

# 确保static目录存在
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)

@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """上传文件到static目录"""
    try:
        # 生成唯一文件名
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 构建保存路径
        file_path = STATIC_DIR / unique_filename
        
        # 保存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 生成访问URL
        file_url = f"/static/{unique_filename}"
        
        return {
            "url": file_url,
            "filename": file.filename,
            "saved_name": unique_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )

@router.post("/image")
async def upload_image(image: UploadFile = File(...)):
    """上传图片到static目录"""
    try:
        # 验证文件类型
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="只允许上传图片文件"
            )
        
        # 生成唯一文件名
        file_extension = Path(image.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 构建保存路径
        file_path = STATIC_DIR / unique_filename
        
        # 保存文件
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # 生成访问URL
        image_url = f"/static/{unique_filename}"
        
        return {
            "url": image_url,
            "filename": image.filename,
            "saved_name": unique_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"图片上传失败: {str(e)}"
        ) 