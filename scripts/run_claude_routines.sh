#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run_claude_routine.sh"

CURRENT="$(date '+%u %H %M')"
ROUTINE=""
case "$CURRENT" in
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
    echo "No scheduled routine for $CURRENT"
    exit 0
    ;;
esac

cd "$PROJECT_ROOT"
"$RUNNER" "$ROUTINE"
