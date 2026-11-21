"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-11-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255)),
        sa.Column("first_name", sa.String(255)),
        sa.Column("last_name", sa.String(255)),
        sa.Column("locale", sa.String(8), nullable=False, server_default="en"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Tehran"),
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("onboarding_done", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("stars_price", sa.Integer(), server_default="0"),
        sa.Column("duration_days", sa.Integer(), server_default="30"),
        sa.Column("habit_limit", sa.Integer()),
        sa.Column("bill_limit", sa.Integer()),
        sa.Column("features", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("city", sa.String(128)),
        sa.Column("country", sa.String(128)),
        sa.Column("quiet_hours_start", sa.Time()),
        sa.Column("quiet_hours_end", sa.Time()),
        sa.Column("notify_streak_nudge", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notify_cycle", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notify_bills", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("notify_digest", sa.Boolean(), server_default=sa.text("true")),
    )

    op.create_table(
        "habits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("emoji", sa.String(16)),
        sa.Column("streak_current", sa.Integer(), server_default="0"),
        sa.Column("streak_best", sa.Integer(), server_default="0"),
        sa.Column("last_checkin_date", sa.Date()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_habits_user_id", "habits", ["user_id"])

    op.create_table(
        "habit_checkins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("habit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("habits.id", ondelete="CASCADE")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("habit_id", "checkin_date", name="uq_habit_checkin_date"),
    )

    op.create_table(
        "bills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2)),
        sa.Column("currency", sa.String(8), server_default="IRR"),
        sa.Column("next_due", sa.Date(), nullable=False),
        sa.Column("warn_days", sa.Integer(), server_default="3"),
        sa.Column("recurrence", sa.String(16), server_default="monthly"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("last_warned_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_bills_user_id", "bills", ["user_id"])

    op.create_table(
        "calendar_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("source", sa.String(32), server_default="manual"),
        sa.Column("source_id", postgresql.UUID(as_uuid=True)),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True)),
        sa.Column("all_day", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_calendar_events_user_id", "calendar_events", ["user_id"])

    op.create_table(
        "cycle_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("avg_cycle_days", sa.Integer(), server_default="28"),
        sa.Column("avg_period_days", sa.Integer(), server_default="5"),
        sa.Column("last_start", sa.Date()),
        sa.Column("reminders_enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("remind_days_before", sa.Integer(), server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "cycle_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cycle_profiles.id", ondelete="CASCADE")),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date()),
        sa.Column("notes", sa.Text()),
        sa.Column("flow", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "digest_prefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("hour", sa.Integer(), server_default="8"),
        sa.Column("minute", sa.Integer(), server_default="0"),
        sa.Column("city", sa.String(128)),
        sa.Column("latitude", sa.String(32)),
        sa.Column("longitude", sa.String(32)),
        sa.Column("news_topic", sa.String(64), server_default="technology"),
        sa.Column("price_symbols", postgresql.ARRAY(sa.String())),
        sa.Column("include_weather", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("include_calendar", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("include_prices", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("include_news", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("last_sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id")),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("starts_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("ends_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "star_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("telegram_payment_charge_id", sa.String(255), unique=True),
        sa.Column("provider_payment_charge_id", sa.String(255)),
        sa.Column("stars_amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(16), server_default="XTR"),
        sa.Column("payload", sa.String(255)),
        sa.Column("status", sa.String(32), server_default="completed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    for table in (
        "star_payments",
        "subscriptions",
        "digest_prefs",
        "cycle_logs",
        "cycle_profiles",
        "calendar_events",
        "bills",
        "habit_checkins",
        "habits",
        "user_profiles",
        "plans",
        "users",
    ):
        op.drop_table(table)
