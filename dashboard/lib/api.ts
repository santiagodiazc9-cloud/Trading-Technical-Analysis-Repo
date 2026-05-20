const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchState() {
  const res = await fetch(`${API_BASE}/state`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch state");
  return res.json();
}

export async function fetchPositions() {
  const res = await fetch(`${API_BASE}/positions`, { cache: "no-store" });
  return res.json();
}

export async function fetchBars(symbol: string, days = 1) {
  const res = await fetch(`${API_BASE}/bars/${symbol}?days=${days}`, { cache: "no-store" });
  return res.json();
}

export async function fetchScores() {
  const res = await fetch(`${API_BASE}/scores`, { cache: "no-store" });
  return res.json();
}

export async function approveSetup(setupId: string) {
  const res = await fetch(`${API_BASE}/approve/${encodeURIComponent(setupId)}`, { method: "POST" });
  return res.json();
}

export async function denySetup(setupId: string, reason = "denied via dashboard") {
  const res = await fetch(`${API_BASE}/deny/${encodeURIComponent(setupId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  return res.json();
}

export async function setSession(approved: boolean, maxTrades = 2, maxLossUsd = 500) {
  const res = await fetch(`${API_BASE}/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved, max_trades: maxTrades, max_loss_usd: maxLossUsd }),
  });
  return res.json();
}

export async function pauseAgent(reason = "paused via dashboard") {
  const res = await fetch(`${API_BASE}/pause`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  return res.json();
}

export async function resumeAgent() {
  const res = await fetch(`${API_BASE}/resume`, { method: "POST" });
  return res.json();
}

export const WS_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000")
  .replace(/^http/, "ws") + "/stream";
