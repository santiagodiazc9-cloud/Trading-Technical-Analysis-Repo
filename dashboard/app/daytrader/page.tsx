"use client";
import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { fetchState, fetchBars, setSession } from "@/lib/api";

const CandleChart = dynamic(() => import("@/components/CandleChart"), { ssr: false });

const DAY_SYMBOLS = ["NVDA", "TSLA", "AMD", "SPY", "QQQ", "PLTR", "NNE", "SMR"];

export default function DayTraderPage() {
  const [state, setState] = useState<any>(null);
  const [bars, setBars] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("SPY");
  const [toggling, setToggling] = useState(false);

  const loadState = async () => {
    try { setState(await fetchState()); } catch {}
  };

  const loadBars = async (sym: string) => {
    try {
      const data = await fetchBars(sym, 2);
      setBars(data.bars ?? []);
    } catch {}
  };

  useEffect(() => {
    loadState();
    loadBars(selectedSymbol);
    const iv = setInterval(() => { loadState(); loadBars(selectedSymbol); }, 30_000);
    return () => clearInterval(iv);
  }, [selectedSymbol]);

  const session = state?.day_trading_session ?? {};
  const approved = session.session_approved ?? false;

  const toggleSession = async () => {
    setToggling(true);
    await setSession(!approved, session.max_trades ?? 2, session.max_loss_usd ?? 500);
    await loadState();
    setToggling(false);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Day Trader</h1>
        <button
          onClick={toggleSession}
          disabled={toggling}
          className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50
            ${approved
              ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30"
              : "bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700"}`}>
          {toggling ? "…" : approved ? "⚡ Session ON" : "○ Session OFF"}
        </button>
      </div>

      {approved && (
        <div className="grid grid-cols-3 gap-2 text-xs">
          <StatBadge label="Trades" value={`${session.trades_taken ?? 0} / ${session.max_trades ?? 2}`} />
          <StatBadge label="Max Loss" value={`$${session.max_loss_usd ?? 500}`} />
          <StatBadge label="Loss So Far" value={`$${(session.loss_usd ?? 0).toFixed(0)}`}
            color={(session.loss_usd ?? 0) > 0 ? "text-red-400" : "text-slate-300"} />
        </div>
      )}

      {/* Symbol picker */}
      <div className="flex flex-wrap gap-2">
        {DAY_SYMBOLS.map((sym) => (
          <button key={sym} onClick={() => setSelectedSymbol(sym)}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors
              ${selectedSymbol === sym
                ? "bg-blue-500 text-white"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"}`}>
            {sym}
          </button>
        ))}
      </div>

      {/* Chart */}
      {bars.length > 0
        ? <CandleChart bars={bars} symbol={selectedSymbol} />
        : <div className="h-64 bg-slate-900 rounded-lg border border-slate-800 flex items-center justify-center text-slate-500 text-sm">Loading chart…</div>}

      {/* Scores */}
      <ScoreTable scores={state?.day_scores ?? []} />

      <p className="text-xs text-slate-600 text-center">
        Chart + scores auto-refresh every 30s · Models retrain weekly via train_all.py
      </p>
    </div>
  );
}

function ScoreTable({ scores }: { scores: any[] }) {
  if (!scores.length) {
    return (
      <div className="bg-slate-900 rounded-lg p-4 border border-slate-800 text-center text-slate-500 text-sm">
        No scores yet — run <code className="text-slate-400">engine.py --dry-run</code> to populate
      </div>
    );
  }

  return (
    <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
      <div className="grid grid-cols-5 text-xs text-slate-500 px-3 py-2 border-b border-slate-800">
        <span>Symbol</span><span>Direction</span><span>Score</span><span>ML</span><span>Patterns</span>
      </div>
      {scores.map((s: any) => {
        const dir = s.direction ?? "NEUTRAL";
        const color = dir === "LONG" ? "text-emerald-400" : dir === "SHORT" ? "text-red-400" : "text-slate-500";
        return (
          <div key={s.symbol}
            className="grid grid-cols-5 text-xs px-3 py-2 border-b border-slate-800/50 last:border-0">
            <span className="font-medium text-white">{s.symbol}</span>
            <span className={`font-semibold ${color}`}>{dir}</span>
            <span className={color}>{s.composite != null ? (s.composite >= 0 ? "+" : "") + s.composite.toFixed(3) : "—"}</span>
            <span className="text-slate-400">{s.ml_prob != null ? (s.ml_prob * 100).toFixed(0) + "%" : "—"}</span>
            <span className="text-slate-500 truncate">{(s.pattern_names ?? []).join(", ") || "—"}</span>
          </div>
        );
      })}
    </div>
  );
}

function StatBadge({ label, value, color = "text-slate-300" }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-slate-900 rounded-lg p-2 border border-slate-800 text-center">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-sm font-semibold ${color}`}>{value}</div>
    </div>
  );
}
