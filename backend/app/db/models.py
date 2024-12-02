from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)  # 对话ID
    session_id = Column(String(64), unique=True, index=True)  # 会话ID
    name = Column(String(100), nullable=True)  # 新增name字段
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 添加与 Message 的关系
    messages = relationship("Message", back_populates="conversation", lazy="selectin")

class Message(BaseModel):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    parent_message_id = Column(Integer, ForeignKey("messages.id"))
    file_id = Column(String(64), ForeignKey("files.file_id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # 添加与 Conversation 的关系
    conversation = relationship("Conversation", back_populates="messages")
    parent_message = relationship("Message", remote_side=[id], backref="child_messages")
    # 添加与 File 的关系
    file = relationship("File", lazy="joined")

class File(BaseModel):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), unique=True, index=True)
    original_name = Column(String(255), nullable=True)
    file_path = Column(String(512), nullable=True)
    file_type = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    user_session_id = Column(String(64), index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class AnalysisRecord(BaseModel):
    __tablename__ = "analysis_records"
    
    id = Column(Integer, primary_key=True)
    file_id = Column(String(64), ForeignKey("files.file_id"))
    analysis_type = Column(String(50), nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Handbook(Base):
    __tablename__ = "handbooks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    user_id = Column(Integer, default=1)  # 默认用户
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = relationship("Category", backref="handbooks")
    notes = relationship("Note", back_populates="handbook", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
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
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

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
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    total_revisions = Column(Integer, default=0)
    last_revision_date = Column(DateTime(timezone=True), nullable=True)
    current_mastery_level = Column(String(50), default="not_started")

    # 关系定义
    handbook = relationship("Handbook", back_populates="notes")
    tags = relationship("Tag", secondary="note_tags", back_populates="notes_relation", lazy="selectin")
    attachments = relationship("NoteAttachment", back_populates="note", lazy="selectin")
    revision_histories = relationship("RevisionHistory", back_populates="note")

class NoteAttachment(Base):
    __tablename__ = "note_attachments"
    
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    file_id = Column(String(36), ForeignKey("files.file_id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # 关系
    note = relationship("Note", back_populates="attachments")
    file = relationship("File")

class RevisionPlan(Base):
    __tablename__ = "revision_plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="active")  # active, completed, cancelled
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # JSON fields for storing IDs
    handbook_ids = Column(JSON, nullable=True)
    category_ids = Column(JSON, nullable=True)
    tag_ids = Column(JSON, nullable=True)
    note_statuses = Column(JSON, nullable=True)
    
    # 关系
    tasks = relationship("RevisionTask", back_populates="plan")

class RevisionTask(Base):
    __tablename__ = "revision_tasks"
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("revision_plans.id"))
    note_id = Column(Integer, ForeignKey("notes.id"))
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending")  # pending, completed, skipped
    mastery_level = Column(String(50), nullable=True)  # not_mastered, partially_mastered, fully_mastered
    revision_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    plan = relationship("RevisionPlan", back_populates="tasks")
    note = relationship("Note")
    histories = relationship("RevisionHistory", back_populates="task")

class RevisionSettings(Base):
    __tablename__ = "revision_settings"
    
    id = Column(Integer, primary_key=True)
    reminder_enabled = Column(Boolean, default=True)
    reminder_time = Column(String(5), default="08:00")  # 格式: "HH:MM"
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class RevisionHistory(Base):
    __tablename__ = "revision_histories"
    
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey("notes.id"))
    task_id = Column(Integer, ForeignKey("revision_tasks.id"))
    mastery_level = Column(String(20), nullable=False)
    revision_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    comments = Column(Text, nullable=True)
    
    # 关系
    note = relationship("Note")
    task = relationship("RevisionTask", back_populates="histories")