from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import re

class MessageBase(BaseModel):
    content: str = Field(..., description="消息内容")
    role: str = Field(..., description="消息角色", pattern="^(user|assistant)$")
    parent_message_id: Optional[int] = Field(None, description="父消息ID")

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    parent_message_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    session_id: str = Field(..., description="会话ID")
    name: Optional[str] = Field(None, description="会话名称")

class ConversationCreate(BaseModel):
    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="会话ID，如果不提供则自动生成UUID"
    )
    name: Optional[str] = Field(None, description="会话名称")

    @field_validator('session_id')
    def validate_session_id(cls, v):
        """验证session_id格式"""
        if not v:  # 如果为空，生成新的UUID
            return str(uuid.uuid4())
        
        # 验证是否是有效的UUID格式
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            return str(uuid.uuid4())

class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

class ConversationUpdate(BaseModel):
    name: str = Field(..., description="新的会话名称", max_length=100)

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")

class ChatResponse(BaseModel):
    session_id: str = Field(..., description="会话ID")
    response: str = Field(..., description="AI回复") 

class DocumentAnalysisResponse(BaseModel):
    file_id: str
    original_name: str
    analysis: str

class MultiDocumentAnalysisResponse(BaseModel):
    individual_analyses: List[Dict[str, Any]]
    comparison_analysis: str

class AnalysisRecord(BaseModel):
    id: int
    file_id: str
    analysis_type: str
    result: str
    created_at: datetime

    class Config:
        from_attributes = True 

class ImageMetadata(BaseModel):
    format: str
    mode: str
    size: tuple[int, int]
    width: int
    height: int

class ImageAnalysisResponse(BaseModel):
    file_id: str
    original_name: str
    metadata: ImageMetadata
    analysis: str
    extracted_text: Optional[str] = None 