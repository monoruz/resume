#!/usr/bin/env bash
# Send a one-line job-search event to mono's Telegram chat.
#
#   build/notify.sh <event> "<message>" [link]
#
# <event> is one of: applied, email, leads, waiting, daily, error, info
#
# Credentials are read from the environment, never from this repo:
#   TELEGRAM_BOT_TOKEN   bot token from @BotFather
#   TELEGRAM_CHAT_ID     chat id that receives the messages
# On a local machine they may instead live in ~/.config/jobs/telegram.env
# (two KEY=value lines, chmod 600). That file must never be committed.
#
# A missing token or a failed send prints a warning and exits 0, so a
# notification problem never stops the run that triggered it.

set -u

event="${1:-info}"
message="${2:-}"
link="${3:-}"

if [[ -z "$message" ]]; then
  echo "usage: build/notify.sh <event> \"<message>\" [link]" >&2
  exit 2
fi

local_env="${HOME}/.config/jobs/telegram.env"
if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]] && [[ -f "$local_env" ]]; then
  # shellcheck disable=SC1090
  set -a; . "$local_env"; set +a
fi

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]]; then
  echo "notify: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set; skipped" >&2
  exit 0
fi

case "$event" in
  applied) icon="✅"; label="Applied" ;;
  email)   icon="📧"; label="Email" ;;
  leads)   icon="🔎"; label="New leads" ;;
  waiting) icon="⏳"; label="Waiting on you" ;;
  daily)   icon="📋"; label="Daily search" ;;
  error)   icon="⚠️"; label="Problem" ;;
  *)       icon="ℹ️"; label="Update" ;;
esac

text="${icon} ${label}"$'\n'"${message}"
[[ -n "$link" ]] && text+=$'\n'"${link}"

# Telegram caps a message at 4096 characters.
text="${text:0:4000}"

response="$(curl -sS --max-time 20 \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${text}" \
  --data-urlencode "disable_web_page_preview=true" 2>&1)"

if [[ "$response" == *'"ok":true'* ]]; then
  echo "notify: sent ($event)"
else
  # Print Telegram's description only; never echo the request URL (it holds the token).
  desc="$(printf '%s' "$response" | sed -n 's/.*"description":"\([^"]*\)".*/\1/p')"
  echo "notify: send failed (${desc:-network error}); continuing" >&2
fi
exit 0
