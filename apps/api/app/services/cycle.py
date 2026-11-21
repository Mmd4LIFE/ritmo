from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cycle import CycleLog, CycleProfile
from app.models.user import User


def predicted_next(profile: CycleProfile) -> date | None:
    if not profile.last_start:
        return None
    return profile.last_start + timedelta(days=profile.avg_cycle_days)


async def get_or_create_profile(db: AsyncSession, user: User) -> CycleProfile:
    result = await db.execute(select(CycleProfile).where(CycleProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile:
        return profile
    profile = CycleProfile(user_id=user.id)
    db.add(profile)
    await db.flush()
    return profile


async def log_cycle(db: AsyncSession, user: User, data: dict) -> CycleLog:
    profile = await get_or_create_profile(db, user)
    log = CycleLog(user_id=user.id, profile_id=profile.id, **data)
    db.add(log)
    profile.last_start = data["start_date"]
    await db.flush()
    return log
