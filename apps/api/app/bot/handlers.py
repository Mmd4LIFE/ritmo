from __future__ import annotations

from uuid import UUID

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from app.bot.keyboards import language_keyboard, mini_app_keyboard
from app.core.database import AsyncSessionLocal
from app.i18n.loader import t
from app.services.billing import activate_premium, list_plans
from app.services.bills import mark_paid
from app.services.habits import checkin_habit
from app.services.users import get_or_create_user


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        await db.commit()
        locale = user.locale
    await message.answer(t(locale, "choose_language"), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery) -> None:
    locale = callback.data.split(":", 1)[1]
    if locale not in ("en", "fa"):
        locale = "en"
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=callback.from_user.id, locale=locale)
        user.locale = locale
        await db.commit()
    await callback.message.edit_text(t(locale, "language_set"))
    await callback.message.answer(t(locale, "welcome"), reply_markup=mini_app_keyboard(locale))
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=message.from_user.id)
        await db.commit()
        locale = user.locale
    await message.answer(t(locale, "help"), reply_markup=mini_app_keyboard(locale))


@router.message(Command("app"))
async def cmd_app(message: Message) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=message.from_user.id)
        await db.commit()
        locale = user.locale
    await message.answer(t(locale, "open_mini_app"), reply_markup=mini_app_keyboard(locale))


@router.callback_query(F.data.startswith("habit_check:"))
async def habit_check(callback: CallbackQuery) -> None:
    habit_id = UUID(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=callback.from_user.id)
        try:
            habit, created = await checkin_habit(db, user, habit_id)
        except ValueError:
            await callback.answer("Not found", show_alert=True)
            return
        await db.commit()
        locale = user.locale
        if created:
            text = t(locale, "habit_checked", title=habit.title, streak=habit.streak_current)
        else:
            text = t(locale, "habit_already", title=habit.title)
    await callback.answer(text, show_alert=True)


@router.callback_query(F.data.startswith("bill_paid:"))
async def bill_paid(callback: CallbackQuery) -> None:
    bill_id = UUID(callback.data.split(":", 1)[1])
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=callback.from_user.id)
        try:
            bill = await mark_paid(db, user, bill_id)
        except ValueError:
            await callback.answer("Not found", show_alert=True)
            return
        await db.commit()
        text = t(user.locale, "bill_paid", title=bill.title, next_due=str(bill.next_due))
    await callback.answer(text, show_alert=True)


@router.message(Command("premium"))
async def cmd_premium(message: Message) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=message.from_user.id)
        plans = await list_plans(db)
        await db.commit()
        premium = next((p for p in plans if p.code == "premium"), None)
        locale = user.locale
    if not premium or premium.stars_price <= 0:
        await message.answer(t(locale, "premium_required"), reply_markup=mini_app_keyboard(locale))
        return
    prices = [LabeledPrice(label=premium.name, amount=premium.stars_price)]
    await message.answer_invoice(
        title="Ritmo Premium",
        description="Unlimited habits & bills, cycle insights, quiet controls",
        payload=f"premium:{user.id}",
        currency="XTR",
        prices=prices,
        provider_token="",  # Stars
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    payment = message.successful_payment
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, telegram_id=message.from_user.id)
        await activate_premium(
            db,
            user,
            stars=payment.total_amount,
            payload=payment.invoice_payload,
            charge_id=payment.telegram_payment_charge_id,
        )
        await db.commit()
        locale = user.locale
    await message.answer("Premium activated!" if locale == "en" else "پریمیوم فعال شد!")
