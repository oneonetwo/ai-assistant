from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import joinedload
from enum import Enum

class MasteryLevel(str, Enum):
    """掌握程度枚举"""
    NOT_MASTERED = "not_mastered"  # 未掌握
    PARTIALLY_MASTERED = "partially_mastered"  # 部分掌握
    MASTERED = "mastered"  # 完全掌握

class RevisionPlanCreate(BaseModel):
    name: str = Field(..., max_length=200)
    start_date: datetime
    end_date: datetime
    handbook_ids: Optional[List[int]] = []
    category_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []
    note_statuses: Optional[List[str]] = []

class RevisionPlanResponse(RevisionPlanCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RevisionTaskUpdate(BaseModel):
    """复习任务更新模型"""
    mastery_level: Optional[MasteryLevel] = Field(
        None,
        description="掌握程度: not_mastered(未掌握) / partially_mastered(部分掌握) / mastered(完全掌握)"
    )
    completed_at: Optional[datetime] = None

class NoteBasicInfo(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    
    class Config:
        from_attributes = True

class RevisionTaskResponse(BaseModel):
    """复习任务响应模型"""
    id: int
    note_id: int
    scheduled_date: datetime
    mastery_level: Optional[MasteryLevel] = Field(
        None,
        description="掌握程度: not_mastered(未掌握) / partially_mastered(部分掌握) / mastered(完全掌握)"
    )
    revision_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    note: Optional[NoteBasicInfo] = None
    
    class Config:
        from_attributes = True 