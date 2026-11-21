from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Plan, StarPayment, Subscription
from app.models.user import User


async def seed_plans(db: AsyncSession) -> None:
    existing = await db.scalar(select(Plan).where(Plan.code == "premium"))
    if existing:
        return
    db.add(
        Plan(
            code="free",
            name="Free",
            stars_price=0,
            duration_days=0,
            habit_limit=3,
            bill_limit=3,
            features="digest,3 habits,3 bills",
        )
    )
    db.add(
        Plan(
            code="premium",
            name="Premium",
            stars_price=150,
            duration_days=30,
            habit_limit=None,
            bill_limit=None,
            features="unlimited habits/bills,cycle insights,quiet controls,streak recovery",
        )
    )
    await db.flush()


async def activate_premium(db: AsyncSession, user: User, stars: int, payload: str, charge_id: str | None) -> None:
    plan = await db.scalar(select(Plan).where(Plan.code == "premium"))
    if not plan:
        await seed_plans(db)
        plan = await db.scalar(select(Plan).where(Plan.code == "premium"))
    assert plan is not None

    ends = datetime.now(timezone.utc) + timedelta(days=plan.duration_days)
    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if sub:
        sub.plan_id = plan.id
        sub.status = "active"
        sub.ends_at = ends
    else:
        db.add(
            Subscription(
                user_id=user.id,
                plan_id=plan.id,
                status="active",
                ends_at=ends,
            )
        )
    user.is_premium = True
    db.add(
        StarPayment(
            user_id=user.id,
            telegram_payment_charge_id=charge_id,
            stars_amount=stars,
            payload=payload,
            status="completed",
        )
    )
    await db.flush()


async def list_plans(db: AsyncSession) -> list[Plan]:
    await seed_plans(db)
    result = await db.execute(select(Plan).where(Plan.is_active.is_(True)).order_by(Plan.stars_price))
    return list(result.scalars().all())
