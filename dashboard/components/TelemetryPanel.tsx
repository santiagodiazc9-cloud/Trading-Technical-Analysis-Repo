"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { fetchUsage } from "@/lib/api";

function SensorWidget({ label, value, sub, color = "#00d4ff", index }: {
  label: string; value: string; sub?: string; color?: string; index: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      className="rounded-sm px-3 py-2.5 relative overflow-hidden"
      style={{
        background: "rgba(0,6,20,0.6)",
        border: "1px solid rgba(0,212,255,0.07)",
      }}
    >
      {/* Corner accent */}
      <div className="absolute top-0 right-0 w-4 h-4 hud-corner-tr opacity-30"/>

      <p className="text-[8px] tracking-[0.2em] text-slate-700 mb-1.5">{label}</p>
      <p className="text-xl font-bold leading-none tracking-tight" style={{ color }}>
        {value}
      </p>
      {sub && <p className="text-[8px] text-slate-700 mt-1 tracking-wider">{sub}</p>}

      {/* Active bar */}
      <div className="absolute bottom-0 left-0 right-0 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${color}40, transparent)` }}/>
    </motion.div>
  );
}

interface TelemetryProps { state: any; live: any[]; }

export default function TelemetryPanel({ state, live }: TelemetryProps) {
  const [usage, setUsage] = useState<any>(null);
  useEffect(() => {
    fetchUsage().then(setUsage);
    const id = setInterval(() => fetchUsage().then(setUsage), 60_000);
    return () => clearInterval(id);
  }, []);
  const account  = state?.account ?? {};
  const equity   = parseFloat(account.equity ?? 0);
  const positions: any[] = state?.positions ?? [];
  const unrealized = positions.reduce((s: number, p: any) => s + parseFloat(p.unrealized_pnl ?? 0), 0);
  const tradesWeek = (() => {
    const wc = state?.trade_log?.weekly_trade_count ?? {};
    return Object.values(wc).reduce((s: number, v: any) => s + (typeof v === "number" ? v : 0), 0);
  })();
  const clock   = state?.clock ?? {};
  const isOpen  = clock.is_open ?? false;
  const plColor = unrealized >= 0 ? "#10b981" : "#ef4444";

  const widgets = [
    {
      label: "PROFIT · LOSS",
      value: equity ? `${unrealized >= 0 ? "+" : "-"}$${Math.abs(unrealized).toFixed(2)}` : "—",
      sub: `${positions.length} position${positions.length !== 1 ? "s" : ""} in orbit`,
      color: plColor,
    },
    {
      label: "EQUITY RESERVE",
      value: equity ? `$${equity.toLocaleString("en-US", { maximumFractionDigits: 0 })}` : "—",
      sub: "paper trading account",
      color: "#e2e8f0",
    },
    {
      label: "MISSION SORTIES",
      value: `${tradesWeek} / 3`,
      sub: "weekly trade limit",
      color: tradesWeek >= 3 ? "#ef4444" : tradesWeek >= 2 ? "#f59e0b" : "#10b981",
    },
    {
      label: "ACTIVE AGENTS",
      value: `${live.filter(a => a.status === "active").length}`,
      sub: `of ${live.length} total deployed`,
      color: "#00d4ff",
    },
    {
      label: "TRANSMISSION WINDOW",
      value: isOpen ? "OPEN" : "CLOSED",
      sub: isOpen ? "markets trading" : clock.next_open
        ? `opens ${new Date(clock.next_open).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", timeZone: "America/New_York" })} ET`
        : "awaiting window",
      color: isOpen ? "#10b981" : "#475569",
    },
    {
      label: "FUEL RESERVES",
      value: account.buying_power ? `$${parseFloat(account.buying_power).toLocaleString("en-US", { maximumFractionDigits: 0 })}` : "—",
      sub: "buying power available",
      color: "#64748b",
    },
  ];

  return (
    <aside className="w-[256px] shrink-0 flex flex-col overflow-hidden"
      style={{
        background: "linear-gradient(180deg, rgba(0,8,24,0.95) 0%, rgba(0,4,16,0.98) 100%)",
        borderLeft: "1px solid rgba(0,212,255,0.08)",
      }}>

      {/* Header */}
      <div className="px-4 py-3 border-b border-[rgba(0,212,255,0.07)]">
        <div className="flex items-center gap-2">
          <div className="w-1 h-1 rounded-full bg-[#a855f7] animate-ping opacity-70"/>
          <p className="text-[9px] tracking-[0.3em] text-[#a855f7] opacity-70 flicker">
            SENSOR ARRAY
          </p>
        </div>
        <p className="text-[8px] text-slate-800 mt-0.5 tracking-widest">
          REAL-TIME TELEMETRY
        </p>
      </div>

      {/* Widgets */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
        {widgets.map((w, i) => (
          <SensorWidget key={w.label} {...w} index={i}/>
        ))}
      </div>

      {/* Compute budget */}
      {usage && (
        <div className="px-3 py-3 mx-3 mb-2 rounded-sm"
          style={{ background: "rgba(0,6,20,0.6)", border: "1px solid rgba(168,85,247,0.1)" }}>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1 h-1 rounded-full bg-[#a855f7] animate-ping opacity-60"/>
            <p className="text-[8px] tracking-[0.2em] text-[#a855f7] opacity-60">COMPUTE BUDGET</p>
          </div>
          <div className="space-y-1.5">
            {[
              { label: "TODAY",     value: `$${(usage.today_cost_usd ?? 0).toFixed(3)}`, color: "#e2e8f0" },
              { label: "THIS WEEK", value: `$${(usage.week_cost_usd ?? 0).toFixed(2)}`,  color: "#94a3b8" },
              { label: "ALL TIME",  value: `$${(usage.totals?.cost_usd ?? 0).toFixed(2)}`, color: "#475569" },
              { label: "RUNS",      value: `${usage.totals?.run_count ?? 0}`, color: "#475569" },
            ].map(row => (
              <div key={row.label} className="flex justify-between items-center">
                <span className="text-[8px] tracking-widest text-slate-700">{row.label}</span>
                <span className="text-[10px] font-bold tabular-nums" style={{ color: row.color }}>
                  {row.value}
                </span>
              </div>
            ))}
            {/* Mini bar: today vs weekly */}
            {usage.week_cost_usd > 0 && (
              <div className="mt-1.5">
                <div className="h-0.5 rounded-full bg-slate-900 overflow-hidden">
                  <div className="h-full rounded-full bg-[#a855f7] opacity-60"
                    style={{ width: `${Math.min(100, (usage.today_cost_usd / Math.max(usage.week_cost_usd, 0.01)) * 100)}%` }}/>
                </div>
                <p className="text-[7px] text-slate-800 mt-0.5">today / this week</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* System health footer */}
      <div className="px-4 py-2.5 border-t border-[rgba(0,212,255,0.06)]">
        <p className="text-[8px] tracking-[0.2em] text-[#a855f7] opacity-50 mb-1.5 flicker">
          SYSTEM HEALTH
        </p>
        {[
          { label: "ALPACA API",   status: equity ? "NOMINAL" : "OFFLINE", ok: !!equity },
          { label: "DISCORD RELAY", status: "NOMINAL",  ok: true },
          { label: "GHA FAILSAFE", status: "ARMED",    ok: true },
          { label: "TAVILY INTEL", status: "NOMINAL",  ok: true },
        ].map(row => (
          <div key={row.label} className="flex justify-between items-center py-0.5">
            <span className="text-[8px] tracking-wide text-slate-700">{row.label}</span>
            <div className="flex items-center gap-1.5">
              <div className="w-1 h-1 rounded-full"
                style={{ backgroundColor: row.ok ? "#10b981" : "#ef4444" }}/>
              <span className="text-[8px]" style={{ color: row.ok ? "#10b981" : "#ef4444" }}>
                {row.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
