"""
Agent client — bridges FastAPI async world and Strands synchronous agents.

Key design decisions:
1. run_supervisor() is synchronous (Strands blocks until done).  We run it
   in a thread executor via asyncio.to_thread so we never block the event
   loop.
2. Memory is read BEFORE calling the agent (to inject context) and written
   AFTER (to store the new turn and update LTM if needed).
3. LTM auto-update: if the user mentions a known scoped product name and no
   LTM product is stored yet, we persist it.  This is the "deliberate
   extraction" approach described in agent_memory.py.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import AsyncGenerator

from app.agents.supervisor import run_supervisor
from app.memory.agent_memory import memory_client
from app.schemas import AgentAnswer

# Products in scope for this capstone.  LTM is only set if the user's message
# references one of these — prevents random nouns from becoming the
# "scoped product".
_SCOPED_PRODUCTS = {"lisinopril", "metformin", "sertraline"}


def _detect_product(text: str) -> str | None:
    """Return the first scoped product mentioned in text, or None."""
    lower = text.lower()
    for product in _SCOPED_PRODUCTS:
        if product in lower:
            return product
    return None


async def invoke_agent(
    message: str,
    session_id: str | None = None,
    user_id: int | None = None,
) -> AsyncGenerator[str, None]:
    """
    Invoke the Supervisor agent and stream the response as SSE-compatible
    JSON chunks.

    Memory lifecycle:
      1. Build memory context (STM last-6 turns + LTM scoped product).
      2. Call run_supervisor in a thread executor (non-blocking).
      3. Store user turn in STM.
      4. Store assistant turn in STM.
      5. Optionally update LTM scoped product.

    Yields:
        JSON-encoded AgentAnswer or error dicts.
    """
    actor_id = str(user_id or "anonymous")
    sid = session_id or f"anon-{actor_id}"

    # 1. Build memory context
    memory_context = memory_client.build_memory_context(
        session_id=sid, actor_id=actor_id
    )

    # 2. Store user turn in STM before calling agent
    memory_client.store_turn(
        session_id=sid, actor_id=actor_id, role="user", content=message
    )

    # 3. Auto-update LTM if product not yet set and message references one
    if not memory_client.get_scoped_product(actor_id):
        detected = _detect_product(message)
        if detected:
            memory_client.remember_scoped_product(actor_id, detected)
            # Rebuild context with the newly set product
            memory_context = memory_client.build_memory_context(
                session_id=sid, actor_id=actor_id
            )

    try:
        # 4. Run synchronous Strands agent in thread pool to avoid blocking
        response: AgentAnswer = await asyncio.to_thread(
            run_supervisor,
            message,
            memory_context,
        )

        # 5. Store assistant turn in STM
        memory_client.store_turn(
            session_id=sid,
            actor_id=actor_id,
            role="assistant",
            content=response.text,
        )

        yield response.model_dump_json()

    except Exception as exc:
        error_response = AgentAnswer(
            text=f"An error occurred while processing your request: {exc}",
            citations=[],
            agent_used="ErrorHandler",
        )
        yield error_response.model_dump_json()


async def invoke_agent_sync(
    message: str,
    session_id: str | None = None,
    user_id: int | None = None,
) -> AgentAnswer:
    """
    Convenience wrapper that collects the full streamed response and returns
    a single AgentAnswer.  Used by the /intake structured-output path.
    """
    result_json = ""
    async for chunk in invoke_agent(message, session_id=session_id, user_id=user_id):
        result_json = chunk  # last chunk is the full response in our single-yield model
    if result_json:
        return AgentAnswer.model_validate_json(result_json)
    return AgentAnswer(text="No response", citations=[], agent_used="ErrorHandler")
