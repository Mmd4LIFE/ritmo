from __future__ import annotations

from datetime import datetime

import feedparser
import httpx
import pytz
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.i18n.loader import t
from app.models.calendar import CalendarEvent
from app.models.digest import DigestPrefs
from app.models.user import User


NEWS_FEEDS = {
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
}


async def fetch_weather(city: str | None, lat: str | None, lon: str | None) -> str | None:
    params: dict[str, str | float] = {"current_weather": "true"}
    if lat and lon:
        params["latitude"] = float(lat)
        params["longitude"] = float(lon)
    elif city:
        # Geocode via Open-Meteo
        async with httpx.AsyncClient(timeout=10) as client:
            geo = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1},
            )
            geo.raise_for_status()
            data = geo.json()
            results = data.get("results") or []
            if not results:
                return None
            params["latitude"] = results[0]["latitude"]
            params["longitude"] = results[0]["longitude"]
    else:
        return None

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        resp.raise_for_status()
        cw = resp.json().get("current_weather") or {}
        temp = cw.get("temperature")
        wind = cw.get("windspeed")
        if temp is None:
            return None
        return f"{temp}°C, wind {wind} km/h"


async def fetch_prices(symbols: list[str] | None) -> str | None:
    symbols = symbols or ["USD/IRR"]
    # Lightweight public FX snapshot via open.er-api.com (USD base)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/USD")
            resp.raise_for_status()
            rates = resp.json().get("rates") or {}
    except Exception:
        return None

    parts: list[str] = []
    for symbol in symbols[:5]:
        sym = symbol.upper().replace(" ", "")
        if sym in ("USD/IRR", "USDIRR", "IRR"):
            irr = rates.get("IRR")
            if irr:
                parts.append(f"USD/IRR {irr:,.0f}")
        elif sym in ("EUR/USD", "EURUSD", "EUR"):
            eur = rates.get("EUR")
            if eur:
                parts.append(f"EUR/USD {1/eur:.4f}" if eur else "")
        elif sym in ("GOLD", "XAU"):
            parts.append("Gold: check local rate")
    return ", ".join(p for p in parts if p) or None


def fetch_news(topic: str) -> str | None:
    feed_url = NEWS_FEEDS.get(topic, NEWS_FEEDS["technology"])
    try:
        parsed = feedparser.parse(feed_url)
        if not parsed.entries:
            return None
        return parsed.entries[0].get("title")
    except Exception:
        return None


async def compose_digest(db: AsyncSession, user: User) -> str:
    prefs = user.digest_prefs
    locale = user.locale or "en"
    lines = [t(locale, "digest_header")]

    if prefs and prefs.include_weather:
        city = prefs.city or (user.profile.city if user.profile else None)
        weather = await fetch_weather(city, prefs.latitude if prefs else None, prefs.longitude if prefs else None)
        if weather:
            lines.append(t(locale, "digest_weather", city=city or "—", summary=weather))

    if prefs is None or prefs.include_calendar:
        try:
            tz = pytz.timezone(user.timezone)
        except Exception:
            tz = pytz.timezone("Asia/Tehran")
        start = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59)
        result = await db.execute(
            select(CalendarEvent).where(
                and_(
                    CalendarEvent.user_id == user.id,
                    CalendarEvent.starts_at >= start,
                    CalendarEvent.starts_at <= end,
                )
            ).limit(5)
        )
        events = list(result.scalars().all())
        if events:
            items = "; ".join(e.title for e in events)
            lines.append(t(locale, "digest_calendar", items=items))

    if prefs is None or prefs.include_prices:
        prices = await fetch_prices(prefs.price_symbols if prefs else None)
        if prices:
            lines.append(t(locale, "digest_prices", items=prices))

    if prefs is None or prefs.include_news:
        topic = prefs.news_topic if prefs else "technology"
        news = fetch_news(topic)
        if news:
            lines.append(t(locale, "digest_news", title=news))

    return "\n".join(lines)


async def users_due_for_digest(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .join(DigestPrefs, DigestPrefs.user_id == User.id)
        .where(DigestPrefs.enabled.is_(True))
        .options(
            selectinload(User.profile),
            selectinload(User.digest_prefs),
        )
    )
    users = list(result.scalars().unique().all())
    due: list[User] = []
    now_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)
    for user in users:
        prefs = user.digest_prefs
        if not prefs:
            continue
        try:
            tz = pytz.timezone(user.timezone)
        except Exception:
            tz = pytz.timezone("Asia/Tehran")
        local = now_utc.astimezone(tz)
        if local.hour != prefs.hour or local.minute != prefs.minute:
            continue
        if prefs.last_sent_at:
            last_local = prefs.last_sent_at.astimezone(tz)
            if last_local.date() == local.date():
                continue
        due.append(user)
    return due
