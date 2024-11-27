from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)  # 对话ID
    session_id = Column(String(64), unique=True, index=True)  # 会话ID
    name = Column(String(100), nullable=True)  # 新增name字段
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 添加与 Message 的关系
    messages = relationship("Message", back_populates="conversation", lazy="selectin")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    file_id = Column(String(36), ForeignKey("files.file_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 添加与 Conversation 的关系
    conversation = relationship("Conversation", back_populates="messages")
    parent_message = relationship("Message", remote_side=[id], backref="child_messages")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    original_name = Column(String)
    file_path = Column(String)
    file_type = Column(String)  # image/document
    mime_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    user_session_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), ForeignKey("files.file_id"))
    analysis_type = Column(String(50))  # document/image/text
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)