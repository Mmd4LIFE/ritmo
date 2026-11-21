from __future__ import annotations

from fastapi import HTTPException

from app.core.config import get_settings
from app.models.user import User


def habit_limit_for(user: User) -> int | None:
    if user.is_premium:
        return None
    return get_settings().free_habit_limit


def bill_limit_for(user: User) -> int | None:
    if user.is_premium:
        return None
    return get_settings().free_bill_limit


def assert_can_add_habit(user: User, current_count: int) -> None:
    limit = habit_limit_for(user)
    if limit is not None and current_count >= limit:
        raise HTTPException(status_code=402, detail="premium_required")


def assert_can_add_bill(user: User, current_count: int) -> None:
    limit = bill_limit_for(user)
    if limit is not None and current_count >= limit:
        raise HTTPException(status_code=402, detail="premium_required")
