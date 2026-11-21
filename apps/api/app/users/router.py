from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import create_access_token, get_current_user, validate_webapp_init_data
from app.core.config import get_settings
from app.core.database import get_db
from app.models.bill import Bill
from app.models.habit import Habit
from app.models.user import User, UserProfile
from app.schemas.common import (
    AuthRequest,
    AuthResponse,
    BillOut,
    HomeSummary,
    ProfileUpdate,
    UserOut,
)
from app.services.habits import today_in_tz
from app.services.users import get_or_create_user


router = APIRouter(prefix="/api", tags=["users"])


@router.post("/auth/telegram", response_model=AuthResponse)
async def auth_telegram(body: AuthRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    settings = get_settings()
    if settings.environment == "development" and body.init_data.startswith("dev:"):
        # Local Mini App testing without Telegram: initData = "dev:<telegram_id>"
        telegram_id = int(body.init_data.split(":", 1)[1])
        tg_user = {"id": telegram_id, "first_name": "Dev", "username": "dev"}
    else:
        validated = validate_webapp_init_data(body.init_data, settings.telegram_bot_token)
        tg_user = validated["user"]

    raw_lang = (tg_user.get("language_code") or "").lower()
    inferred_locale = "fa" if raw_lang.startswith("fa") else ("en" if raw_lang.startswith("en") else None)

    user = await get_or_create_user(
        db,
        telegram_id=int(tg_user["id"]),
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
        locale=inferred_locale,
    )
    token = create_access_token(str(user.id), user.telegram_id)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    if body.locale is not None:
        user.locale = body.locale
    if body.timezone is not None:
        user.timezone = body.timezone
    if body.onboarding_done is not None:
        user.onboarding_done = body.onboarding_done

    if user.profile is None:
        user.profile = UserProfile(user_id=user.id)
        db.add(user.profile)

    for field in (
        "city",
        "country",
        "quiet_hours_start",
        "quiet_hours_end",
        "notify_streak_nudge",
        "notify_cycle",
        "notify_bills",
        "notify_digest",
    ):
        value = getattr(body, field)
        if value is not None:
            setattr(user.profile, field, value)

    await db.flush()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/home", response_model=HomeSummary)
async def home(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> HomeSummary:
    habits = list(
        (
            await db.execute(select(Habit).where(Habit.user_id == user.id, Habit.is_active.is_(True)))
        ).scalars()
    )
    today = today_in_tz(user.timezone)
    checked = sum(1 for h in habits if h.last_checkin_date == today)
    streak_best = max((h.streak_best for h in habits), default=0)
    next_bill = (
        await db.execute(
            select(Bill)
            .where(Bill.user_id == user.id, Bill.is_active.is_(True), Bill.next_due >= date.today())
            .order_by(Bill.next_due)
            .limit(1)
        )
    ).scalar_one_or_none()
    return HomeSummary(
        habits_active=len(habits),
        habits_checked_today=checked,
        next_bill=BillOut.model_validate(next_bill) if next_bill else None,
        streak_best=streak_best,
        is_premium=user.is_premium,
        digest_enabled=bool(user.digest_prefs and user.digest_prefs.enabled),
    )
