from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import CycleLogCreate, CycleProfileOut, CycleProfileUpdate
from app.services.cycle import get_or_create_profile, log_cycle, predicted_next

router = APIRouter(prefix="/api/cycle", tags=["cycle"])


@router.get("", response_model=CycleProfileOut)
async def get_cycle(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> CycleProfileOut:
    profile = await get_or_create_profile(db, user)
    out = CycleProfileOut.model_validate(profile)
    out.predicted_next = predicted_next(profile)
    return out


@router.patch("", response_model=CycleProfileOut)
async def patch_cycle(
    body: CycleProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CycleProfileOut:
    profile = await get_or_create_profile(db, user)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(profile, k, v)
    await db.flush()
    out = CycleProfileOut.model_validate(profile)
    out.predicted_next = predicted_next(profile)
    return out


@router.post("/log", response_model=CycleProfileOut)
async def post_log(
    body: CycleLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CycleProfileOut:
    await log_cycle(db, user, body.model_dump())
    profile = await get_or_create_profile(db, user)
    out = CycleProfileOut.model_validate(profile)
    out.predicted_next = predicted_next(profile)
    return out
