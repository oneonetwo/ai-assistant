from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import joinedload
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

class NoteBasicInfo(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    
    class Config:
        from_attributes = True

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
    note: Optional[NoteBasicInfo] = None
    
    class Config:
        from_attributes = True 