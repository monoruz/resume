#!/usr/bin/env bash
# Render an HTML resume to PDF via headless Chrome and report the page count.
#
# Usage: build/render.sh <resume.html> [out.pdf]
# Env:   STRICT_PAGES=1   exit non-zero if the result is not exactly 2 pages (used by CI)
#        CHROME=/path     override Chrome discovery
set -euo pipefail

find_chrome() {
  if [ -n "${CHROME:-}" ]; then echo "$CHROME"; return; fi
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "$(command -v google-chrome-stable || true)" \
    "$(command -v google-chrome || true)" \
    "$(command -v chromium-browser || true)" \
    "$(command -v chromium || true)"
  do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return; }
  done
  return 1
}

CHROME_BIN="$(find_chrome)" || { echo "error: no Chrome or Chromium found (set CHROME=/path)" >&2; exit 1; }

SRC="${1:?usage: build/render.sh <resume.html> [out.pdf]}"
[ -f "$SRC" ] || { echo "error: no such file: $SRC" >&2; exit 1; }
OUT="${2:-${SRC%.html}.pdf}"

SRC_ABS="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
OUT_DIR="$(dirname "$OUT")"; mkdir -p "$OUT_DIR"
OUT_ABS="$(cd "$OUT_DIR" && pwd)/$(basename "$OUT")"

PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/chrome-resume.XXXXXX")"
CPID=""
cleanup(){ [ -n "$CPID" ] && kill "$CPID" 2>/dev/null || true; rm -rf "$PROFILE"; }
trap cleanup EXIT

# Headless mode differs by platform: old headless hangs on --print-to-pdf for
# file:// URLs on some macOS builds, and new headless is the only mode present in
# recent Linux builds. Try each, take whichever produces output.
attempt() {
  local mode="$1"
  rm -f "$OUT_ABS"
  "$CHROME_BIN" \
    --headless="$mode" \
    --disable-gpu \
    --no-sandbox \
    --no-first-run \
    --no-pdf-header-footer \
    --virtual-time-budget=5000 \
    --user-data-dir="$PROFILE" \
    --print-to-pdf="$OUT_ABS" \
    "file://$SRC_ABS" >/dev/null 2>&1 &
  CPID=$!
  for _ in $(seq 1 30); do sleep 1; [ -s "$OUT_ABS" ] && break; done
  kill "$CPID" 2>/dev/null || true
  wait "$CPID" 2>/dev/null || true
  CPID=""
  [ -s "$OUT_ABS" ]
}

attempt old || attempt new || { echo "error: render produced no output in either headless mode" >&2; exit 1; }

PAGES=$(python3 - "$OUT_ABS" <<'PY'
import re, sys
d = open(sys.argv[1], 'rb').read()
n = len(re.findall(rb'/Type\s*/Page[^s]', d))
if not n:
    n = max((int(x) for x in re.findall(rb'/Count\s+(\d+)', d)), default=0)
print(n)
PY
)

SIZE=$(du -h "$OUT_ABS" | awk '{print $1}')
echo "rendered: $OUT  (${PAGES} page(s), ${SIZE})"

if [ "$PAGES" != "2" ]; then
  echo "  !! page count is ${PAGES}, target is 2 — tune the density knobs in the <style> block, or cut/add content"
  [ "${STRICT_PAGES:-0}" = "1" ] && exit 1
fi
exit 0
