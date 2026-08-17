"""
escalate_to_human is a Supervisor-only tool (not given to the specialists).
It doesn't take any clinical action itself -- it just writes a triage
record that the FastAPI /cases review queue picks up. The actual DB write
happens in the backend (backend/routers/chat.py listens for this tool call
in the agent's tool-use trace and persists it); this function returns a
structured payload the backend can act on.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from strands import tool


@tool
def escalate_to_human(reason: str, summary: str, urgency: str = "routine") -> dict[str, Any]:
    """
    Flag the current conversation for human review instead of answering
    directly. Use this for clinical-advice requests, ambiguous adverse-event
    reports, or anything outside the three specialists' scope.

    Args:
        reason: Short machine-readable reason code, e.g.
            "clinical_advice_request", "ambiguous_ae_report", "out_of_scope".
        summary: One or two sentence human-readable summary of why this
            needs review.
        urgency: One of "routine", "priority", "urgent". Use "urgent" only
            for language suggesting an acute medical emergency -- and still
            tell the user to contact emergency services directly, since this
            tool does not notify anyone in real time.

    Returns:
        dict with keys: escalation_id, reason, summary, urgency, created_at.
    """
    return {
        "escalation_id": str(uuid.uuid4()),
        "reason": reason,
        "summary": summary,
        "urgency": urgency,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }