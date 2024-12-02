from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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
    status: Optional[str] = None
    mastery_level: Optional[str] = None

class RevisionTaskResponse(BaseModel):
    id: int
    plan_id: int
    note_id: int
    scheduled_date: datetime
    status: str
    mastery_level: Optional[str]
    revision_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    note: dict  # 包含笔记的基本信息
    
    class Config:
        from_attributes = True 