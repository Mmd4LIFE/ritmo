#!/usr/bin/env bash
set -euo pipefail

# Usage (on server, with .env loaded):
#   set -a; source /root/mk-projects/ritmo/.env; set +a
#   ./deploy/set-telegram.sh

: "${TELEGRAM_BOT_TOKEN:?TELEGRAM_BOT_TOKEN required}"
: "${TELEGRAM_WEBHOOK_SECRET:?TELEGRAM_WEBHOOK_SECRET required}"
BASE_URL="${PUBLIC_BASE_URL:-https://ritmo.mammad.site}"

curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=${BASE_URL}/webhook/telegram" \
  -d "secret_token=${TELEGRAM_WEBHOOK_SECRET}" \
  -d "drop_pending_updates=true"

echo

curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setChatMenuButton" \
  -H 'Content-Type: application/json' \
  -d "{\"menu_button\":{\"type\":\"web_app\",\"text\":\"Ritmo\",\"web_app\":{\"url\":\"${BASE_URL}\"}}}"

echo
curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
echo
