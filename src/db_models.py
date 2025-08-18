"""SQLAlchemy database models."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Machine(Base):
    """Database model for SSH machine configurations."""
    
    __tablename__ = "machines"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    host = Column(String, nullable=False)
    port = Column(Integer, default=22)
    username = Column(String, nullable=False)
    password = Column(String, nullable=True)  # Encrypted
    private_key_path = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    sessions = relationship("ConversationSession", back_populates="machine")


class ConversationSession(Base):
    """Database model for conversation sessions."""
    
    __tablename__ = "conversation_sessions"
    
    id = Column(String, primary_key=True)
    machine_id = Column(String, ForeignKey("machines.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_activity = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    machine = relationship("Machine", back_populates="sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")


class ConversationMessage(Base):
    """Database model for conversation messages."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("conversation_sessions.id"), nullable=False)
    message_type = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    session = relationship("ConversationSession", back_populates="messages")


class CommandExecution(Base):
    """Database model for command execution history."""
    
    __tablename__ = "command_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("conversation_sessions.id"), nullable=False)
    machine_id = Column(String, ForeignKey("machines.id"), nullable=False)
    command = Column(Text, nullable=False)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    exit_code = Column(Integer, nullable=False)
    execution_time = Column(Integer, nullable=False)  # milliseconds
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    session = relationship("ConversationSession")
    machine = relationship("Machine")