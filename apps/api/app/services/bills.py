from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.user import User
from app.services.entitlements import assert_can_add_bill


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def advance_due(current: date, recurrence: str) -> date:
    if recurrence == "weekly":
        return current + timedelta(days=7)
    if recurrence == "yearly":
        return _add_months(current, 12)
    if recurrence == "once":
        return current
    return _add_months(current, 1)


async def list_bills(db: AsyncSession, user: User) -> list[Bill]:
    result = await db.execute(
        select(Bill).where(Bill.user_id == user.id, Bill.is_active.is_(True)).order_by(Bill.next_due)
    )
    return list(result.scalars().all())


async def create_bill(db: AsyncSession, user: User, data: dict) -> Bill:
    count = await db.scalar(
        select(func.count()).select_from(Bill).where(Bill.user_id == user.id, Bill.is_active.is_(True))
    )
    assert_can_add_bill(user, int(count or 0))
    bill = Bill(user_id=user.id, **data)
    db.add(bill)
    await db.flush()
    return bill


async def mark_paid(db: AsyncSession, user: User, bill_id: UUID) -> Bill:
    result = await db.execute(select(Bill).where(Bill.id == bill_id, Bill.user_id == user.id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise ValueError("bill_not_found")
    if bill.recurrence == "once":
        bill.is_active = False
    else:
        bill.next_due = advance_due(bill.next_due, bill.recurrence)
    bill.last_warned_at = None
    await db.flush()
    return bill
