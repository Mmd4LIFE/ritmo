from __future__ import annotations

from datetime import datetime, time

import pytz
from aiogram import Bot

from app.core.config import get_settings
from app.models.user import User


def in_quiet_hours(user: User) -> bool:
    profile = user.profile
    if not profile or not profile.quiet_hours_start or not profile.quiet_hours_end:
        return False
    try:
        tz = pytz.timezone(user.timezone)
    except Exception:
        tz = pytz.timezone("Asia/Tehran")
    now = datetime.now(tz).time()
    start: time = profile.quiet_hours_start
    end: time = profile.quiet_hours_end
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end


async def send_message(telegram_id: int, text: str, reply_markup=None) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return
    bot = Bot(token=settings.telegram_bot_token)
    try:
        await bot.send_message(telegram_id, text, reply_markup=reply_markup)
    finally:
        await bot.session.close()


async def send_if_allowed(user: User, text: str, *, kind: str = "generic", reply_markup=None) -> bool:
    profile = user.profile
    if kind == "digest" and profile and not profile.notify_digest:
        return False
    if kind == "bill" and profile and not profile.notify_bills:
        return False
    if kind == "streak" and profile and not profile.notify_streak_nudge:
        return False
    if kind == "cycle" and profile and not profile.notify_cycle:
        return False
    if in_quiet_hours(user) and kind != "digest":
        return False
    await send_message(user.telegram_id, text, reply_markup=reply_markup)
    return True
