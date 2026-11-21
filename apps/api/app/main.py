from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.billing.router import router as billing_router
from app.bills.router import router as bills_router
from app.bot.setup import create_bot, create_dispatcher
from app.calendar.router import router as calendar_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.cycle.router import router as cycle_router
from app.digest.router import router as digest_router
from app.habits.router import router as habits_router
from app.services.billing import seed_plans
from app.users.router import router as users_router

settings = get_settings()
bot = create_bot()
dp = create_dispatcher()
_polling_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _polling_task
    async with AsyncSessionLocal() as db:
        await seed_plans(db)
        await db.commit()

    use_polling = False
    if settings.telegram_bot_token and settings.environment != "development":
        webhook_url = f"{settings.public_base_url.rstrip('/')}/webhook/telegram"
        try:
            await bot.set_webhook(
                webhook_url,
                secret_token=settings.telegram_webhook_secret,
                drop_pending_updates=True,
            )
            print(f"webhook set: {webhook_url}")
        except Exception as exc:
            # Telegram DNS can lag behind public resolvers; keep the bot alive via polling.
            print(f"webhook setup failed, falling back to polling: {exc}")
            use_polling = True
    elif settings.telegram_bot_token and settings.environment == "development":
        use_polling = True

    if use_polling and settings.telegram_bot_token:
        await bot.delete_webhook(drop_pending_updates=True)
        _polling_task = asyncio.create_task(dp.start_polling(bot))
        print("telegram polling started")

    yield

    if _polling_task is not None:
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
        await dp.stop_polling()
    await bot.session.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(habits_router)
app.include_router(bills_router)
app.include_router(calendar_router)
app.include_router(cycle_router)
app.include_router(digest_router)
app.include_router(billing_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if settings.telegram_webhook_secret and x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}
