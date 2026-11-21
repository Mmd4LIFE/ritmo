from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.digest import DigestPrefs
from app.models.user import User, UserProfile


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    *,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    locale: str | None = None,
) -> User:
    result = await db.execute(
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(
            selectinload(User.profile),
            selectinload(User.digest_prefs),
            selectinload(User.cycle_profile),
            selectinload(User.subscription),
        )
    )
    user = result.scalar_one_or_none()
    settings = get_settings()
    if user:
        user.username = username or user.username
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        if locale:
            user.locale = locale
        await db.flush()
        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        locale=locale or "en",
    )
    db.add(user)
    await db.flush()
    db.add(UserProfile(user_id=user.id))
    db.add(
        DigestPrefs(
            user_id=user.id,
            hour=settings.digest_default_hour,
            minute=settings.digest_default_minute,
            price_symbols=["USD/IRR"],
        )
    )
    await db.flush()
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(
            selectinload(User.profile),
            selectinload(User.digest_prefs),
            selectinload(User.cycle_profile),
            selectinload(User.subscription),
        )
    )
    return result.scalar_one()
