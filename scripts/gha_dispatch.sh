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

DOW="$(date '+%u')"   # 1=Mon … 7=Sun
HOUR="$(date '+%H')"
MIN="$(date '+%M')"
HHMM=$((10#$HOUR * 100 + 10#$MIN))

# GHA is FAILSAFE-ONLY for the 5 main routines. Strategy:
#   - Main routine windows start 15 min after scheduled time, giving local Mac
#     priority. If local ran and pushed the lockfile, GHA skips.
#   - Discord dispatcher fills all other active-window slots (idempotent, cheap).
#
# Schedule (ET) → GHA failsafe window:
#   Pre-market   08:00 → 08:15–08:29
#   Market-open  09:35 → 09:50–10:04
#   Midday       12:30 → 12:45–12:59
#   EOD          15:45 → 16:00–16:14
#   Weekly (Fri) 16:30 → 16:45–16:59

ROUTINE=""
IS_MAIN_ROUTINE=0
if   (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 815  && HHMM <= 829  )); then
  ROUTINE="routines/1_pre_market_research.md";  IS_MAIN_ROUTINE=1
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 950  && HHMM <= 1004 )); then
  ROUTINE="routines/2_market_open_execution.md"; IS_MAIN_ROUTINE=1
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 1245 && HHMM <= 1259 )); then
  ROUTINE="routines/3_midday_scan.md";           IS_MAIN_ROUTINE=1
elif (( DOW >= 1 && DOW <= 5 )) && (( HHMM >= 1600 && HHMM <= 1614 )); then
  ROUTINE="routines/4_end_of_day_review.md";     IS_MAIN_ROUTINE=1
elif (( DOW == 5 ))              && (( HHMM >= 1645 && HHMM <= 1659 )); then
  ROUTINE="routines/5_weekly_review.md";         IS_MAIN_ROUTINE=1
else
  # GHA is failsafe-only for the 5 main routines. The discord dispatcher runs
  # locally via run_claude_polling.sh and doesn't need a cloud backup — running
  # it here would burn API credits every 15 min unnecessarily.
  echo "$(date '+%F %T %Z') — no routine for DOW=$DOW HHMM=$HHMM (idle)"
  exit 0
fi

cd "$PROJECT_ROOT"

# For main routines: skip if local Mac already ran this slot (lockfile in git).
LOCKFILE="$PROJECT_ROOT/memory/last_routine_run.json"
if [[ "$IS_MAIN_ROUTINE" == "1" ]] && [[ -f "$LOCKFILE" ]]; then
  SKIP=$(python3 - "$LOCKFILE" "$ROUTINE" <<'EOF'
import json, time, sys
try:
    d = json.load(open(sys.argv[1]))
    same     = d.get("routine")   == sys.argv[2]
    by_local = d.get("fired_by")  == "local"
    age      = time.time() - d.get("fired_at_epoch", 0)
    print("1" if same and by_local and age < 1800 else "0")
except Exception:
    print("0")
EOF
  )
  if [[ "$SKIP" == "1" ]]; then
    echo "$(date '+%F %T %Z') — skipping $ROUTINE (local Mac ran it; GHA failsafe not needed)"
    exit 0
  fi
  echo "$(date '+%F %T %Z') — local Mac missed $ROUTINE; firing as failsafe"
fi

if [[ "$IS_MAIN_ROUTINE" == "1" ]]; then
  python3 -c "import json,time; json.dump({'routine':'$ROUTINE','fired_by':'gha','fired_at_epoch':int(time.time())},open('$LOCKFILE','w'))"
fi

echo "$(date '+%F %T %Z') — dispatching $ROUTINE"
"$RUNNER" "$ROUTINE"
