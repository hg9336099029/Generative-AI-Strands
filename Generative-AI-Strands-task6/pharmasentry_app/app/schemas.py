from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

#------------------User_model--------------------------------------#
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Userout(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

#-----------------------------------Token_model--------------------------------------#

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None


#-----------------------------------Case Models--------------------------------------#

class CaseSummaryOut(BaseModel):
    id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseDetailOut(BaseModel):
    id: str
    user_id: int
    narrative: str
    narrative_redacted: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    narrative: str


#-----------------------------------Chat Models--------------------------------------#

class ChatMessageSchema(BaseModel):
    id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    id: str
    user_id: int
    actor_id: int
    agentcore_session_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    message: str
    role: str = "assistant"


#-----------------------------------Agent Models--------------------------------------#

class Citation(BaseModel):
    """Citation source for agent responses"""
    title: str
    url: Optional[str] = None
    source: Optional[str] = None


class AgentAnswer(BaseModel):
    """Response from an agent"""
    text: str
    citations: List[Citation] = []
    agent_used: Optional[str] = None
    signal_present: Optional[bool] = None


class Tool(BaseModel):
    """Tool definition for agents"""
    name: str
    description: str
    parameters: Optional[dict] = None