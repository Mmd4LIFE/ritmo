from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AuthRequest(BaseModel):
    init_data: str = Field(..., alias="initData")

    model_config = ConfigDict(populate_by_name=True)


class ProfileUpdate(BaseModel):
    locale: str | None = None
    timezone: str | None = None
    city: str | None = None
    country: str | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    notify_streak_nudge: bool | None = None
    notify_cycle: bool | None = None
    notify_bills: bool | None = None
    notify_digest: bool | None = None
    onboarding_done: bool | None = None


class ProfileOut(ORMModel):
    city: str | None = None
    country: str | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    notify_streak_nudge: bool
    notify_cycle: bool
    notify_bills: bool
    notify_digest: bool


class UserOut(ORMModel):
    id: UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    locale: str
    timezone: str
    is_premium: bool
    onboarding_done: bool
    profile: ProfileOut | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class HabitCreate(BaseModel):
    kind: str = "custom"
    title: str
    emoji: str | None = None


class HabitOut(ORMModel):
    id: UUID
    kind: str
    title: str
    emoji: str | None = None
    streak_current: int
    streak_best: int
    last_checkin_date: date | None = None
    is_active: bool
    checked_today: bool = False


class BillCreate(BaseModel):
    title: str
    amount: Decimal | None = None
    currency: str = "IRR"
    next_due: date
    warn_days: int = 3
    recurrence: str = "monthly"


class BillUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    next_due: date | None = None
    warn_days: int | None = None
    recurrence: str | None = None
    is_active: bool | None = None


class BillOut(ORMModel):
    id: UUID
    title: str
    amount: Decimal | None = None
    currency: str
    next_due: date
    warn_days: int
    recurrence: str
    is_active: bool


class CalendarEventCreate(BaseModel):
    title: str
    description: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    all_day: bool = False


class CalendarEventOut(ORMModel):
    id: UUID
    title: str
    description: str | None = None
    source: str
    starts_at: datetime
    ends_at: datetime | None = None
    all_day: bool


class CycleProfileUpdate(BaseModel):
    avg_cycle_days: int | None = None
    avg_period_days: int | None = None
    last_start: date | None = None
    reminders_enabled: bool | None = None
    remind_days_before: int | None = None


class CycleLogCreate(BaseModel):
    start_date: date
    end_date: date | None = None
    notes: str | None = None
    flow: str | None = None


class CycleProfileOut(ORMModel):
    id: UUID
    avg_cycle_days: int
    avg_period_days: int
    last_start: date | None = None
    reminders_enabled: bool
    remind_days_before: int
    predicted_next: date | None = None


class DigestPrefsUpdate(BaseModel):
    enabled: bool | None = None
    hour: int | None = None
    minute: int | None = None
    city: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    news_topic: str | None = None
    price_symbols: list[str] | None = None
    include_weather: bool | None = None
    include_calendar: bool | None = None
    include_prices: bool | None = None
    include_news: bool | None = None


class DigestPrefsOut(ORMModel):
    enabled: bool
    hour: int
    minute: int
    city: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    news_topic: str
    price_symbols: list[str] | None = None
    include_weather: bool
    include_calendar: bool
    include_prices: bool
    include_news: bool


class PlanOut(ORMModel):
    id: UUID
    code: str
    name: str
    stars_price: int
    duration_days: int
    habit_limit: int | None = None
    bill_limit: int | None = None


class HomeSummary(BaseModel):
    habits_active: int
    habits_checked_today: int
    next_bill: BillOut | None = None
    streak_best: int
    is_premium: bool
    digest_enabled: bool
