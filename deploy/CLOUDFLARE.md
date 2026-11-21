# Cloudflare Tunnel for ritmo.mammad.site

## Prerequisites

1. Domain `mammad.site` managed in Cloudflare DNS
2. Cloudflare Zero Trust account
3. Bot token from [@BotFather](https://t.me/BotFather)
4. Mini App URL set in BotFather → Bot Settings → Menu Button / Web App: `https://ritmo.mammad.site`

## Create tunnel (dashboard or CLI)

### Option A — Token (used by docker-compose.prod.yml)

1. Cloudflare Zero Trust → Networks → Tunnels → Create
2. Name: `ritmo`
3. Public hostname:
   - Hostname: `ritmo.mammad.site`
   - Path: (empty) → Service: `http://web:3000`
4. Add another public hostname / path rules (or use Ingress in config):
   - Path `/api*` → `http://api:8000`
   - Path `/webhook*` → `http://api:8000`
   - Path `/health` → `http://api:8000`

If the dashboard only allows one service, use a local config file instead (Option B) or put Next.js rewrites in front. Recommended docker network approach with `cloudflared` config:

### Option B — Config file (more control)

`deploy/cloudflared-config.yml`:

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: ritmo.mammad.site
    path: /api/*
    service: http://api:8000
  - hostname: ritmo.mammad.site
    path: /webhook/*
    service: http://api:8000
  - hostname: ritmo.mammad.site
    path: /health
    service: http://api:8000
  - hostname: ritmo.mammad.site
    service: http://web:3000
  - service: http_status:404
```

Then run cloudflared with that config instead of `TUNNEL_TOKEN`.

## After tunnel is live

1. Set webhook:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://ritmo.mammad.site/webhook/telegram" \
  -d "secret_token=${TELEGRAM_WEBHOOK_SECRET}"
```

2. Open the bot → `/start` → Mini App

## VPS hardening checklist

- Rotate root password (if ever shared)
- Add your SSH key; disable `PasswordAuthentication`
- `ufw allow OpenSSH`; deny public 80/443 if using tunnel only
- Keep `.env` only on server (`chmod 600`)
