from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, JSON, Boolean
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
    # 添加与 File 的关系
    file = relationship("File", lazy="joined")

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

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Handbook(Base):
    __tablename__ = "handbooks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, default=1)  # 默认用户
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("Category", backref="handbooks")
    notes = relationship("Note", back_populates="handbook", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        nullable=False
    )

    # 关系定义
    notes_relation = relationship("Note", secondary="note_tags", back_populates="tags")

class NoteTag(Base):
    __tablename__ = "note_tags"
    
    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    message_ids = Column(JSON)  # 存储相关消息ID
    priority = Column(Integer, default=0)
    status = Column(String(50), default="draft")
    is_shared = Column(Boolean, default=False)
    handbook_id = Column(Integer, ForeignKey("handbooks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    handbook = relationship("Handbook", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes_relation", lazy="selectin")
    attachments = relationship("NoteAttachment", back_populates="note", lazy="selectin")

class NoteAttachment(Base):
    __tablename__ = "note_attachments"
    
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    file_id = Column(String, ForeignKey("files.file_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    note = relationship("Note", back_populates="attachments")
    file = relationship("File")