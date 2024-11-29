from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HandbookBase(BaseModel):
    name: str = Field(..., max_length=100)
    category_id: int

class HandbookCreate(HandbookBase):
    pass

class HandbookUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None

class HandbookResponse(HandbookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str = Field(..., max_length=50)

class TagCreate(TagBase):
    pass

class TagResponse(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class AttachmentCreate(BaseModel):
    url: str
    file_name: Optional[str] = None

class FileResponse(BaseModel):
    file_id: str
    original_name: str
    file_path: str
    file_type: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

class NoteBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: Optional[str] = None
    message_ids: Optional[List[int]] = None
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    status: Optional[str] = None
    is_shared: bool = False
    handbook_id: int

class NoteCreate(NoteBase):
    tags: Optional[List[str]] = None
    attachments: Optional[List[AttachmentCreate]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    message_ids: Optional[List[int]] = None
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    status: Optional[str] = None
    is_shared: Optional[bool] = None
    tags: Optional[List[str]] = None

class NoteResponse(NoteBase):
    id: int
    times: int
    tags: List[TagResponse]
    attachments: List[FileResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
 