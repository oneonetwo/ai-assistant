from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.image_service import image_service
from app.services.file_service import file_service
from app.models.schemas import ImageAnalysisResponse
from app.middleware.upload import require_file_type
from app.core.config import settings
from pathlib import Path

router = APIRouter(prefix="/image-analysis", tags=["image-analysis"])

@router.post("/analyze", response_model=ImageAnalysisResponse)
@require_file_type(*settings.ALLOWED_IMAGE_TYPES)
async def analyze_image(
    file: UploadFile = File(...),
    query: Optional[str] = None,
    extract_text: bool = Query(False, description="是否提取图片中的文字"),
    system_prompt: Optional[str] = None,
    session_id: str = Query(..., description="用户会话ID"),
    db: AsyncSession = Depends(get_db)
):
    """分析图片"""
    try:
        # 保存文件
        saved_file = await file_service.save_file(
            file=file,
            file_type="image",
            db=db,
            session_id=session_id
        )
        
        # 分析图片
        result = await image_service.analyze_image(
            db=db,
            file_id=saved_file.file_id,
            query=query,
            extract_text=extract_text,
            system_prompt=system_prompt
        )
        
        return ImageAnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-text", response_model=Dict[str, str])
@require_file_type(*settings.ALLOWED_IMAGE_TYPES)
async def extract_text_from_image(
    file: UploadFile = File(...),
    session_id: str = Query(..., description="用户会话ID"),
    db: AsyncSession = Depends(get_db)
):
    """从图片中提取文字"""
    try:
        # 保存文件
        saved_file = await file_service.save_file(
            file=file,
            file_type="image",
            db=db,
            session_id=session_id
        )
        
        # 获取文件路径
        file_path = Path(settings.UPLOAD_DIR) / saved_file.file_path
        
        # 提取文字
        extracted_text = await image_service.extract_text(file_path)
        
        return {"text": extracted_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 