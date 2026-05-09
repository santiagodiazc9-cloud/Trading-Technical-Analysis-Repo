#!/usr/bin/env python3
"""
Vault index helper for the Obsidian/RuFlo brain.

Walks the project vault, builds a manifest of markdown files that should be
indexed into RuFlo memory, and emits the manifest as JSON to stdout.

This script does NOT call RuFlo MCP itself (Python can't reach MCP tools
directly). Instead, run this from a Claude Code session that has the
mcp__ruflo__memory_store tool, then have Claude iterate the manifest and
write each entry.

Usage:
    python3 scripts/vault_index.py                # all .md files in vault
    python3 scripts/vault_index.py --since 2026-05-09   # only files modified since
    python3 scripts/vault_index.py --paths memory/ docs/adr/   # restrict scope

The output schema (for Claude to consume):
    {
      "namespace": "trading-vault",
      "entries": [
        {
          "path": "memory/strategy.md",
          "key": "vault/memory/strategy",
          "tags": ["vault", "memory", "strategy"],
          "mtime": "2026-05-09T18:00:00Z",
          "size_bytes": 1234,
          "content_preview": "# Active Strategy\\n\\n## Current Approach...",
          "suggested_value": "<full file content>"
        },
        ...
      ]
    }
"""
import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Folders the indexer ignores entirely.
EXCLUDED_DIRS = {
    ".git",
    ".claude",
    ".claude-flow",
    ".swarm",
    ".obsidian",
    ".vscode",
    "attachments",
    "__pycache__",
    "venv",
    ".venv",
    "templates",  # templates aren't recall content
}

# Files that are auto-managed; indexing them creates churn without value.
EXCLUDED_FILES = {
    "memory/last_poll.json",
    "memory/clickup_config.json",
    "memory/trade_log.json",
    "memory/watchlist.json",
    "memory/pending_clickup_updates.md",
}


def slugify(s: str) -> str:
    out = []
    for ch in s.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def derive_tags(rel_path: Path) -> list[str]:
    parts = rel_path.parts
    tags = ["vault"]
    if parts:
        tags.append(parts[0])  # top-level folder = primary tag
    name = rel_path.stem.lower()
    # Heuristic tags based on filename keywords
    for kw in ("setup", "lesson", "adr", "strategy", "learnings",
              "market", "context", "weekly", "session", "security"):
        if kw in name or kw in rel_path.as_posix().lower():
            tags.append(kw)
    # Date-stamped journal entries: tag with year-month
    if parts[0:1] == ("journal",):
        for tok in name.split("-"):
            if tok.isdigit() and len(tok) == 4:
                tags.append(f"y{tok}")
    return sorted(set(tags))


def derive_key(rel_path: Path) -> str:
    # vault/<relative path without extension, slugified>
    no_ext = rel_path.with_suffix("")
    return "vault/" + "/".join(slugify(p) for p in no_ext.parts)


def walk(paths: list[Path], since_ts: float | None) -> list[dict]:
    entries = []
    for base in paths:
        for root, dirs, files in os.walk(base):
            # Mutate dirs in-place to skip excluded
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                fp = Path(root) / fn
                rel = fp.relative_to(PROJECT_ROOT)
                if rel.as_posix() in EXCLUDED_FILES:
                    continue
                try:
                    stat = fp.stat()
                except OSError:
                    continue
                if since_ts is not None and stat.st_mtime < since_ts:
                    continue
                content = fp.read_text(encoding="utf-8", errors="replace")
                entries.append({
                    "path": rel.as_posix(),
                    "key": derive_key(rel),
                    "tags": derive_tags(rel),
                    "mtime": _dt.datetime.fromtimestamp(stat.st_mtime, tz=_dt.timezone.utc).isoformat(),
                    "size_bytes": stat.st_size,
                    "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
                    "content_preview": content[:240].replace("\n", " "),
                    "suggested_value": content,
                })
    return entries


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--since", help="Only index files modified after YYYY-MM-DD")
    p.add_argument("--paths", nargs="*", default=None,
                   help="Restrict to these top-level folders (e.g. memory docs/adr)")
    args = p.parse_args()

    since_ts = None
    if args.since:
        since_ts = _dt.datetime.fromisoformat(args.since).replace(
            tzinfo=_dt.timezone.utc).timestamp()

    if args.paths:
        roots = [PROJECT_ROOT / p for p in args.paths]
        for r in roots:
            if not r.exists():
                print(f"warn: {r} does not exist", file=sys.stderr)
        roots = [r for r in roots if r.exists()]
    else:
        roots = [PROJECT_ROOT]

    entries = walk(roots, since_ts)
    manifest = {
        "namespace": "trading-vault",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "entry_count": len(entries),
        "entries": entries,
    }
    json.dump(manifest, sys.stdout, indent=2, default=str)
    print()


if __name__ == "__main__":
    main()
