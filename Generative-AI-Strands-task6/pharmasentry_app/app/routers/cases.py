from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import TriageCase, User
from app.Oauth2 import get_current_user
from app.schemas import CaseDetailOut, CaseSummaryOut

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseSummaryOut])
async def list_cases(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Demo-scope access control: users see their own submitted cases. A
    # real deployment would add a separate reviewer role with visibility
    # across all users' cases -- flagged here rather than silently assumed.
    result = await db.execute(
        select(TriageCase).where(TriageCase.user_id == user.id).order_by(TriageCase.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{case_id}", response_model=CaseDetailOut)
async def get_case(
    case_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TriageCase).where(TriageCase.id == case_id, TriageCase.user_id == user.id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case