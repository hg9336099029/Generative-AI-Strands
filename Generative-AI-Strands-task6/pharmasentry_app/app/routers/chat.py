"""
Chat router — SSE streaming chat endpoint with AgentCore Memory integration.
"""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.agent_client import invoke_agent
from app.database import async_session_maker, get_db
from app.models import ChatMessage, ChatSession, User
from app.Oauth2 import get_current_user
from app.schemas import ChatRequest
from app.utils import get_correlation_id

router = APIRouter(tags=["chat"], prefix="/api/v1")


async def _get_or_create_session(
    db: AsyncSession, user: User, session_id: str | None
) -> ChatSession:
    """Get an existing chat session or create a new one."""
    if session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user.id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    new_session = ChatSession(
        user_id=user.id,
        actor_id=user.id,
        agentcore_session_id=f"sess-{user.id}-{uuid.uuid4().hex[:8]}",
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.post("/chat")
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Chat endpoint that streams the agent response as Server-Sent Events.

    Memory is automatically read before and written after each turn:
      - STM (short-term): last 6 turns injected into the Supervisor's prompt.
      - LTM (long-term): user's scoped product of interest persisted across sessions.
    """
    session = await _get_or_create_session(db, user, body.session_id)

    # Persist user message to DB
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.commit()

    async def event_generator():
        response_text = ""
        try:
            async for chunk in invoke_agent(
                message=body.message,
                session_id=session.agentcore_session_id,
                user_id=user.id,
            ):
                yield {"data": chunk}
                # Accumulate for DB storage (last chunk is the full AgentAnswer JSON)
                response_text = chunk

            # Persist assistant message to DB
            async with async_session_maker() as save_session:
                # Extract plain text from AgentAnswer JSON if possible
                try:
                    answer_data = json.loads(response_text)
                    content = answer_data.get("text", response_text)
                except (json.JSONDecodeError, AttributeError):
                    content = response_text

                assistant_msg = ChatMessage(
                    session_id=session.id,
                    role="assistant",
                    content=content,
                )
                save_session.add(assistant_msg)
                await save_session.commit()

        except Exception as exc:
            error_payload = json.dumps({"type": "error", "message": str(exc)})
            yield {"data": error_payload}

    return EventSourceResponse(event_generator())


@router.get("/chat/sessions")
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all chat sessions for the current user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "session_id": s.id,
            "agentcore_session_id": s.agentcore_session_id,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sessions
    ]


@router.get("/chat/{session_id}")
async def get_session(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific chat session with all messages."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = messages_result.scalars().all()

    return {
        "session_id": session.id,
        "agentcore_session_id": session.agentcore_session_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
            }
            for msg in messages
        ],
    }