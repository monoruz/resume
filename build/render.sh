#!/usr/bin/env bash
# Render an HTML resume to PDF via headless Chrome and report the page count.
# Usage: build/render.sh jobs/<slug>/resume.html [out.pdf]
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "error: Google Chrome not found at $CHROME" >&2; exit 1; }

SRC="${1:?usage: build/render.sh <resume.html> [out.pdf]}"
[ -f "$SRC" ] || { echo "error: no such file: $SRC" >&2; exit 1; }
OUT="${2:-${SRC%.html}.pdf}"

SRC_ABS="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"
OUT_DIR="$(dirname "$OUT")"; mkdir -p "$OUT_DIR"
OUT_ABS="$(cd "$OUT_DIR" && pwd)/$(basename "$OUT")"
rm -f "$OUT_ABS"

PROFILE="$(mktemp -d "${TMPDIR:-/tmp}/chrome-resume.XXXXXX")"
cleanup(){ [ -n "${CPID:-}" ] && kill "$CPID" 2>/dev/null || true; rm -rf "$PROFILE"; }
trap cleanup EXIT

# NOTE: --headless=old is deliberate. The new headless mode hangs on
# --print-to-pdf for local file:// URLs on this machine.
"$CHROME" \
  --headless=old \
  --disable-gpu \
  --no-first-run \
  --no-pdf-header-footer \
  --virtual-time-budget=3000 \
  --user-data-dir="$PROFILE" \
  --print-to-pdf="$OUT_ABS" \
  "file://$SRC_ABS" >/dev/null 2>&1 &
CPID=$!

for _ in $(seq 1 30); do sleep 1; [ -s "$OUT_ABS" ] && break; done
kill "$CPID" 2>/dev/null || true
wait "$CPID" 2>/dev/null || true

[ -s "$OUT_ABS" ] || { echo "error: render produced no output" >&2; exit 1; }

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
fi
