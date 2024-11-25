from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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
    
    id = Column(Integer, primary_key=True, index=True)  # 消息ID
    conversation_id = Column(Integer, ForeignKey("conversations.id"))  # 关联的对话ID
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    role = Column(String(20))  # 消息角色（user/assistant）
    content = Column(Text)  # 消息内容
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间 

    # 添加与 Conversation 的关系
    conversation = relationship("Conversation", back_populates="messages")
    parent_message = relationship("Message", remote_side=[id], backref="child_messages")