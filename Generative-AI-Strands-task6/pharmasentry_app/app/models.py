from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .database import Base


# create User orm model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    cases = relationship("TriageCase", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


# TriageCase model for case management
class TriageCase(Base):
    __tablename__ = "triage_cases"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    narrative = Column(Text, nullable=False)
    narrative_redacted = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="pending", nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="cases")


# ChatSession model for managing chat conversations
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    actor_id = Column(Integer, nullable=False)
    agentcore_session_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# ChatMessage model for storing chat messages
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")