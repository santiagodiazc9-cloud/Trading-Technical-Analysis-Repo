#!/usr/bin/env bash
# Polling dispatcher — runs every 15 minutes via launchd, but only fires the
# polling routine during active trading-day hours.
#
# Active window: Mon-Fri, 08:00–16:30 local time (matches scheduled trading
# routines which run in ET; machine clock should be ET).
#
# Outside the window: exit 0 silently.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run_claude_routine.sh"

# Day-of-week (1=Mon, 7=Sun)
DOW="$(date '+%u')"
HOUR="$(date '+%H')"
MIN="$(date '+%M')"

# Skip weekends
if [[ "$DOW" -gt 5 ]]; then
  echo "$(date '+%F %T') — polling skipped (weekend)"
  exit 0
fi

# HHMM as a comparable integer
NOW_HHMM=$((10#$HOUR * 100 + 10#$MIN))

# Active: 08:00 (= 800) through 16:30 (= 1630) inclusive
if (( NOW_HHMM < 800 || NOW_HHMM > 1630 )); then
  echo "$(date '+%F %T') — polling skipped (outside 08:00–16:30 ET window)"
  exit 0
fi

cd "$PROJECT_ROOT"
"$RUNNER" "routines/6_clickup_polling.md"
