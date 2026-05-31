#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ROUTINE_FILE="${1:-}"

if [[ -z "$ROUTINE_FILE" ]]; then
  echo "Usage: $0 <routine-markdown-file>"
  exit 1
fi

ROUTINE_PATH="$PROJECT_ROOT/$ROUTINE_FILE"
if [[ ! -f "$ROUTINE_PATH" ]]; then
  echo "Routine file not found: $ROUTINE_PATH" >&2
  exit 1
fi

PROMPT="$(cat "$ROUTINE_PATH")"
ROUTINE_NAME="$(basename "$ROUTINE_FILE" .md)"

# Post a one-liner to Discord (#general if configured, else #daily_brief).
# Uses only stdlib (json + urllib) — no httpx or dotenv needed.
_discord_ping() {
  local title="$1" body="$2"
  python3 - "$title" "$body" "$PROJECT_ROOT" <<'PYEOF' 2>/dev/null || true
import json, sys, urllib.request, urllib.error
from pathlib import Path
title, body, project_root = sys.argv[1], sys.argv[2], sys.argv[3]
cfg_path = Path(project_root) / "memory" / "discord_config.json"
if not cfg_path.exists():
    sys.exit(0)
try:
    cfg = json.loads(cfg_path.read_text())
except Exception:
    sys.exit(0)
for ch in ("general", "daily_brief"):
    chan = cfg.get("channels", {}).get(ch, {})
    url = chan.get("webhook_url", "")
    if not url or "REPLACE" in url:
        continue
    payload = json.dumps({
        "embeds": [{"title": title, "description": body, "color": 10070709}]
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "DiscordBot (trading-agent, 1.0)"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass
    break
PYEOF
}

TIMESTAMP_ET="$(TZ=America/New_York date '+%a %Y-%m-%d %H:%M ET')"
_discord_ping "▶ Routine starting: ${ROUTINE_NAME}" "${TIMESTAMP_ET}"

# Locate the claude CLI. Try common install paths in priority order, then
# fall back to PATH lookup so this works on both Mac (~/.local/bin) and
# CI runners (npm global / /usr/local/bin).
CLAUDE_BIN=""
for candidate in "$HOME/.local/bin/claude" "/usr/local/bin/claude" "/opt/homebrew/bin/claude"; do
  if [[ -x "$candidate" ]]; then
    CLAUDE_BIN="$candidate"
    break
  fi
done
if [[ -z "$CLAUDE_BIN" ]]; then
  CLAUDE_BIN="$(command -v claude || true)"
fi
if [[ -z "$CLAUDE_BIN" ]] || [[ ! -x "$CLAUDE_BIN" ]]; then
  echo "Claude CLI not found in ~/.local/bin, /usr/local/bin, /opt/homebrew/bin, or PATH" >&2
  exit 1
fi

# In CI (GitHub Actions), skip permission prompts — no human available to approve.
CLAUDE_FLAGS="-p"
if [[ "${CI:-}" == "true" ]]; then
  CLAUDE_FLAGS="--dangerously-skip-permissions -p"
fi

# Retry once on transient socket/network errors (60s gives the connection time to recover).
# Routines are safe to retry — they read current state before acting.
MAX_ATTEMPTS=2
ATTEMPT=0
ROUTINE_EXIT=1
while (( ATTEMPT < MAX_ATTEMPTS )); do
  ATTEMPT=$(( ATTEMPT + 1 ))
  if (( ATTEMPT > 1 )); then
    echo "$(date '+%F %T') — socket/network error on attempt 1; retrying in 60s..."
    sleep 60
  fi
  # caffeinate -i holds an assertion against system sleep for the life of the process.
  # Without it, macOS can sleep mid-routine and drop the socket connection.
  # On Linux (GHA) caffeinate is absent; the `command -v` check skips it cleanly.
  if command -v caffeinate &>/dev/null; then
    # shellcheck disable=SC2086
    caffeinate -i "$CLAUDE_BIN" $CLAUDE_FLAGS "$PROMPT" 2>&1
  else
    # shellcheck disable=SC2086
    "$CLAUDE_BIN" $CLAUDE_FLAGS "$PROMPT" 2>&1
  fi
  ROUTINE_EXIT=$?
  [[ "$ROUTINE_EXIT" -eq 0 ]] && break
  echo "$(date '+%F %T') — claude exited $ROUTINE_EXIT on attempt $ATTEMPT"
done

if [[ "$ROUTINE_EXIT" -eq 0 ]]; then
  _discord_ping "✅ Routine done: ${ROUTINE_NAME}" "Completed successfully · $(TZ=America/New_York date '+%H:%M ET')"
  # Write lockfile so GHA failsafe knows local already ran this slot.
  python3 - "$PROJECT_ROOT" "$ROUTINE_FILE" <<'PYEOF' 2>/dev/null || true
import json, time, sys
lock = {"routine": sys.argv[2], "fired_by": "local", "fired_at_epoch": int(time.time())}
open(sys.argv[1] + "/memory/last_routine_run.json", "w").write(json.dumps(lock))
PYEOF
else
  _discord_ping "❌ Routine failed: ${ROUTINE_NAME}" "Exit code ${ROUTINE_EXIT} · $(TZ=America/New_York date '+%H:%M ET') — check launchd log"
fi

# Track token usage estimate for the dashboard
python3 "$SCRIPT_DIR/track_usage.py" "$ROUTINE_FILE" "$ROUTINE_EXIT" 2>/dev/null || true

# Git cowork mode — auto-commit memory + journal updates after each routine.
# Toggle with: export TRADING_GIT_AUTOCOMMIT=1 (default OFF until user enables).
if [[ "${TRADING_GIT_AUTOCOMMIT:-0}" == "1" ]] && [[ -d "$PROJECT_ROOT/.git" ]]; then
  cd "$PROJECT_ROOT"
  ROUTINE_NAME="$(basename "$ROUTINE_FILE" .md)"
  TIMESTAMP="$(date '+%Y-%m-%d %H:%M %Z')"

  # Stage only memory + journal + docs/adr (never code, never .env)
  git add memory/ journal/ docs/adr/ 2>/dev/null || true

  # Commit only if there's something staged
  if ! git diff --cached --quiet; then
    git commit -m "routine($ROUTINE_NAME): $TIMESTAMP" || true

    # Push only if a remote is configured
    if git remote get-url origin >/dev/null 2>&1; then
      git push origin HEAD 2>&1 || echo "git push failed — will retry next routine"
    fi
  fi
fi

exit $ROUTINE_EXIT
