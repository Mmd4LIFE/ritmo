from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

import pytz
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit, HabitCheckin
from app.models.user import User
from app.services.entitlements import assert_can_add_habit


def today_in_tz(tz_name: str) -> date:
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Asia/Tehran")
    return datetime.now(tz).date()


async def list_habits(db: AsyncSession, user: User) -> list[Habit]:
    result = await db.execute(
        select(Habit).where(Habit.user_id == user.id, Habit.is_active.is_(True)).order_by(Habit.created_at)
    )
    return list(result.scalars().all())


async def create_habit(db: AsyncSession, user: User, kind: str, title: str, emoji: str | None) -> Habit:
    count = await db.scalar(
        select(func.count()).select_from(Habit).where(Habit.user_id == user.id, Habit.is_active.is_(True))
    )
    assert_can_add_habit(user, int(count or 0))
    habit = Habit(user_id=user.id, kind=kind, title=title, emoji=emoji)
    db.add(habit)
    await db.flush()
    return habit


async def checkin_habit(db: AsyncSession, user: User, habit_id: UUID) -> tuple[Habit, bool]:
    result = await db.execute(select(Habit).where(Habit.id == habit_id, Habit.user_id == user.id))
    habit = result.scalar_one_or_none()
    if not habit:
        raise ValueError("habit_not_found")

    today = today_in_tz(user.timezone)
    if habit.last_checkin_date == today:
        return habit, False

    db.add(HabitCheckin(habit_id=habit.id, user_id=user.id, checkin_date=today))

    if habit.last_checkin_date == today - timedelta(days=1):
        habit.streak_current += 1
    else:
        habit.streak_current = 1
    habit.streak_best = max(habit.streak_best, habit.streak_current)
    habit.last_checkin_date = today
    await db.flush()
    return habit, True
