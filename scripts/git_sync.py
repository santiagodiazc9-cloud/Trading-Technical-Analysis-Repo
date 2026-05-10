#!/usr/bin/env python3
"""Agent-safe git sync.

Single entrypoint the agent uses to commit/push/pull during routines.
Designed to be conservative: never touches code, never stages secrets,
never force-pushes, never amends.

Subcommands:
  status       Show working tree + ahead/behind vs origin/main.
  pull         Fast-forward pull from origin/main (no merge commits).
  commit MSG   Stage agent-owned paths, run secret scan, commit if dirty.
  push         Push current branch to origin (no force, no skip-hooks).
  sync MSG     pull --ff-only ; commit MSG ; push (idempotent — skips no-ops).
  guard PATH   Run the secret scan against PATH (for ad-hoc checks).

Output is JSON on stdout so routines/parsers can act on it.

Agent-owned paths (the only things this script will ever stage):
  memory/  journal/  docs/  inbox/  templates/  *.md (root docs)

Hard blocks:
  - .env, anything matching common secret patterns -> abort with reason
  - committing on a branch other than main (configurable via --allow-branch)
  - push if HEAD is detached
  - --force, --no-verify, amends — never supported

Usage from agent:
  python3 scripts/git_sync.py status
  python3 scripts/git_sync.py sync "routine(pre_market): 2026-05-11 08:05"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paths the agent is allowed to stage. Everything else is rejected.
AGENT_OWNED_PREFIXES = (
    "memory/",
    "journal/",
    "docs/",
    "inbox/",
    "templates/",
    "Dashboard.md",  # actually gitignored, but allow attempts to be silently dropped
)
# Root markdown docs the agent may update (CLAUDE.md is intentionally excluded —
# only humans edit the rulebook).
AGENT_OWNED_ROOT_MD = {
    "CLOUD_COWORK.md",
    "DISCORD.md",
    "README.md",
    "RUN_ROUTINES.md",
    "SETUP.md",
    "TRADING_GUIDE.md",
    "VAULT.md",
}

# Files we never stage, even if their path is otherwise allowed.
HARD_BLOCKLIST = {
    ".env",
    ".env.local",
    ".env.production",
    "memory/discord_config.json",
    "memory/clickup_config.json",
}

# Heuristic regexes for secret detection. Run against file contents of every
# staged file before committing.
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "Anthropic API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_\-]+"), "Discord webhook URL"),
    (re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"(?i)bot\s*token\s*[:=]\s*['\"]?[A-Za-z0-9._\-]{40,}"), "Discord bot token"),
    (re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----"), "Private key block"),
    # Alpaca paper keys are 20-char alnum prefixed by "PK". Live keys "AK". Either is a secret.
    (re.compile(r"\b(PK|AK)[A-Z0-9]{18}\b"), "Alpaca API key"),
]

ALLOWED_BRANCHES = {"main"}


def run(cmd, check=True, capture=True):
    """Run a subprocess; return (rc, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({' '.join(cmd)}): {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.returncode, result.stdout, result.stderr


def emit(payload):
    print(json.dumps(payload, indent=2))


def current_branch():
    _, out, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip()


def path_is_agent_owned(path: str) -> bool:
    if path in HARD_BLOCKLIST:
        return False
    if path in AGENT_OWNED_ROOT_MD:
        return True
    return any(path.startswith(prefix) for prefix in AGENT_OWNED_PREFIXES)


def scan_for_secrets(paths):
    """Return list of (path, reason) for any file that hits a secret pattern."""
    hits = []
    for rel in paths:
        full = REPO_ROOT / rel
        if not full.is_file():
            continue
        try:
            text = full.read_text(errors="ignore")
        except OSError:
            continue
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append({"path": rel, "reason": label})
                break
    return hits


def _porcelain_paths(porcelain: str):
    """Parse `git status --porcelain` output into a list of paths.

    Format: each line is `XY<space>path` (sometimes `R<space><space>old -> new`).
    Don't strip the whole blob — that eats the leading status space of the first line.
    """
    out = []
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.append(path)
    return out


def cmd_status(_args):
    _, dirty, _ = run(["git", "status", "--porcelain"])
    _, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    rc, _, _ = run(["git", "fetch", "origin", "--quiet"], check=False)
    _, ab, _ = run(
        ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
        check=False,
    )
    behind, ahead = (ab.strip().split() + ["0", "0"])[:2]
    emit(
        {
            "ok": True,
            "branch": branch.strip(),
            "dirty_files": _porcelain_paths(dirty),
            "ahead": int(ahead) if ahead.isdigit() else 0,
            "behind": int(behind) if behind.isdigit() else 0,
            "fetch_ok": rc == 0,
        }
    )


def cmd_pull(_args):
    branch = current_branch()
    if branch not in ALLOWED_BRANCHES:
        emit({"ok": False, "error": f"refusing to pull on branch {branch!r}", "branch": branch})
        return 2
    rc, out, err = run(["git", "pull", "--ff-only", "origin", branch], check=False)
    emit(
        {
            "ok": rc == 0,
            "branch": branch,
            "stdout": out.strip(),
            "stderr": err.strip(),
        }
    )
    return 0 if rc == 0 else 1


def staged_paths():
    _, out, _ = run(["git", "diff", "--cached", "--name-only"])
    return [p for p in out.splitlines() if p]


def cmd_commit(args):
    if not args.message or len(args.message.strip()) < 8:
        emit({"ok": False, "error": "commit message must be >=8 chars"})
        return 2

    branch = current_branch()
    if branch not in ALLOWED_BRANCHES and not args.allow_branch:
        emit({"ok": False, "error": f"refusing to commit on branch {branch!r}", "branch": branch})
        return 2

    # Collect candidate paths: every modified / untracked file at REPO_ROOT.
    _, porcelain, _ = run(["git", "status", "--porcelain"])
    candidates, skipped = [], []
    for path in _porcelain_paths(porcelain):
        (candidates if path_is_agent_owned(path) else skipped).append(path)

    if not candidates:
        emit(
            {
                "ok": True,
                "committed": False,
                "reason": "nothing agent-owned to commit",
                "skipped": skipped,
            }
        )
        return 0

    # Reset index first to avoid accidentally including pre-staged garbage.
    run(["git", "reset", "--quiet"], check=False)
    run(["git", "add", "--"] + candidates)

    staged = staged_paths()
    if not staged:
        emit(
            {
                "ok": True,
                "committed": False,
                "reason": "after staging, nothing in index",
                "skipped": skipped,
            }
        )
        return 0

    secret_hits = scan_for_secrets(staged)
    if secret_hits:
        run(["git", "reset", "--quiet"], check=False)
        emit(
            {
                "ok": False,
                "committed": False,
                "error": "secret scan blocked commit — see leaks",
                "leaks": secret_hits,
            }
        )
        return 3

    rc, out, err = run(["git", "commit", "-m", args.message], check=False)
    if rc != 0:
        emit({"ok": False, "committed": False, "stdout": out.strip(), "stderr": err.strip()})
        return 1

    _, sha, _ = run(["git", "rev-parse", "HEAD"])
    emit(
        {
            "ok": True,
            "committed": True,
            "sha": sha.strip(),
            "message": args.message,
            "files": staged,
            "skipped": skipped,
        }
    )
    return 0


def cmd_push(_args):
    branch = current_branch()
    if branch in {"HEAD", ""}:
        emit({"ok": False, "error": "detached HEAD — refusing to push"})
        return 2
    rc, out, err = run(["git", "push", "origin", branch], check=False)
    emit(
        {
            "ok": rc == 0,
            "branch": branch,
            "stdout": out.strip(),
            "stderr": err.strip(),
        }
    )
    return 0 if rc == 0 else 1


def cmd_sync(args):
    """pull --ff-only ; commit ; push. Errors short-circuit but never raise."""
    summary = {"steps": []}

    # Step 1: pull
    branch = current_branch()
    if branch not in ALLOWED_BRANCHES:
        emit({"ok": False, "error": f"refusing to sync on branch {branch!r}"})
        return 2
    rc, _, err = run(["git", "pull", "--ff-only", "origin", branch], check=False)
    summary["steps"].append({"step": "pull", "ok": rc == 0, "stderr": err.strip()})
    if rc != 0:
        summary["ok"] = False
        summary["error"] = "pull failed — resolve before retry"
        emit(summary)
        return 1

    # Step 2: commit
    commit_rc = cmd_commit_inline(args.message)
    summary["steps"].append({"step": "commit", **commit_rc})
    if not commit_rc["ok"]:
        summary["ok"] = False
        summary["error"] = commit_rc.get("error", "commit failed")
        emit(summary)
        return 1

    if not commit_rc.get("committed"):
        # Nothing to push — but we still attempt push in case there's an
        # earlier local commit that hasn't been pushed.
        pass

    # Step 3: push
    rc, _, err = run(["git", "push", "origin", branch], check=False)
    summary["steps"].append({"step": "push", "ok": rc == 0, "stderr": err.strip()})
    summary["ok"] = rc == 0
    if rc != 0:
        summary["error"] = "push failed"
    emit(summary)
    return 0 if rc == 0 else 1


def cmd_commit_inline(message):
    """Same as cmd_commit but returns a dict instead of printing/exiting.

    Used by sync so we get a structured summary.
    """
    if not message or len(message.strip()) < 8:
        return {"ok": False, "error": "commit message must be >=8 chars"}

    _, porcelain, _ = run(["git", "status", "--porcelain"])
    candidates, skipped = [], []
    for path in _porcelain_paths(porcelain):
        (candidates if path_is_agent_owned(path) else skipped).append(path)

    if not candidates:
        return {"ok": True, "committed": False, "reason": "nothing agent-owned", "skipped": skipped}

    run(["git", "reset", "--quiet"], check=False)
    run(["git", "add", "--"] + candidates)
    staged = staged_paths()
    if not staged:
        return {"ok": True, "committed": False, "reason": "empty index after stage", "skipped": skipped}

    leaks = scan_for_secrets(staged)
    if leaks:
        run(["git", "reset", "--quiet"], check=False)
        return {"ok": False, "committed": False, "error": "secret scan blocked commit", "leaks": leaks}

    rc, out, err = run(["git", "commit", "-m", message], check=False)
    if rc != 0:
        return {"ok": False, "committed": False, "stderr": err.strip(), "stdout": out.strip()}
    _, sha, _ = run(["git", "rev-parse", "HEAD"])
    return {
        "ok": True,
        "committed": True,
        "sha": sha.strip(),
        "files": staged,
        "skipped": skipped,
    }


def cmd_guard(args):
    leaks = scan_for_secrets([args.path])
    emit({"ok": not leaks, "path": args.path, "leaks": leaks})
    return 0 if not leaks else 3


def main():
    parser = argparse.ArgumentParser(description="Agent-safe git sync.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    sub.add_parser("pull")
    p_commit = sub.add_parser("commit")
    p_commit.add_argument("message")
    p_commit.add_argument("--allow-branch", action="store_true")
    sub.add_parser("push")
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("message")
    p_guard = sub.add_parser("guard")
    p_guard.add_argument("path")

    args = parser.parse_args()
    handlers = {
        "status": cmd_status,
        "pull": cmd_pull,
        "commit": cmd_commit,
        "push": cmd_push,
        "sync": cmd_sync,
        "guard": cmd_guard,
    }
    try:
        rc = handlers[args.cmd](args)
    except RuntimeError as exc:
        emit({"ok": False, "error": str(exc)})
        rc = 1
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
