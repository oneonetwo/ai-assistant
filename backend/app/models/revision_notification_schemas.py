from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time

class RevisionSettingsUpdate(BaseModel):
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

class RevisionSettingsResponse(BaseModel):
    id: int
    reminder_enabled: bool
    reminder_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RevisionHistoryEntry(BaseModel):
    id: int
    note_id: int
    task_id: int
    mastery_level: str
    revision_date: datetime
    comments: Optional[str]
    
    class Config:
        from_attributes = True

class RevisionStatistics(BaseModel):
    total_revisions: int
    mastery_levels: dict
    revision_dates: List[datetime] 