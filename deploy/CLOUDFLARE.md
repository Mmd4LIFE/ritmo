# Cloudflare Tunnel for ritmo.mammad.site

Same pattern as crypto / pulse / ludo on this VPS.

## App entrypoint

Docker edge nginx listens on **`127.0.0.1:8097`** and routes:

- `/` → Mini App
- `/api/*`, `/webhook/*`, `/health` → FastAPI

## Create tunnel

1. Cloudflare Zero Trust → Networks → Tunnels → Create → name `ritmo`
2. Public hostname:
   - Hostname: `ritmo.mammad.site`
   - Type: HTTP
   - URL: `localhost:8097`
3. Copy the tunnel token, then on the VPS:

```bash
cd /root/mk-projects/ritmo
./deploy/install-tunnel.sh '<TUNNEL_TOKEN>'
```

## After tunnel is live

```bash
cd /root/mk-projects/ritmo
set -a; source .env; set +a
./deploy/set-telegram.sh
```

Open [@rit_mo_bot](https://t.me/rit_mo_bot) → `/start`.

## Security

- Rotate root password if it was shared in chat
- Prefer SSH keys; disable password login
- Never commit `.env` or bot tokens
- `chmod 600 /root/mk-projects/ritmo/.env`
