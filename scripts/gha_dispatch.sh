#!/usr/bin/env bash
# GitHub Actions dispatcher — analogue of run_claude_routines.sh but
# evaluated against America/New_York time (set via TZ in the workflow).
#
# Picks a routine based on current ET day-of-week + HH:MM and runs it
# through scripts/run_claude_routine.sh. Exits 0 silently if the current
# slot doesn't map to any routine, so the every-15-min cron is cheap.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run_claude_routine.sh"

DOW="$(date '+%u')"     # 1=Mon … 7=Sun
HOUR="$(date '+%H')"
MIN="$(date '+%M')"
KEY="${DOW} ${HOUR} ${MIN}"

ROUTINE=""
case "$KEY" in
  "1 08 00"|"2 08 00"|"3 08 00"|"4 08 00"|"5 08 00")
    ROUTINE="routines/1_pre_market_research.md" ;;
  "1 09 35"|"2 09 35"|"3 09 35"|"4 09 35"|"5 09 35")
    ROUTINE="routines/2_market_open_execution.md" ;;
  "1 12 30"|"2 12 30"|"3 12 30"|"4 12 30"|"5 12 30")
    ROUTINE="routines/3_midday_scan.md" ;;
  "1 15 45"|"2 15 45"|"3 15 45"|"4 15 45"|"5 15 45")
    ROUTINE="routines/4_end_of_day_review.md" ;;
  "5 16 30")
    ROUTINE="routines/5_weekly_review.md" ;;
  *)
    # Non-routine slot. Run the Discord dispatcher if we're inside the
    # active polling window (Mon-Fri 08:00–16:30 ET), else exit silently.
    HHMM=$((10#$HOUR * 100 + 10#$MIN))
    if (( DOW <= 5 )) && (( HHMM >= 800 )) && (( HHMM <= 1630 )); then
      ROUTINE="routines/6_discord_dispatcher.md"
    else
      echo "$(date '+%F %T %Z') — no routine for slot $KEY (idle)"
      exit 0
    fi
    ;;
esac

cd "$PROJECT_ROOT"
echo "$(date '+%F %T %Z') — dispatching $ROUTINE"
"$RUNNER" "$ROUTINE"
