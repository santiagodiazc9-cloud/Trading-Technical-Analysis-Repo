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
