from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from app.core.config import get_settings
from app.i18n.loader import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="English", callback_data="lang:en"),
                InlineKeyboardButton(text="فارسی", callback_data="lang:fa"),
            ]
        ]
    )


def mini_app_keyboard(locale: str) -> InlineKeyboardMarkup:
    settings = get_settings()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(locale, "open_mini_app"),
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ]
        ]
    )


def habit_checkin_keyboard(habit_id: str, title: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ {title}", callback_data=f"habit_check:{habit_id}")]
        ]
    )


def bill_paid_keyboard(bill_id: str, title: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"✓ {title}", callback_data=f"bill_paid:{bill_id}")]
        ]
    )
