#!/usr/bin/env bash
set -euo pipefail

# Run on the VPS as root after cloning the repo.
# Does NOT print or embed passwords.

APP_DIR="${APP_DIR:-/opt/ritmo}"

apt-get update
apt-get install -y ca-certificates curl git ufw

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

ufw allow OpenSSH
ufw --force enable || true

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ ! -d .git ]; then
  git clone https://github.com/Mmd4LIFE/ritmo.git .
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env — edit secrets before starting:"
  echo "  nano $APP_DIR/.env"
  exit 1
fi

docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps
echo "Done. Configure Cloudflare Tunnel token in .env (TUNNEL_TOKEN) and restart cloudflared."
