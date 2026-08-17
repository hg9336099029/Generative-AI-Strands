"""
Intake router — non-conversational adverse-event narrative submission.

This is the structured-output path described in the capstone:
  1. User POSTs a free-text adverse-event narrative.
  2. PII is redacted.
  3. The redacted narrative is stored in the database as a TriageCase.
  4. The agent analyses it and returns a validated, structured Pydantic model
     (StructuredCase) so the caller gets machine-parseable output rather than
     free-form chat.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent_client import invoke_agent_sync
from app.database import get_db
from app.models import TriageCase, User
from app.Oauth2 import get_current_user
from app.pii_redaction import redact_narrative
from app.schemas import CaseCreate, CaseDetailOut
from app.utils import get_correlation_id

router = APIRouter(prefix="/intake", tags=["intake"])


# ---------------------------------------------------------------------------
# Structured output schema (the Pydantic model returned by /intake/submit)
# ---------------------------------------------------------------------------

class StructuredCase(BaseModel):
    """
    Validated structured representation of an adverse-event narrative.
    This is what the non-conversational intake path returns instead of chat text.
    """
    case_id: str
    product_suspected: Optional[str] = None
    reactions_reported: list[str] = []
    seriousness_indicators: list[str] = []
    narrative_summary: str
    requires_expedited_review: bool = False
    raw_agent_assessment: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/submit",
    response_model=StructuredCase,
    status_code=status.HTTP_201_CREATED,
)
async def submit_case(
    case: CaseCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    correlation_id: str = Depends(get_correlation_id),
):
    """
    Submit an adverse-event narrative for structured analysis.

    Pipeline:
    1. PII redaction (Presidio with regex fallback).
    2. Store the case (original + redacted) in the database.
    3. Ask the agent to extract a structured summary.
    4. Return a validated StructuredCase Pydantic model.
    """
    # 1. Redact PII
    redacted = redact_narrative(case.narrative)

    # 2. Persist case to DB
    new_case = TriageCase(
        user_id=user.id,
        narrative=case.narrative,
        narrative_redacted=redacted,
        status="pending",
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    # 3. Ask the agent to extract structure from the redacted narrative
    extraction_prompt = (
        "You are performing structured adverse-event case extraction. "
        "Analyse the following redacted narrative and return a JSON object "
        "with exactly these keys:\n"
        '  "product_suspected": string or null,\n'
        '  "reactions_reported": list of strings,\n'
        '  "seriousness_indicators": list of strings (e.g. hospitalisation, death),\n'
        '  "narrative_summary": one-sentence summary,\n'
        '  "requires_expedited_review": boolean\n\n'
        f"Narrative:\n{redacted}"
    )

    agent_response = await invoke_agent_sync(
        message=extraction_prompt,
        user_id=user.id,
    )
    raw_text = agent_response.text

    # 4. Parse agent JSON output — be lenient, agent may wrap in markdown
    structured: dict = {}
    try:
        # Strip markdown fences if present
        json_text = re.sub(r"```(?:json)?|```", "", raw_text).strip()
        # Find the first { ... } block
        match = re.search(r"\{.*\}", json_text, re.DOTALL)
        if match:
            structured = json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass  # Fall through to defaults

    # Update case status
    new_case.status = "structured"
    await db.commit()

    return StructuredCase(
        case_id=str(new_case.id),
        product_suspected=structured.get("product_suspected"),
        reactions_reported=structured.get("reactions_reported", []),
        seriousness_indicators=structured.get("seriousness_indicators", []),
        narrative_summary=structured.get("narrative_summary", redacted[:200]),
        requires_expedited_review=bool(structured.get("requires_expedited_review", False)),
        raw_agent_assessment=raw_text,
    )


@router.get("/cases", response_model=list[CaseDetailOut])
async def list_my_cases(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all submitted cases for the current user."""
    from sqlalchemy import select
    result = await db.execute(
        select(TriageCase)
        .where(TriageCase.user_id == user.id)
        .order_by(TriageCase.created_at.desc())
    )
    return result.scalars().all()