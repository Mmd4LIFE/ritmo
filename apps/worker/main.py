from __future__ import annotations

import asyncio
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.orm import selectinload


# Allow importing api package when worker shares the image or PYTHONPATH
API_ROOT = Path(__file__).resolve().parents[1] / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.bot.keyboards import bill_paid_keyboard, habit_checkin_keyboard  # noqa: E402
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.i18n.loader import t  # noqa: E402
from app.models.bill import Bill  # noqa: E402
from app.models.cycle import CycleProfile  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.cycle import predicted_next  # noqa: E402
from app.services.digest import compose_digest, users_due_for_digest  # noqa: E402
from app.services.habits import today_in_tz  # noqa: E402
from app.services.notify import send_if_allowed  # noqa: E402


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ritmo.worker")


async def job_daily_digest() -> None:
    async with AsyncSessionLocal() as db:
        users = await users_due_for_digest(db)
        for user in users:
            try:
                text = await compose_digest(db, user)
                sent = await send_if_allowed(user, text, kind="digest")
                if sent and user.digest_prefs:
                    user.digest_prefs.last_sent_at = datetime.now(timezone.utc)
            except Exception:
                logger.exception("digest failed for user %s", user.id)
        await db.commit()
    logger.info("digest job done (%s users)", len(users))


async def job_bill_warn() -> None:
    today = date.today()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Bill, User)
            .join(User, User.id == Bill.user_id)
            .where(Bill.is_active.is_(True))
            .options(selectinload(User.profile))
        )
        for bill, user in result.all():
            days = (bill.next_due - today).days
            if days < 0 or days > bill.warn_days:
                continue
            if bill.last_warned_at and bill.last_warned_at.date() == today:
                continue
            text = t(user.locale, "bill_warn", title=bill.title, days=days, due=str(bill.next_due))
            kb = bill_paid_keyboard(str(bill.id), bill.title)
            sent = await send_if_allowed(user, text, kind="bill", reply_markup=kb)
            if sent:
                bill.last_warned_at = datetime.now(timezone.utc)
        await db.commit()
    logger.info("bill warn job done")


async def job_streak_nudge() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(selectinload(User.profile), selectinload(User.habits))
        )
        users = list(result.scalars().unique().all())
        now_utc = datetime.now(timezone.utc)
        for user in users:
            try:
                tz = pytz.timezone(user.timezone)
            except Exception:
                tz = pytz.timezone("Asia/Tehran")
            local = now_utc.astimezone(tz)
            if local.hour != 20 or local.minute > 2:
                continue
            today = today_in_tz(user.timezone)
            pending = [h for h in user.habits if h.is_active and h.last_checkin_date != today]
            if not pending:
                continue
            text = t(user.locale, "streak_nudge", count=len(pending))
            kb = habit_checkin_keyboard(str(pending[0].id), pending[0].title)
            await send_if_allowed(user, text, kind="streak", reply_markup=kb)
        await db.commit()
    logger.info("streak nudge job done")


async def job_cycle_remind() -> None:
    today = date.today()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CycleProfile, User)
            .join(User, User.id == CycleProfile.user_id)
            .where(CycleProfile.reminders_enabled.is_(True))
            .options(selectinload(User.profile))
        )
        for profile, user in result.all():
            nxt = predicted_next(profile)
            if not nxt:
                continue
            days = (nxt - today).days
            if days != profile.remind_days_before:
                continue
            text = t(user.locale, "cycle_remind", date=str(nxt))
            await send_if_allowed(user, text, kind="cycle")
        await db.commit()
    logger.info("cycle remind job done")


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(job_daily_digest, "cron", minute="*")
    scheduler.add_job(job_bill_warn, "cron", hour="6", minute="0")
    scheduler.add_job(job_streak_nudge, "cron", minute="*")
    scheduler.add_job(job_cycle_remind, "cron", hour="9", minute="0")
    scheduler.start()
    logger.info("Ritmo worker started")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
