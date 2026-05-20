"use client";
import { useState, useEffect } from "react";
import { fetchState, pauseAgent, resumeAgent } from "@/lib/api";

export default function SettingsPage() {
  const [state, setState] = useState<any>(null);
  const [toggling, setToggling] = useState(false);

  const load = async () => {
    try { setState(await fetchState()); } catch {}
  };
  useEffect(() => { load(); }, []);

  const togglePause = async () => {
    setToggling(true);
    const paused = state?.paused ?? false;
    if (paused) await resumeAgent();
    else await pauseAgent();
    await load();
    setToggling(false);
  };

  const paused = state?.paused ?? false;
  const wl = /* state?.watchlist — not included in state yet, use count */ null;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-white">Settings</h1>

      {/* Agent pause/resume */}
      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-white">Swing Agent</div>
            <div className="text-xs text-slate-500 mt-0.5">
              {paused ? "Paused — no new setups will be proposed" : "Active — pre-market routine running"}
            </div>
          </div>
          <button
            onClick={togglePause}
            disabled={toggling}
            className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50
              ${paused
                ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30"
                : "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 border border-yellow-500/30"}`}>
            {toggling ? "…" : paused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>

      {/* Watchlist stats */}
      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <div className="text-sm font-medium text-white mb-1">Watchlist</div>
        <div className="text-2xl font-bold text-emerald-400">{state?.watchlist_count ?? "—"}</div>
        <div className="text-xs text-slate-500">symbols tracked</div>
        <div className="text-xs text-slate-600 mt-2">Edit memory/watchlist.json to add/remove symbols.</div>
      </div>

      {/* Market context */}
      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <div className="text-sm font-medium text-white mb-2">Market Context</div>
        <pre className="text-xs text-slate-400 whitespace-pre-wrap break-words overflow-auto max-h-48">
          {state?.market_context_raw ?? "Loading…"}
        </pre>
      </div>

      {/* API info */}
      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
        <div className="text-sm font-medium text-white mb-2">API</div>
        <div className="text-xs text-slate-500 font-mono">Backend: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</div>
        <div className="text-xs text-slate-500 mt-1">Data: Alpaca Markets (paper)</div>
      </div>
    </div>
  );
}
