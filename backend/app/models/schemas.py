from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import re
import json

class MessageBase(BaseModel):
    content: str = Field(..., description="消息内容")
    role: str = Field(..., description="消息角色", pattern="^(user|assistant)$")
    parent_message_id: Optional[int] = Field(None, description="父消息ID")
    file_id: Optional[str] = Field(None, description="关联文件ID")

class MessageCreate(MessageBase):
    pass

class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"

class FileResponse(BaseModel):
    file_id: str
    original_name: str
    file_type: str
    file_path: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    file_id: Optional[str] = None
    file: Optional[FileResponse] = None
    created_at: Optional[str] = None

    @classmethod
    def from_db_model(cls, message: "Message", file_info: Optional[Dict] = None):
        return cls(
            id=message.id,
            role=message.role,
            content=message.content,
            file_id=message.file_id,
            file=FileResponse(**file_info) if file_info else None,
            created_at=message.created_at.isoformat() if message.created_at else None
        )

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
    message: str
    system_prompt: Optional[str] = None

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

class ImageChatRequest(BaseModel):
    """图片聊天请求模型"""
    message: str
    image: str  # base64编码的图片
    system_prompt: Optional[str] = None
    extract_text: Optional[bool] = False

class ImageChatResponse(BaseModel):
    """图片聊天响应模型"""
    analysis: str
    extracted_text: Optional[str] = None

class FileChatRequest(BaseModel):
    """带文件的聊天请求模型"""
    message: str
    file: str  # base64编码的文件
    file_name: str
    file_type: str  # image/document
    system_prompt: Optional[str] = None

class FileChatResponse(BaseModel):
    """带文件的聊天响应模型"""
    session_id: str
    response: str
    file_id: Optional[str] = None

class ImageAnalysisRequest(BaseModel):
    url: str
    query: Optional[str] = None
    extract_text: bool = False
    system_prompt: Optional[str] = None
    session_id: str

class DocumentAnalysisRequest(BaseModel):
    url: str
    query: Optional[str] = None
    system_prompt: Optional[str] = None
    session_id: str

class CategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class HandbookBase(BaseModel):
    title: str = Field(..., description="手册标题")
    content: str = Field(..., description="手册内容")
    category_id: int = Field(..., description="分类ID")

class HandbookCreate(HandbookBase):
    pass

class HandbookResponse(HandbookBase):
    id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True

class AudioChatRequest(BaseModel):
    message: str
    file: str
    file_name: str
    file_type: str
    system_prompt: Optional[str] = None

class AudioChatResponse(BaseModel):
    session_id: str
    response: str
    file_id: str

class BatchFileQuery(BaseModel):
    """批量查询文件请求模型"""
    ids: Optional[List[int]] = None
    file_ids: Optional[List[str]] = None

    @field_validator('ids', 'file_ids')
    def validate_query_params(cls, v):
        if v is not None and len(v) > 100:  # 限制单次查询数量
            raise ValueError("一次最多查询100个文件")
        return v

class FileDetailResponse(BaseModel):
    """文件详细信息响应模型"""
    id: int
    file_id: str
    original_name: str
    file_path: str
    file_type: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
