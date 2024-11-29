from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.models.handbook_schemas import (
    HandbookCreate, HandbookUpdate, HandbookResponse,
    CategoryCreate, CategoryResponse
)
from app.services.handbook_service import handbook_service
from app.core.logging import app_logger

router = APIRouter(prefix="/handbooks", tags=["handbooks"])

@router.post("/categories", response_model=CategoryResponse,
    summary="创建分类",
    description="创建一个新的手册分类",
    response_description="返回创建的分类信息")
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的手册分类
    
    - **name**: 分类名称
    """
    try:
        return await handbook_service.create_category(db, category)
    except Exception as e:
        app_logger.error(f"创建分类失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/categories", response_model=List[CategoryResponse],
    summary="获取分类列表",
    description="获取所有手册分类",
    response_description="返回分类列表")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    获取所有手册分类列表
    """
    try:
        return await handbook_service.get_categories(db)
    except Exception as e:
        app_logger.error(f"获取分类列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=HandbookResponse,
    summary="创建手册",
    description="创建一个新的知识手册",
    response_description="返回创建的手册信息")
async def create_handbook(
    handbook: HandbookCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新的知识手册
    
    - **name**: 手册名称
    - **category_id**: 分类ID
    """
    try:
        return await handbook_service.create_handbook(db, handbook)
    except Exception as e:
        app_logger.error(f"创建手册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("", response_model=List[HandbookResponse],
    summary="获取手册列表",
    description="获取知识手册列表，可以按分类筛选",
    response_description="返回手册列表")
async def get_handbooks(
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取手册列表
    
    - **category_id**: 可选的分类ID过滤器
    """
    try:
        return await handbook_service.get_handbooks(db, category_id)
    except Exception as e:
        app_logger.error(f"获取手册列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{handbook_id}", response_model=HandbookResponse,
    summary="获取手册详情",
    description="获取指定手册的详细信息",
    response_description="返回手册详情")
async def get_handbook(
    handbook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个手册的详细信息
    
    - **handbook_id**: 手册ID
    """
    handbook = await handbook_service.get_handbook(db, handbook_id)
    if not handbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="手册不存在"
        )
    return handbook

@router.patch("/{handbook_id}", response_model=HandbookResponse,
    summary="更新手册",
    description="更新指定手册的信息",
    response_description="返回更新后的手册信息")
async def update_handbook(
    handbook_id: int,
    handbook_update: HandbookUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新手册信息
    
    - **handbook_id**: 手册ID
    - **name**: 可选的新手册名称
    - **category_id**: 可选的新分类ID
    """
    try:
        handbook = await handbook_service.update_handbook(db, handbook_id, handbook_update)
        if not handbook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="手册不存在"
            )
        return handbook
    except Exception as e:
        app_logger.error(f"更新手册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{handbook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除手册",
    description="删除指定的手册",
    response_description="成功删除返回204")
async def delete_handbook(
    handbook_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定手册
    
    - **handbook_id**: 要删除的手册ID
    """
    try:
        success = await handbook_service.delete_handbook(db, handbook_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="手册不存在"
            )
    except Exception as e:
        app_logger.error(f"删除手册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 