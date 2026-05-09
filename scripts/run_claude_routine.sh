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

CLAUDE_BIN="/usr/local/bin/claude"
if [[ ! -x "$CLAUDE_BIN" ]]; then
  echo "Claude CLI not found or not executable at $CLAUDE_BIN" >&2
  exit 1
fi

"$CLAUDE_BIN" -p "$PROMPT"
ROUTINE_EXIT=$?

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
