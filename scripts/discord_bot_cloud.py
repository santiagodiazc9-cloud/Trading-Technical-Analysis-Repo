#!/usr/bin/env python3
"""
Cloud entrypoint for discord_bot.py.

Runs on Railway / Fly.io / Render where there is no local .env or
local discord_config.json. Reads both from environment variables:

  DISCORD_BOT_TOKEN       — required
  DISCORD_CONFIG_JSON     — required (full JSON string)
  GH_TOKEN                — required for git push (repo write access)
  GH_REPO_OWNER           — required (e.g. "nicholasward")
  GH_REPO_NAME            — required (e.g. "Trading-Technical-Analysis-Repo")

Before starting the bot, this script:
  1. Writes DISCORD_CONFIG_JSON to memory/discord_config.json
  2. Configures git credentials so git_sync.py can push

Then hands off to discord_bot.main().
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "memory"
CONFIG_PATH = MEMORY / "discord_config.json"


def _require(var: str) -> str:
    val = os.environ.get(var, "").strip()
    if not val:
        print(f"[cloud] ERROR: required env var {var!r} is not set", file=sys.stderr)
        sys.exit(1)
    return val


def setup_discord_config() -> None:
    raw = _require("DISCORD_CONFIG_JSON")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"[cloud] ERROR: DISCORD_CONFIG_JSON is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    MEMORY.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(parsed, indent=2))
    print("[cloud] discord_config.json written from env var")


def setup_git_credentials() -> None:
    token = _require("GH_TOKEN")
    owner = _require("GH_REPO_OWNER")
    repo = _require("GH_REPO_NAME")

    # Configure git identity (required to commit)
    subprocess.run(
        ["git", "config", "user.email", "trading-bot@railway.local"],
        cwd=ROOT, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "trading-bot"],
        cwd=ROOT, check=True,
    )

    # Set remote URL with token embedded so push works without interactive auth
    remote_url = f"https://{token}@github.com/{owner}/{repo}.git"
    subprocess.run(
        ["git", "remote", "set-url", "origin", remote_url],
        cwd=ROOT, check=True,
    )
    print("[cloud] git credentials configured")


def main() -> None:
    setup_discord_config()
    setup_git_credentials()

    # Write a minimal .env so discord_bot.py's load_dotenv() finds the token
    env_path = ROOT / ".env"
    token = _require("DISCORD_BOT_TOKEN")
    env_path.write_text(f"DISCORD_BOT_TOKEN={token}\n")

    # Hand off to the real bot
    from discord_bot import main as bot_main
    bot_main()


if __name__ == "__main__":
    main()
