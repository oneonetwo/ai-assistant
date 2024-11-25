from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.document_service import document_service
from app.services.file_service import file_service
from app.models.schemas import (
    DocumentAnalysisResponse,
    MultiDocumentAnalysisResponse,
)
from app.middleware.upload import require_file_type
from app.core.config import settings

router = APIRouter(prefix="/document-analysis", tags=["document-analysis"])

@router.post("/analyze-file", response_model=DocumentAnalysisResponse)
@require_file_type(*settings.ALLOWED_DOCUMENT_TYPES)
async def analyze_file(
    file: UploadFile = File(...),
    query: Optional[str] = None,
    system_prompt: Optional[str] = None,
    session_id: str = Query(..., description="用户会话ID"),
    db: AsyncSession = Depends(get_db)
):
    """分析单个文件"""
    try:
        # 保存文件
        saved_file = await file_service.save_file(
            file=file,
            file_type="document",
            db=db,
            session_id=session_id
        )
        
        # 分析文档
        result = await document_service.analyze_document(
            db=db,
            file_id=saved_file.file_id,
            query=query,
            system_prompt=system_prompt
        )
        
        return DocumentAnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-multiple-files", response_model=MultiDocumentAnalysisResponse)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...),
    query: Optional[str] = None,
    system_prompt: Optional[str] = None,
    session_id: str = Query(..., description="用户会话ID"),
    db: AsyncSession = Depends(get_db)
):
    """分析多个文件"""
    try:
        file_ids = []
        for file in files:
            # 验证文件类型
            if not any(file.content_type == t for t in settings.ALLOWED_DOCUMENT_TYPES):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {file.content_type}"
                )
            
            # 保存文件
            saved_file = await file_service.save_file(
                file=file,
                file_type="document",
                db=db,
                session_id=session_id
            )
            file_ids.append(saved_file.file_id)
        
        # 分析文档
        result = await document_service.analyze_multiple_documents(
            db=db,
            file_ids=file_ids,
            query=query,
            system_prompt=system_prompt
        )
        
        return MultiDocumentAnalysisResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 