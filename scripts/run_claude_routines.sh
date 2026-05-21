#!/usr/bin/env bash
# launchd routine dispatcher. Fired by StartCalendarInterval at each routine's
# scheduled Madrid-wall-clock time (which maps to the intended ET time via the
# TZ=America/New_York env var set in the plist).
#
# Uses ±10-minute windows instead of exact-minute matching because launchd can
# fire jobs late after sleep/wake or load spikes. Exact matching was the root
# cause of "No scheduled routine" failures during Week 2 (2026-05-11..14).
set -euo pipefail
export TZ=America/New_York  # plist env var doesn't propagate to shell on macOS; force date to return ET

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RUNNER="$SCRIPT_DIR/run_claude_routine.sh"

DOW="$(date '+%u')"   # 1=Mon … 7=Sun
HOUR="$(date '+%H')"
MIN="$(date '+%M')"
HHMM=$((10#$HOUR * 100 + 10#$MIN))

ROUTINE=""
if   (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 800  && HHMM <= 814  )); then
  ROUTINE="routines/1_pre_market_research.md"
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 935  && HHMM <= 949  )); then
  ROUTINE="routines/2_market_open_execution.md"
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 1230 && HHMM <= 1244 )); then
  ROUTINE="routines/3_midday_scan.md"
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 1545 && HHMM <= 1559 )); then
  ROUTINE="routines/4_end_of_day_review.md"
elif (( DOW == 5 ))              && (( HHMM >= 1630 && HHMM <= 1644 )); then
  ROUTINE="routines/5_weekly_review.md"
else
  echo "$(date '+%F %T') — no scheduled routine for DOW=$DOW HHMM=$HHMM"
  exit 0
fi

cd "$PROJECT_ROOT"

# Write lockfile so GHA can see that local ran (GHA is failsafe-only).
# Push just this one file so GHA's checkout picks it up; failures are non-fatal.
LOCKFILE="$PROJECT_ROOT/memory/last_routine_run.json"
python3 -c "import json,time; json.dump({'routine':'$ROUTINE','fired_by':'local','fired_at_epoch':int(time.time())},open('$LOCKFILE','w'))"
git pull --ff-only --quiet 2>/dev/null || true
git add "$LOCKFILE" 2>/dev/null || true
git diff --cached --quiet 2>/dev/null || git commit -m "routine-lock(local): $ROUTINE" --no-verify -q 2>/dev/null || true
git push origin HEAD --quiet 2>/dev/null || true

echo "$(date '+%F %T') — dispatching $ROUTINE (DOW=$DOW HHMM=$HHMM)"
"$RUNNER" "$ROUTINE"
