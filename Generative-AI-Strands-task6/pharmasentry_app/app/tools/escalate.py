"""
Escalation tool — used by the Supervisor to hand off complex cases to a human.

Must be decorated with @tool so Strands can discover and call it.
"""
from __future__ import annotations

from typing import Optional

from strands import tool


@tool
def escalate_to_human(reason: str, case_id: Optional[str] = None) -> str:
    """
    Escalate this conversation to a human pharmacovigilance reviewer.

    Use this tool when:
    - The user reports a serious or unexpected adverse event
    - The question is outside the scope of available labelling or FAERS data
    - The user seems distressed or is asking for personal medical advice

    Args:
        reason: A brief explanation of why human review is needed.
        case_id: Optional case identifier to attach this escalation to.

    Returns:
        Confirmation message to relay to the user.
    """
    import logging
    logging.getLogger(__name__).warning(
        "ESCALATION triggered | reason=%s | case_id=%s", reason, case_id
    )
    return (
        f"Your question has been escalated to our human review team. "
        f"Reason: {reason}. A specialist will follow up shortly."
    )
