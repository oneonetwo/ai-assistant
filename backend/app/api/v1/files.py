'''
Author: yangjingyuan yangjingyuan@pwrd.com
Date: 2024-12-10 18:47:42
LastEditors: yangjingyuan yangjingyuan@pwrd.com
LastEditTime: 2024-12-10 18:47:48
FilePath: \backend\app\api\v1\files.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.models.schemas import BatchFileQuery, FileDetailResponse
from app.services.file_service import file_service
from app.core.logging import app_logger

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/batch", 
    response_model=List[FileDetailResponse],
    summary="批量查询文件",
    description="""
    批量查询文件信息，支持通过id列表或file_id列表查询。
    
    - 可以提供ids或file_ids中的任意一个或两个都提供
    - 单次查询最多支持100个文件
    - 返回符合条件的所有文件信息
    """,
    responses={
        200: {
            "description": "成功返回文件列表",
            "content": {
                "application/json": {
                    "example": [{
                        "id": 1,
                        "file_id": "uuid-string",
                        "original_name": "example.pdf",
                        "file_path": "path/to/file",
                        "file_type": "pdf",
                        "mime_type": "application/pdf",
                        "file_size": 1024,
                        "created_at": "2024-03-10T10:00:00",
                        "updated_at": "2024-03-10T10:00:00"
                    }]
                }
            }
        },
        400: {
            "description": "请求参数错误"
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def get_files_batch(
    query: BatchFileQuery,
    db: AsyncSession = Depends(get_db)
) -> List[FileDetailResponse]:
    """批量查询文件"""
    try:
        if not query.ids and not query.file_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供ids或file_ids中的至少一个参数"
            )

        files = await file_service.get_files_by_batch(
            db=db,
            ids=query.ids,
            file_ids=query.file_ids
        )

        return [FileDetailResponse.from_orm(file) for file in files]

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"批量查询文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 