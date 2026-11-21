#!/usr/bin/env bash
#
# Install a dedicated Cloudflare Tunnel for Ritmo Mini App.
#
#   ./deploy/install-tunnel.sh <tunnel-token>
#
# Cloudflare dashboard (Zero Trust → Networks → Tunnels):
#   Public Hostname: ritmo.mammad.site
#   Type: HTTP
#   URL:  localhost:8097
#
set -euo pipefail

TOKEN="${1:-}"
if [[ -z "$TOKEN" ]]; then
  echo "usage: $0 <tunnel-token>" >&2
  exit 1
fi

PORT="${RITMO_PORT:-8097}"
if ! curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/health"; then
  echo "Ritmo edge is not answering on 127.0.0.1:${PORT}." >&2
  echo "Start it with: cd /root/mk-projects/ritmo && docker compose -f docker-compose.prod.yml up -d" >&2
  exit 1
fi

install -d -m 700 /etc/cloudflared
printf '%s' "$TOKEN" > /etc/cloudflared/ritmo-token
chmod 600 /etc/cloudflared/ritmo-token

CF_BIN=/usr/local/bin/cloudflared
[[ -x "$CF_BIN" ]] || CF_BIN=/usr/bin/cloudflared

cat > /etc/systemd/system/cloudflared-ritmo.service <<UNIT
[Unit]
Description=cloudflared (Ritmo Mini App tunnel)
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
TimeoutStartSec=20
ExecStart=${CF_BIN} --no-autoupdate tunnel --protocol http2 run --token-file /etc/cloudflared/ritmo-token
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now cloudflared-ritmo
sleep 3
systemctl --no-pager --lines=20 status cloudflared-ritmo || true

echo
echo "Tunnel installed. Point ritmo.mammad.site → http://localhost:${PORT}"
echo "Then set Telegram webhook + menu button (see deploy/CLOUDFLARE.md)."
