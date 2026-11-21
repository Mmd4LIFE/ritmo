# Ritmo

Professional Telegram lifestyle bot + Mini App.

- Morning digest (weather, calendar, prices, one news item)
- Habit streaks with check-in
- Bill / subscription reminders
- Private cycle tracking
- Unified calendar & profile
- EN / FA (RTL)
- Telegram Stars Premium ready

## Stack

- **API:** FastAPI, aiogram 3, SQLAlchemy 2, Alembic, Postgres
- **Worker:** APScheduler (digest, bills, streaks, cycle)
- **Mini App:** Next.js 15, Tailwind, shadcn-style UI, next-intl
- **Deploy:** Docker Compose + Cloudflare Tunnel → `ritmo.mammad.site`

## Quick start (local)

```bash
cp .env.example .env
# set TELEGRAM_BOT_TOKEN if you have one (optional for API/dev auth)

docker compose up --build
```

- Mini App: http://localhost:3000 (use **Continue as dev user**)
- API health: http://localhost:8000/health
- Telegram webhook (prod): `POST /webhook/telegram`

## Bot commands

- `/start` — language + Mini App
- `/app` — open Mini App
- `/help` — short help
- `/premium` — Telegram Stars invoice

## Production

```bash
cp .env.example .env
# fill secrets, TELEGRAM_BOT_TOKEN, TUNNEL_TOKEN, strong DB password

docker compose -f docker-compose.prod.yml up -d --build
```

See [deploy/CLOUDFLARE.md](deploy/CLOUDFLARE.md) for tunnel setup on `ritmo.mammad.site`.

## Security

Never commit `.env`. Rotate any password that was shared in chat. Prefer SSH keys and disable password login on the VPS.
