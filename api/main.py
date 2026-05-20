#!/usr/bin/env python3
"""
FastAPI backend for the trading dashboard.

Endpoints:
  GET  /state          — account + positions + pending setups + market context
  GET  /positions      — live Alpaca positions
  GET  /bars/{symbol}  — 5-min bars for chart rendering
  GET  /scores         — latest day trading scores (last poll result)
  POST /session        — approve/revoke the day trading session
  POST /approve/{id}   — approve a swing setup
  POST /deny/{id}      — deny a swing setup
  POST /pause          — pause the agent
  POST /resume         — resume the agent
  WS   /stream         — WebSocket: pushes state updates every 5s

Run:
    uvicorn api.main:app --reload --port 8000
"""

import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Any

import pytz
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from scripts.research import get_bars, compute_indicators

app = FastAPI(title="Trading Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ET = pytz.timezone("America/New_York")

# In-memory cache for day trading scores (updated by /scores endpoint or engine)
_latest_scores: list[dict] = []


# ── file helpers ──────────────────────────────────────────────────────────────

def _read_json(path: str, default: Any = None) -> Any:
    try:
        with open(os.path.join(ROOT, path)) as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, data: Any):
    with open(os.path.join(ROOT, path), "w") as f:
        json.dump(data, f, indent=2)


def _read_text(path: str) -> str:
    try:
        with open(os.path.join(ROOT, path)) as f:
            return f.read()
    except Exception:
        return ""


def _alpaca(cmd: list[str]) -> Any:
    try:
        result = subprocess.run(
            ["python3", os.path.join(ROOT, "scripts", "alpaca_client.py")] + cmd,
            capture_output=True, text=True, timeout=15
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


# ── state assembly ─────────────────────────────────────────────────────────────

def _build_state() -> dict:
    account = _alpaca(["account"])
    positions = _alpaca(["positions"])
    market_ctx = _read_text("memory/market_context.md")
    open_pos_raw = _read_text("memory/open_positions.md")
    trade_log = _read_json("memory/trade_log.json", {})
    session = _read_json("memory/daytrader_session.json",
                         {"session_approved": False, "max_trades": 2, "trades_taken": 0})
    pause_state = _read_json("memory/pause_state.json", {"paused": False})
    watchlist = _read_json("memory/watchlist.json", {"watchlist": []})

    # Parse pending setups from open_positions.md
    pending_setups = _parse_pending_setups(open_pos_raw)

    # Market posture from market_context.md
    posture = "UNKNOWN"
    for line in market_ctx.splitlines():
        if line.strip().startswith("🟢"):
            posture = "GREEN"
        elif line.strip().startswith("🟡"):
            posture = "CAUTION"
        elif line.strip().startswith("🔴"):
            posture = "RED"
        elif line.strip().startswith("⚫"):
            posture = "BEAR"

    return {
        "timestamp": datetime.now(ET).isoformat(),
        "account": account,
        "positions": positions if isinstance(positions, list) else [],
        "pending_setups": pending_setups,
        "market_posture": posture,
        "market_context_raw": market_ctx,
        "day_trading_session": session,
        "paused": pause_state.get("paused", False),
        "day_scores": _latest_scores,
        "watchlist_count": len(watchlist.get("watchlist", [])),
        "trade_log_summary": {
            "total_trades": len(trade_log.get("trades", [])),
            "open_trades": len([t for t in trade_log.get("trades", []) if t.get("status") == "open"]),
        },
    }


def _parse_pending_setups(raw: str) -> list[dict]:
    """
    Extract structured pending setup data from open_positions.md.
    Looks for setup-data:json blocks (machine-readable mirror).
    """
    setups = []
    blocks = re.findall(
        r'<!--\s*setup-data:json\s*(\{.*?\})\s*-->',
        raw, re.DOTALL
    )
    for block in blocks:
        try:
            data = json.loads(block)
            # Find approval status in surrounding text
            setup_id = data.get("setup_id", "")
            approved_match = re.search(
                rf'{re.escape(setup_id)}.*?Approved:\s*(YES|NO)',
                raw, re.DOTALL | re.IGNORECASE
            )
            data["approved"] = approved_match.group(1).upper() if approved_match else "PENDING"
            setups.append(data)
        except Exception:
            pass
    return setups


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/state")
def get_state():
    return JSONResponse(_build_state())


@app.get("/positions")
def get_positions():
    return JSONResponse(_alpaca(["positions"]))


@app.get("/bars/{symbol}")
def get_bars_endpoint(symbol: str, days: int = 2, timeframe: str = "5Min"):
    try:
        df = get_bars(symbol.upper(), timeframe, days_back=days)
        df = compute_indicators(df)
        df["datetime"] = df["datetime"].astype(str)
        import math
        cols = ["datetime", "open", "high", "low", "close", "volume",
                "vwap", "ema_9", "ema_21", "rsi_14", "macd_histogram"]
        cols = [c for c in cols if c in df.columns]
        raw_records = df[cols].tail(100).to_dict(orient="records")
        records = [
            {k: (None if isinstance(v, float) and math.isnan(v) else v)
             for k, v in row.items()}
            for row in raw_records
        ]
        return JSONResponse({"symbol": symbol.upper(), "bars": records})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/scores")
def get_scores():
    return JSONResponse({"scores": _latest_scores,
                         "updated_at": datetime.now(ET).isoformat()})


@app.post("/session")
async def set_session(body: dict):
    """Body: {"approved": true/false, "max_trades": 2, "max_loss_usd": 500}"""
    session = _read_json("memory/daytrader_session.json",
                         {"session_approved": False, "max_trades": 2,
                          "max_loss_usd": 500, "trades_taken": 0, "loss_usd": 0.0})
    session["session_approved"] = bool(body.get("approved", False))
    if "max_trades" in body:
        session["max_trades"] = int(body["max_trades"])
    if "max_loss_usd" in body:
        session["max_loss_usd"] = float(body["max_loss_usd"])
    _write_json("memory/daytrader_session.json", session)
    return {"ok": True, "session": session}


@app.post("/approve/{setup_id}")
async def approve_setup(setup_id: str):
    raw = _read_text("memory/open_positions.md")
    if f"Approved: YES" in raw and setup_id in raw:
        return {"ok": True, "already_approved": True}
    # Insert "Approved: YES" after the setup heading
    pattern = rf'(##\s+{re.escape(setup_id)}[^\n]*\n)'
    new_raw = re.sub(pattern, r'\1Approved: YES\n', raw, count=1)
    if new_raw == raw:
        # Fallback: append after setup_id occurrence
        new_raw = raw.replace(setup_id, f"{setup_id}\nApproved: YES", 1)
    with open(os.path.join(ROOT, "memory", "open_positions.md"), "w") as f:
        f.write(new_raw)
    return {"ok": True, "setup_id": setup_id}


@app.post("/deny/{setup_id}")
async def deny_setup(setup_id: str, body: dict = {}):
    reason = body.get("reason", "denied via dashboard")
    raw = _read_text("memory/open_positions.md")
    pattern = rf'(##\s+{re.escape(setup_id)}[^\n]*\n)'
    new_raw = re.sub(pattern, rf'\1Approved: NO — {reason}\n', raw, count=1)
    with open(os.path.join(ROOT, "memory", "open_positions.md"), "w") as f:
        f.write(new_raw)
    return {"ok": True, "setup_id": setup_id}


@app.post("/pause")
async def pause_agent(body: dict = {}):
    reason = body.get("reason", "paused via dashboard")
    _write_json("memory/pause_state.json",
                {"paused": True, "reason": reason,
                 "paused_at": datetime.now(ET).isoformat()})
    return {"ok": True, "paused": True}


@app.post("/resume")
async def resume_agent():
    _write_json("memory/pause_state.json", {"paused": False})
    return {"ok": True, "paused": False}


# ── WebSocket ────────────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


@app.websocket("/stream")
async def websocket_stream(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            state = _build_state()
            await ws.send_json(state)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/health")
def health():
    return {"ok": True, "time_et": datetime.now(ET).isoformat()}
