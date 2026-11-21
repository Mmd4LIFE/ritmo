from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import HabitCreate, HabitOut
from app.services.habits import checkin_habit, create_habit, list_habits, today_in_tz

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.get("", response_model=list[HabitOut])
async def get_habits(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[HabitOut]:
    habits = await list_habits(db, user)
    today = today_in_tz(user.timezone)
    out: list[HabitOut] = []
    for h in habits:
        item = HabitOut.model_validate(h)
        item.checked_today = h.last_checkin_date == today
        out.append(item)
    return out


@router.post("", response_model=HabitOut)
async def post_habit(
    body: HabitCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitOut:
    habit = await create_habit(db, user, body.kind, body.title, body.emoji)
    item = HabitOut.model_validate(habit)
    item.checked_today = False
    return item


@router.post("/{habit_id}/checkin", response_model=HabitOut)
async def post_checkin(
    habit_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitOut:
    try:
        habit, _ = await checkin_habit(db, user, habit_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Habit not found") from None
    item = HabitOut.model_validate(habit)
    item.checked_today = True
    return item


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    habits = await list_habits(db, user)
    habit = next((h for h in habits if h.id == habit_id), None)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit.is_active = False
    await db.flush()
    return {"ok": True}
