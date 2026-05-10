#!/usr/bin/env bash
# Long-running Discord bot wrapper. Sourced by launchd plist with KeepAlive=true,
# so any crash automatically restarts the process.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Prefer project venv → python.org python (where discord.py is installed)
# → system python3 as last resort. The python.org python lives at a fixed
# Framework path; system python3 (/usr/bin/python3) lacks discord.py.
if [[ -x "$PROJECT_ROOT/.venv/bin/python3" ]]; then
  PY="$PROJECT_ROOT/.venv/bin/python3"
elif [[ -x "$PROJECT_ROOT/venv/bin/python3" ]]; then
  PY="$PROJECT_ROOT/venv/bin/python3"
elif [[ -x "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3" ]]; then
  PY="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
else
  PY="$(command -v python3)"
fi

echo "$(date '+%F %T') — starting discord_bot.py with $PY"
exec "$PY" "$PROJECT_ROOT/scripts/discord_bot.py"
