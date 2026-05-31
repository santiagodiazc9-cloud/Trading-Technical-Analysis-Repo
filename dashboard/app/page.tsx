"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AGENTS } from "@/lib/agents";
import type { AgentStatus } from "@/lib/agents";
import { fetchState, fetchAgents } from "@/lib/api";
import AgentSidebar from "@/components/AgentSidebar";
import NetworkCanvas from "@/components/NetworkCanvas";
import TelemetryPanel from "@/components/TelemetryPanel";
import ActivityFeed from "@/components/ActivityFeed";
import CommandDrawer from "@/components/CommandDrawer";
import TickerTape from "@/components/TickerTape";
import AlertBanner from "@/components/AlertBanner";
import ClockWidget from "@/components/ClockWidget";
import type { WarpEvent } from "@/components/NetworkCanvas";

function MET() {
  const [elapsed, setElapsed] = useState("T+00:00:00");
  useEffect(() => {
    const start = Date.now();
    const id = setInterval(() => {
      const s = Math.floor((Date.now() - start) / 1000);
      const h = String(Math.floor(s / 3600)).padStart(2, "0");
      const m = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
      const sc = String(s % 60).padStart(2, "0");
      setElapsed(`T+${h}:${m}:${sc}`);
    }, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="tabular-nums">{elapsed}</span>;
}

export default function FleetPage() {
  const [state, setState] = useState<any>(null);
  const [liveAgents, setLiveAgents] = useState<any[]>([]);
  const [online, setOnline] = useState(true);
  const [booted, setBooted] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [warpEvent, setWarpEvent] = useState<WarpEvent | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [s, agents] = await Promise.all([fetchState(), fetchAgents()]);
      setState(s);
      setLiveAgents(agents);
      setOnline(true);
    } catch {
      setOnline(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 30_000);
    setTimeout(() => setBooted(true), 200);
    return () => clearInterval(id);
  }, [refresh]);

  const liveMap = Object.fromEntries(liveAgents.map((a: any) => [a.id, a]));

  const positions: any[] = state?.positions ?? [];
  const unrealized = positions.reduce((s: number, p: any) => s + parseFloat(p.unrealized_pnl ?? 0), 0);
  const plColor = unrealized >= 0 ? "#10b981" : "#ef4444";
  const plStr = positions.length > 0
    ? `${unrealized >= 0 ? "+" : "-"}$${Math.abs(unrealized).toFixed(2)}`
    : "$0.00";

  const activeCount  = liveAgents.filter((a: any) => a.status === "active").length;
  const offlineCount = AGENTS.length - activeCount;

  // Alert detection: positions approaching -7% cut rule
  const equity = parseFloat(state?.account?.equity ?? 0);
  const criticalAlerts = positions
    .filter((p: any) => {
      const pct = parseFloat(p.unrealized_pnl_pct ?? 0);
      return pct <= -5; // warn at -5%, cut at -7%
    })
    .map((p: any) => ({
      symbol: p.symbol,
      pct: parseFloat(p.unrealized_pnl_pct ?? 0),
      currentPrice: parseFloat(p.current_price ?? 0),
      stopPrice: parseFloat(p.avg_entry ?? 0) * 0.93,
    }));
  const isAlertMode = criticalAlerts.length > 0;

  return (
    <motion.div
      className={`flex flex-col h-screen overflow-hidden${isAlertMode ? " alert-strobe" : ""}`}
      style={{ background: "#000510" }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      {/* ── MISSION CONTROL HEADER ──────────────────────────── */}
      <header className="shrink-0 h-12 relative overflow-hidden"
        style={{
          background: "linear-gradient(180deg, rgba(0,10,28,0.98) 0%, rgba(0,6,18,0.96) 100%)",
          borderBottom: "1px solid rgba(0,212,255,0.1)",
          boxShadow: "0 1px 0 rgba(0,212,255,0.04), 0 4px 20px rgba(0,0,0,0.6)",
        }}>

        {/* Scan line on header bottom */}
        <div className="absolute bottom-0 left-0 right-0 h-px"
          style={{ background: "linear-gradient(90deg, transparent, #00d4ff40, transparent)" }}/>

        <div className="relative h-full flex items-center px-5 gap-5">
          {/* Left: logo + title */}
          <div className="flex items-center gap-3 shrink-0">
            <motion.div
              className="relative flex items-center justify-center w-7 h-7"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <svg width="28" height="28" viewBox="0 0 28 28">
                <circle cx="14" cy="14" r="12" fill="none" stroke="#00d4ff" strokeWidth="0.8" opacity="0.4"
                  strokeDasharray="4 3"/>
                <circle cx="14" cy="14" r="7" fill="none" stroke="#00d4ff" strokeWidth="1.2" opacity="0.7"/>
                <circle cx="14" cy="14" r="3" fill="#00d4ff" opacity="0.9"/>
              </svg>
            </motion.div>

            <div>
              <h1
                className="text-[11px] font-bold tracking-[0.4em] neon-cyan glitch"
                data-text="MISSION CONTROL"
              >
                MISSION CONTROL
              </h1>
              <p className="text-[8px] tracking-[0.25em] text-slate-700 -mt-0.5">
                AUTONOMOUS AGENT FLEET · SECTOR ALPHA
              </p>
            </div>
          </div>

          {/* Divider */}
          <div className="w-px h-6 bg-[rgba(0,212,255,0.12)]"/>

          {/* Status counts */}
          <div className="flex items-center gap-4 text-[9px] tracking-widest">
            <AnimatePresence>
              {activeCount > 0 && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping opacity-70"/>
                  <span className="text-emerald-400">{activeCount} ACTIVE</span>
                </motion.div>
              )}
            </AnimatePresence>
            <div className="flex items-center gap-1.5 text-slate-700">
              <span className="w-1.5 h-1.5 rounded-full border border-slate-700"/>
              <span>{offlineCount} STAGED</span>
            </div>
          </div>

          <div className="w-px h-6 bg-[rgba(0,212,255,0.08)]"/>

          {/* P&L */}
          <div className="flex items-center gap-2 text-[9px]">
            <span className="text-slate-700 tracking-widest">NET P&amp;L</span>
            <motion.span
              key={plStr}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-base font-bold tabular-nums"
              style={{ color: plColor, textShadow: `0 0 10px ${plColor}80` }}
            >
              {plStr}
            </motion.span>
          </div>

          {/* Spacer */}
          <div className="flex-1"/>

          {/* MET — Mission Elapsed Time */}
          <div className="text-[9px] tracking-widest text-slate-700">
            MET <span className="text-[#00d4ff] opacity-60"><MET /></span>
          </div>

          <div className="w-px h-6 bg-[rgba(0,212,255,0.08)]"/>

          {/* Online / clock */}
          <div className="flex items-center gap-3 text-[9px]">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: online ? "#10b981" : "#ef4444",
                  boxShadow: online ? "0 0 6px #10b981" : "0 0 6px #ef4444" }}/>
              <span className="text-slate-600 tracking-wider">{online ? "UPLINK" : "NO SIGNAL"}</span>
            </div>
            <div className="text-slate-600">
              <ClockWidget />
            </div>
          </div>
        </div>
      </header>

      {/* ── ALERT BANNER ────────────────────────────────────── */}
      <AlertBanner alerts={criticalAlerts} />

      {/* ── TICKER TAPE ─────────────────────────────────────── */}
      <TickerTape />

      {/* ── 3-COLUMN BODY ───────────────────────────────────── */}
      <AnimatePresence>
        {booted && (
          <motion.div className="flex flex-1 overflow-hidden relative"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}>
            <AgentSidebar agents={AGENTS} liveMap={liveMap} onSelectAgent={setSelectedId} />
            <NetworkCanvas
              agents={AGENTS}
              liveMap={liveMap}
              onSelectAgent={setSelectedId}
              warpEvent={warpEvent}
              alertSymbols={criticalAlerts.map(a => a.symbol)}
            />
            <TelemetryPanel state={state} live={liveAgents} />

            {/* Command drawer overlay */}
            <AnimatePresence>
              {selectedId && (() => {
                const agent = AGENTS.find(a => a.id === selectedId);
                if (!agent) return null;
                return (
                  <CommandDrawer
                    agent={agent}
                    live={liveMap[selectedId]}
                    state={state}
                    onClose={() => setSelectedId(null)}
                    onRoutineLaunched={(agentId, routinePath) => {
                      setWarpEvent({ agentId, routinePath });
                      setTimeout(() => setWarpEvent(null), 1000);
                    }}
                  />
                );
              })()}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── COMMS LOG ───────────────────────────────────────── */}
      <ActivityFeed />
    </motion.div>
  );
}
