from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.calendar import CalendarEvent
from app.models.user import User
from app.schemas.common import CalendarEventCreate, CalendarEventOut

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("", response_model=list[CalendarEventOut])
async def get_events(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CalendarEventOut]:
    stmt = select(CalendarEvent).where(CalendarEvent.user_id == user.id)
    if start:
        stmt = stmt.where(CalendarEvent.starts_at >= start)
    if end:
        stmt = stmt.where(CalendarEvent.starts_at <= end)
    stmt = stmt.order_by(CalendarEvent.starts_at)
    result = await db.execute(stmt)
    return [CalendarEventOut.model_validate(e) for e in result.scalars().all()]


@router.post("", response_model=CalendarEventOut)
async def post_event(
    body: CalendarEventCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CalendarEventOut:
    event = CalendarEvent(user_id=user.id, source="manual", **body.model_dump())
    db.add(event)
    await db.flush()
    return CalendarEventOut.model_validate(event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(CalendarEvent).where(
            and_(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id)
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    await db.flush()
    return {"ok": True}
