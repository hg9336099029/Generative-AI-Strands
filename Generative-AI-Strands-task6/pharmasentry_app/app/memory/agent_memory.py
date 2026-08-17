"""
AgentCore Memory wiring.

Two tiers, and WHY each fact lives where it does:

Short-term memory (STM) -- in-session turn history
  - Scope: one chat session.
  - What goes here: the raw back-and-forth turns so the Supervisor has
    conversational context ("what about metformin instead?" needs to know
    the prior product).
  - Lifetime: session-scoped — gone once the session ends, which is correct
    because a stray follow-up should not leak into a different user's or a
    different day's conversation.

Long-term memory (LTM) -- durable, cross-session, per-user facts
  - Scope: the user (actor_id), persists across sessions.
  - What goes here: one durable preference per user — their SCOPED PRODUCT
    OF INTEREST (e.g. "this user primarily asks about lisinopril").  That is
    a genuine long-lived preference; re-deriving it every session would be
    wasteful and would degrade the experience (users would have to keep
    re-specifying the product).
  - What does NOT go here: anything health-sensitive tied to the user's own
    body.  PharmaSentry answers product questions; it is not a personal health
    record.  Storing "user takes metformin for their own diabetes" would turn a
    stateless Q&A tool into an unintended EHR-adjacent system — out of scope.
  - Extraction: we use an explicit `remember_scoped_product` call instead of
    automatic extraction so the single durable fact is deliberate, not
    model-guessed.

STM vs LTM decision rule:
  STM  — volatile, per-session conversational turns.
  LTM  — durable, per-user product preference that transcends sessions.
"""
from __future__ import annotations

import os
from typing import Any


class MemoryClient:
    """
    Thin wrapper around bedrock_agentcore.memory so the rest of the app
    does not import the AgentCore SDK directly.

    Stub mode is active when AGENTCORE_MEMORY_ID is not set or
    PHARMASENTRY_LOCAL_STUB=true is set — in that case, everything is
    backed by an in-process dict so the backend runs without a
    provisioned Memory resource.
    """

    # AWS region — no .env needed; boto3 SSO handles auth.
    _AWS_REGION = "ap-south-1"

    def __init__(self) -> None:
        from app.config import settings
        self.memory_id: str = settings.agentcore_memory_id or os.environ.get("AGENTCORE_MEMORY_ID", "")
        self._local_stub: bool = settings.local_stub or not self.memory_id

        # In-process stores for stub mode
        self._local_stm_store: dict[str, list[dict]] = {}   # session_id → turns
        self._local_ltm_store: dict[str, dict[str, Any]] = {}  # actor_id → facts

        if not self._local_stub:
            try:
                from bedrock_agentcore.memory import MemoryClient as _SDK
                self._client = _SDK(
                    region_name=self._AWS_REGION
                )
            except ImportError:
                print(
                    "[MemoryClient] bedrock_agentcore not installed — "
                    "falling back to local-stub mode."
                )
                self._local_stub = True
                self._client = None
        else:
            self._client = None

    # ------------------------------------------------------------------
    # Short-term memory — per-session turn history
    # ------------------------------------------------------------------

    def store_turn(self, session_id: str, actor_id: str, role: str, content: str) -> None:
        """Append one turn (role='user'|'assistant') to STM for this session."""
        if self._local_stub:
            self._local_stm_store.setdefault(session_id, []).append(
                {"role": role, "content": content}
            )
            return
        try:
            self._client.create_event(
                memory_id=self.memory_id,
                session_id=session_id,
                actor_id=actor_id,
                messages=[{"role": role, "content": content}],
            )
        except Exception as exc:
            print(f"[MemoryClient.store_turn] AgentCore error (non-fatal): {exc}")

    def get_last_k_turns(
        self, session_id: str, actor_id: str, k: int = 10
    ) -> list[dict]:
        """Return the last k turns for this session as [{role, content}]."""
        if self._local_stub:
            turns = self._local_stm_store.get(session_id, [])
            return turns[-k:] if len(turns) > k else turns
        try:
            return self._client.get_last_k_turns(
                memory_id=self.memory_id,
                session_id=session_id,
                actor_id=actor_id,
                k=k,
            )
        except Exception as exc:
            print(f"[MemoryClient.get_last_k_turns] AgentCore error (non-fatal): {exc}")
            return []

    # ------------------------------------------------------------------
    # Long-term memory — durable per-user product preference
    # ------------------------------------------------------------------

    def remember_scoped_product(self, actor_id: str, product_name: str) -> None:
        """
        Persist the user's primary product of interest.
        STM fact: session-volatile.  LTM fact: cross-session durable.
        This is LTM because it should shape future sessions, not just the
        current one.
        """
        if self._local_stub:
            self._local_ltm_store.setdefault(actor_id, {})["scoped_product"] = product_name
            return
        try:
            self._client.create_event(
                memory_id=self.memory_id,
                session_id="ltm-facts",
                actor_id=actor_id,
                messages=[
                    {
                        "role": "assistant",
                        "content": f"User's primary product of interest: {product_name}",
                    }
                ],
            )
        except Exception as exc:
            print(f"[MemoryClient.remember_scoped_product] AgentCore error (non-fatal): {exc}")

    def get_scoped_product(self, actor_id: str) -> str | None:
        """
        Retrieve the user's primary product of interest from LTM.
        Returns None if not set.
        """
        if self._local_stub:
            return self._local_ltm_store.get(actor_id, {}).get("scoped_product")
        try:
            records = self._client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=f"/users/{actor_id}/facts",
                query="scoped product",
            )
            return records[0]["content"] if records else None
        except Exception as exc:
            print(f"[MemoryClient.get_scoped_product] AgentCore error (non-fatal): {exc}")
            return None

    def build_memory_context(self, session_id: str, actor_id: str) -> str:
        """
        Build a human-readable memory context string to inject into the
        Supervisor's system prompt for a given session + user.

        Returns an empty string if there is nothing to inject.
        """
        parts: list[str] = []

        # LTM: scoped product
        scoped_product = self.get_scoped_product(str(actor_id))
        if scoped_product:
            parts.append(
                f"LTM — User's primary product of interest: {scoped_product}. "
                "Prefer answers about this product unless the user specifies otherwise."
            )

        # STM: recent turns
        turns = self.get_last_k_turns(session_id=session_id, actor_id=str(actor_id), k=6)
        if turns:
            turn_lines = "\n".join(
                f"  [{t.get('role', 'unknown').upper()}]: {t.get('content', '')[:200]}"
                for t in turns
            )
            parts.append(f"STM — Recent conversation turns:\n{turn_lines}")

        return "\n\n".join(parts)


# Module-level singleton — shared across all requests in this process
memory_client = MemoryClient()